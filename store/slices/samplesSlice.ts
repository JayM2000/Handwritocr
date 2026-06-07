import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";

// ─── Types ─────────────────────────────────────────────
export interface HandwritingSample {
  id: string;
  name: string;
  dataUrl: string;
  timestamp: number;
}

interface SamplesState {
  samples: HandwritingSample[];
  uploadStatus: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

// ─── Async Thunk (mock for Phase 1 — swap to real API in Phase 2) ──
export const uploadSamplesToServer = createAsyncThunk(
  "samples/uploadToServer",
  async (samples: HandwritingSample[], { rejectWithValue }) => {
    try {
      // Phase 1: Simulate upload delay
      await new Promise((resolve) => setTimeout(resolve, 1500));
      // Phase 2: Replace with actual API call
      // const response = await fetch('/api/upload-samples', {
      //   method: 'POST',
      //   body: JSON.stringify({ samples }),
      // });
      return { success: true, count: samples.length };
    } catch (err) {
      return rejectWithValue("Failed to upload samples");
    }
  }
);

// ─── Initial State ─────────────────────────────────────
const initialState: SamplesState = {
  samples: [],
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
      .addCase(uploadSamplesToServer.fulfilled, (state) => {
        state.uploadStatus = "succeeded";
      })
      .addCase(uploadSamplesToServer.rejected, (state, action) => {
        state.uploadStatus = "failed";
        state.error = (action.payload as string) ?? "Upload failed";
      });
  },
});

export const { addSample, removeSample, clearSamples } = samplesSlice.actions;
export default samplesSlice.reducer;
