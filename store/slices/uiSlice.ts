import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

// ─── Types ─────────────────────────────────────────────
type WizardStep = 0 | 1 | 2 | 3;

interface UiState {
  currentStep: WizardStep;
  isNavOpen: boolean;
}

// ─── Initial State ─────────────────────────────────────
const initialState: UiState = {
  currentStep: 0,
  isNavOpen: false,
};

// ─── Slice ─────────────────────────────────────────────
const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setStep(state, action: PayloadAction<WizardStep>) {
      state.currentStep = action.payload;
    },
    nextStep(state) {
      if (state.currentStep < 3) {
        state.currentStep = (state.currentStep + 1) as WizardStep;
      }
    },
    prevStep(state) {
      if (state.currentStep > 0) {
        state.currentStep = (state.currentStep - 1) as WizardStep;
      }
    },
    toggleNav(state) {
      state.isNavOpen = !state.isNavOpen;
    },
    closeNav(state) {
      state.isNavOpen = false;
    },
  },
});

export const { setStep, nextStep, prevStep, toggleNav, closeNav } =
  uiSlice.actions;
export default uiSlice.reducer;
