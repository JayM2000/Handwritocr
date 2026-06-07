import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ─── Types ─────────────────────────────────────────────
export type PaperStyle = "lined" | "blank" | "grid";

interface TextState {
  content: string;
  paperStyle: PaperStyle;
  fontSize: number;
  lineSpacing: number;
}

// ─── Initial State ─────────────────────────────────────
const initialState: TextState = {
  content: "",
  paperStyle: "lined",
  fontSize: 18,
  lineSpacing: 32,
};

// ─── Slice ─────────────────────────────────────────────
const textSlice = createSlice({
  name: "text",
  initialState,
  reducers: {
    setText(state, action: PayloadAction<string>) {
      state.content = action.payload;
    },
    setPaperStyle(state, action: PayloadAction<PaperStyle>) {
      state.paperStyle = action.payload;
    },
    setFontSize(state, action: PayloadAction<number>) {
      state.fontSize = action.payload;
    },
    setLineSpacing(state, action: PayloadAction<number>) {
      state.lineSpacing = action.payload;
    },
    resetText(state) {
      return initialState;
    },
  },
});

export const { setText, setPaperStyle, setFontSize, setLineSpacing, resetText } =
  textSlice.actions;
export default textSlice.reducer;
