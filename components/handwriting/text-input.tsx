"use client";

import React, { useCallback, useMemo, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import {
  setText,
  setPaperStyle,
  setFontSize,
  setLineSpacing,
  type PaperStyle,
} from "@/store/slices/textSlice";
import { GlassCard } from "@/components/ui/glass-card";
import { FileText, Minus, Plus } from "lucide-react";

const PAPER_STYLES: { value: PaperStyle; label: string }[] = [
  { value: "lined", label: "Lined" },
  { value: "blank", label: "Blank" },
  { value: "grid", label: "Grid" },
];

function TextInputInner() {
  const dispatch = useAppDispatch();
  const content = useAppSelector((state) => state.text.content);
  const paperStyle = useAppSelector((state) => state.text.paperStyle);
  const fontSize = useAppSelector((state) => state.text.fontSize);
  const lineSpacing = useAppSelector((state) => state.text.lineSpacing);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(null);

  // Debounced text update to Redux
  const handleTextChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const value = e.target.value;
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        dispatch(setText(value));
      }, 300);
    },
    [dispatch]
  );

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const stats = useMemo(() => {
    const words = content.trim()
      ? content.trim().split(/\s+/).length
      : 0;
    const chars = content.length;
    return { words, chars };
  }, [content]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-white">Enter Your Text</h2>
        <p className="text-sm text-white/50">
          Type or paste the text you want converted to handwriting.
        </p>
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          defaultValue={content}
          onChange={handleTextChange}
          placeholder="Start typing your text here..."
          rows={8}
          className={cn(
            "w-full resize-none glass-input rounded-2xl p-5",
            "text-white/90 placeholder:text-white/20",
            "text-sm leading-relaxed",
            "focus:outline-none"
          )}
        />
        {/* Stats bar */}
        <div className="flex items-center justify-between mt-2 px-1">
          <div className="flex items-center gap-3">
            <span className="text-[10px] text-white/30">
              {stats.chars} characters
            </span>
            <span className="text-[10px] text-white/20">•</span>
            <span className="text-[10px] text-white/30">
              {stats.words} words
            </span>
          </div>
          <div className="flex items-center gap-1">
            <FileText className="h-3 w-3 text-white/20" />
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Paper Style */}
        <GlassCard padding="sm" hoverable={false} className="space-y-3">
          <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
            Paper Style
          </p>
          <div className="flex gap-2">
            {PAPER_STYLES.map((style) => (
              <button
                key={style.value}
                onClick={() => dispatch(setPaperStyle(style.value))}
                className={cn(
                  "flex-1 py-1.5 px-2 rounded-lg text-xs font-medium transition-all duration-200",
                  paperStyle === style.value
                    ? "bg-white/[0.12] text-white border border-white/[0.2]"
                    : "text-white/40 hover:text-white/60 hover:bg-white/[0.04]"
                )}
              >
                {style.label}
              </button>
            ))}
          </div>
        </GlassCard>

        {/* Font Size */}
        <GlassCard padding="sm" hoverable={false} className="space-y-3">
          <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
            Font Size
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => dispatch(setFontSize(Math.max(12, fontSize - 1)))}
              className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-white/[0.08] transition-colors"
            >
              <Minus className="h-3 w-3 text-white/60" />
            </button>
            <span className="text-sm text-white/80 w-8 text-center font-mono">
              {fontSize}
            </span>
            <button
              onClick={() => dispatch(setFontSize(Math.min(32, fontSize + 1)))}
              className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-white/[0.08] transition-colors"
            >
              <Plus className="h-3 w-3 text-white/60" />
            </button>
          </div>
        </GlassCard>

        {/* Line Spacing */}
        <GlassCard padding="sm" hoverable={false} className="space-y-3">
          <p className="text-[10px] font-medium text-white/40 uppercase tracking-wider">
            Line Spacing
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() =>
                dispatch(setLineSpacing(Math.max(24, lineSpacing - 2)))
              }
              className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-white/[0.08] transition-colors"
            >
              <Minus className="h-3 w-3 text-white/60" />
            </button>
            <span className="text-sm text-white/80 w-8 text-center font-mono">
              {lineSpacing}
            </span>
            <button
              onClick={() =>
                dispatch(setLineSpacing(Math.min(48, lineSpacing + 2)))
              }
              className="h-7 w-7 flex items-center justify-center rounded-lg hover:bg-white/[0.08] transition-colors"
            >
              <Plus className="h-3 w-3 text-white/60" />
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}

export const TextInput = React.memo(TextInputInner);
