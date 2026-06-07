import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ─── Types ─────────────────────────────────────────────
export type PaperStyle = "lined" | "blank" | "grid" | "dotted" | "cornell" | "margin_ruled" | "engineering" | "vintage";
export type PenType = "ballpoint" | "fountain" | "gel" | "pencil" | "felt_tip";

interface TextState {
  content: string;
  paperStyle: PaperStyle;
  penType: PenType;
  fontSize: number;
  lineSpacing: number;
}

// ─── Initial State ─────────────────────────────────────
const initialState: TextState = {
  content: "",
  paperStyle: "lined",
  penType: "ballpoint",
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
    setPenType(state, action: PayloadAction<PenType>) {
      state.penType = action.payload;
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

export const { setText, setPaperStyle, setPenType, setFontSize, setLineSpacing, resetText } =
  textSlice.actions;
export default textSlice.reducer;
