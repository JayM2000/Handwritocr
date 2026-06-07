import { configureStore } from "@reduxjs/toolkit";
import samplesReducer from "./slices/samplesSlice";
import textReducer from "./slices/textSlice";
import generationReducer from "./slices/generationSlice";
import uiReducer from "./slices/uiSlice";

export const store = configureStore({
  reducer: {
    samples: samplesReducer,
    text: textReducer,
    generation: generationReducer,
    ui: uiReducer,
  },
  // Default middleware already includes redux-thunk
  devTools: process.env.NODE_ENV !== "production",
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
