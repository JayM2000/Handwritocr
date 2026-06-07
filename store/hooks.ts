import { useDispatch, useSelector } from "react-redux";
import type { RootState, AppDispatch } from "./index";

/** Typed dispatch hook — use this instead of plain `useDispatch` */
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();

/** Typed selector hook — use this instead of plain `useSelector` */
export const useAppSelector = useSelector.withTypes<RootState>();
