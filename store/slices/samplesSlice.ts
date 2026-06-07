import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";

// ─── Constants ─────────────────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ─────────────────────────────────────────────
export interface HandwritingSample {
  id: string;
  name: string;
  dataUrl: string;
  timestamp: number;
}

interface SamplesState {
  samples: HandwritingSample[];
  sessionId: string | null;
  uploadStatus: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

// ─── Async Thunk — Upload samples to Python backend ────
export const uploadSamplesToServer = createAsyncThunk(
  "samples/uploadToServer",
  async (samples: HandwritingSample[], { rejectWithValue }) => {
    try {
      // Convert data URLs to Blobs for multipart upload
      const formData = new FormData();

      for (const sample of samples) {
        const response = await fetch(sample.dataUrl);
        const blob = await response.blob();
        const ext = blob.type.split("/")[1] || "png";
        formData.append("files", blob, `${sample.name || "sample"}.${ext}`);
      }

      const res = await fetch(`${API_BASE}/api/samples/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Upload failed" }));
        return rejectWithValue(err.detail || "Upload failed");
      }

      const data = await res.json();
      return {
        sessionId: data.session_id as string,
        totalSamples: data.total_samples as number,
      };
    } catch (err) {
      return rejectWithValue("Failed to connect to server. Is the backend running?");
    }
  }
);

// ─── Initial State ─────────────────────────────────────
const initialState: SamplesState = {
  samples: [],
  sessionId: null,
  uploadStatus: "idle",
  error: null,
};

// ─── Slice ─────────────────────────────────────────────
const samplesSlice = createSlice({
  name: "samples",
  initialState,
  reducers: {
    addSample(state, action: PayloadAction<HandwritingSample>) {
      state.samples.push(action.payload);
    },
    removeSample(state, action: PayloadAction<string>) {
      state.samples = state.samples.filter((s) => s.id !== action.payload);
    },
    clearSamples(state) {
      state.samples = [];
      state.sessionId = null;
      state.uploadStatus = "idle";
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(uploadSamplesToServer.pending, (state) => {
        state.uploadStatus = "loading";
        state.error = null;
      })
      .addCase(uploadSamplesToServer.fulfilled, (state, action) => {
        state.uploadStatus = "succeeded";
        state.sessionId = action.payload.sessionId;
      })
      .addCase(uploadSamplesToServer.rejected, (state, action) => {
        state.uploadStatus = "failed";
        state.error = (action.payload as string) ?? "Upload failed";
      });
  },
});

export const { addSample, removeSample, clearSamples } = samplesSlice.actions;
export default samplesSlice.reducer;
