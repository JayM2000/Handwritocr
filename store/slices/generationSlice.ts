import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import type { HandwritingSample } from "./samplesSlice";

// ─── Types ─────────────────────────────────────────────
interface GenerationState {
  previewDataUrl: string | null;
  generationStatus: "idle" | "generating" | "succeeded" | "failed";
  progress: number;
  error: string | null;
}

interface GeneratePayload {
  samples: HandwritingSample[];
  text: string;
  paperStyle: string;
  fontSize: number;
  lineSpacing: number;
}

// ─── Async Thunk (mock for Phase 1) ───────────────────
export const generateHandwriting = createAsyncThunk(
  "generation/generate",
  async (payload: GeneratePayload, { dispatch, rejectWithValue }) => {
    try {
      // Phase 1: Simulate generation with progress updates
      for (let i = 0; i <= 100; i += 10) {
        await new Promise((resolve) => setTimeout(resolve, 200));
        dispatch(setProgress(i));
      }

      // Phase 2: Replace with actual API call
      // const response = await fetch('/api/generate', {
      //   method: 'POST',
      //   body: JSON.stringify(payload),
      // });
      // const data = await response.json();
      // return data.previewDataUrl;

      // Phase 1: Return a mock — the actual rendering happens in PreviewPanel
      return "mock-preview-ready";
    } catch (err) {
      return rejectWithValue("Failed to generate handwriting");
    }
  }
);

// ─── Initial State ─────────────────────────────────────
const initialState: GenerationState = {
  previewDataUrl: null,
  generationStatus: "idle",
  progress: 0,
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
    resetGeneration(state) {
      return initialState;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateHandwriting.pending, (state) => {
        state.generationStatus = "generating";
        state.progress = 0;
        state.error = null;
        state.previewDataUrl = null;
      })
      .addCase(generateHandwriting.fulfilled, (state, action) => {
        state.generationStatus = "succeeded";
        state.progress = 100;
        state.previewDataUrl = action.payload;
      })
      .addCase(generateHandwriting.rejected, (state, action) => {
        state.generationStatus = "failed";
        state.error = (action.payload as string) ?? "Generation failed";
      });
  },
});

export const { setProgress, resetGeneration } = generationSlice.actions;
export default generationSlice.reducer;
