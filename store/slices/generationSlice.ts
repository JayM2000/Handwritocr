import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";

// ─── Constants ─────────────────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

// ─── Types ─────────────────────────────────────────────
interface GenerationState {
  previewDataUrl: string | null;
  generationStatus: "idle" | "generating" | "succeeded" | "failed";
  progress: number;
  progressStep: string;
  taskId: string | null;
  downloadUrl: string | null;
  error: string | null;
}

interface GeneratePayload {
  sessionId: string;
  text: string;
  paperStyle: string;
  fontSize: number;
  lineSpacing: number;
}

// ─── Async Thunk — Real API call + WebSocket progress ──
export const generateHandwriting = createAsyncThunk(
  "generation/generate",
  async (payload: GeneratePayload, { dispatch, rejectWithValue }) => {
    try {
      // POST /api/generate to start the task
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: payload.sessionId,
          text: payload.text,
          paper_style: payload.paperStyle,
          font_size: payload.fontSize,
          line_spacing: payload.lineSpacing,
          export_format: "pdf",
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Generation failed" }));
        return rejectWithValue(err.detail || "Generation failed");
      }

      const data = await res.json();
      const taskId = data.task_id as string;
      dispatch(setTaskId(taskId));

      // If completed synchronously (sync mode fallback)
      if (data.status === "completed") {
        const downloadUrl = `${API_BASE}/api/download/${taskId}`;
        dispatch(setDownloadUrl(downloadUrl));
        return downloadUrl;
      }

      // Otherwise, connect WebSocket for progress
      return await new Promise<string>((resolve, reject) => {
        let ws: WebSocket;
        try {
          ws = new WebSocket(`${WS_BASE}/ws/progress/${taskId}`);
        } catch {
          // WebSocket unavailable — fall back to polling
          return pollForCompletion(taskId, dispatch, resolve, reject);
        }

        const timeout = setTimeout(() => {
          ws.close();
          reject("Generation timed out");
        }, 300000); // 5 min timeout

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            dispatch(setProgress(msg.progress || 0));
            dispatch(setProgressStep(msg.step || ""));

            if (msg.status === "completed") {
              clearTimeout(timeout);
              ws.close();
              const downloadUrl = msg.download_url
                ? `${API_BASE}${msg.download_url}`
                : `${API_BASE}/api/download/${taskId}`;
              dispatch(setDownloadUrl(downloadUrl));
              resolve(downloadUrl);
            } else if (msg.status === "failed") {
              clearTimeout(timeout);
              ws.close();
              reject(msg.error || "Generation failed");
            }
          } catch {
            // Ignore parse errors
          }
        };

        ws.onerror = () => {
          clearTimeout(timeout);
          ws.close();
          // Fall back to polling on WS error
          pollForCompletion(taskId, dispatch, resolve, reject);
        };

        ws.onclose = () => {
          clearTimeout(timeout);
        };
      });
    } catch (err) {
      return rejectWithValue(
        typeof err === "string" ? err : "Failed to connect to server"
      );
    }
  }
);

/** Poll the status endpoint when WebSocket is unavailable */
async function pollForCompletion(
  taskId: string,
  dispatch: ReturnType<typeof createAsyncThunk>["fulfilled"] extends (...args: infer A) => unknown ? never : (...args: unknown[]) => unknown,
  resolve: (url: string) => void,
  reject: (reason: string) => void,
) {
  const maxPolls = 120; // 2 minutes at 1s intervals
  for (let i = 0; i < maxPolls; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    try {
      const res = await fetch(`${API_BASE}/api/generate/${taskId}/status`);
      if (res.ok) {
        const data = await res.json();
        // @ts-expect-error -- dispatch type is complex
        dispatch(setProgress(data.progress || 0));
        // @ts-expect-error -- dispatch type is complex
        dispatch(setProgressStep(data.step || ""));

        if (data.status === "completed") {
          const downloadUrl = data.download_url
            ? `${API_BASE}${data.download_url}`
            : `${API_BASE}/api/download/${taskId}`;
          // @ts-expect-error -- dispatch type is complex
          dispatch(setDownloadUrl(downloadUrl));
          resolve(downloadUrl);
          return;
        } else if (data.status === "failed") {
          reject(data.error || "Generation failed");
          return;
        }
      }
    } catch {
      // Continue polling
    }
  }
  reject("Generation timed out");
}

// ─── Initial State ─────────────────────────────────────
const initialState: GenerationState = {
  previewDataUrl: null,
  generationStatus: "idle",
  progress: 0,
  progressStep: "",
  taskId: null,
  downloadUrl: null,
  error: null,
};

// ─── Slice ─────────────────────────────────────────────
const generationSlice = createSlice({
  name: "generation",
  initialState,
  reducers: {
    setProgress(state, action: PayloadAction<number>) {
      state.progress = action.payload;
    },
    setProgressStep(state, action: PayloadAction<string>) {
      state.progressStep = action.payload;
    },
    setTaskId(state, action: PayloadAction<string>) {
      state.taskId = action.payload;
    },
    setDownloadUrl(state, action: PayloadAction<string>) {
      state.downloadUrl = action.payload;
    },
    resetGeneration(state) {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateHandwriting.pending, (state) => {
        state.generationStatus = "generating";
        state.progress = 0;
        state.progressStep = "Starting...";
        state.error = null;
        state.previewDataUrl = null;
        state.downloadUrl = null;
      })
      .addCase(generateHandwriting.fulfilled, (state, action) => {
        state.generationStatus = "succeeded";
        state.progress = 100;
        state.progressStep = "Complete";
        state.previewDataUrl = action.payload;
      })
      .addCase(generateHandwriting.rejected, (state, action) => {
        state.generationStatus = "failed";
        state.error = (action.payload as string) ?? "Generation failed";
      });
  },
});

export const { setProgress, setProgressStep, setTaskId, setDownloadUrl, resetGeneration } =
  generationSlice.actions;
export default generationSlice.reducer;
