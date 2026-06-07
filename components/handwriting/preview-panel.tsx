"use client";

import React, { useCallback, useMemo } from "react";
import { cn } from "@/lib/utils";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { generateHandwriting, resetGeneration } from "@/store/slices/generationSlice";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassCard } from "@/components/ui/glass-card";
import { Sparkles, RefreshCw, ZoomIn, ZoomOut } from "lucide-react";

function PreviewPanelInner() {
  const dispatch = useAppDispatch();
  const sessionId = useAppSelector((state) => state.samples.sessionId);
  const { content, paperStyle, penType, fontSize, lineSpacing } = useAppSelector(
    (state) => state.text
  );
  const { generationStatus, progress, progressStep, error } = useAppSelector(
    (state) => state.generation
  );
  const [zoom, setZoom] = React.useState(1);
  const [isClientPreview, setIsClientPreview] = React.useState(false);

  const handleGenerate = useCallback(() => {
    if (sessionId) {
      // Backend generation (real handwriting synthesis)
      setIsClientPreview(false);
      dispatch(
        generateHandwriting({
          sessionId,
          text: content,
          paperStyle,
          penType,
          fontSize,
          lineSpacing,
        })
      );
    } else {
      // Client-side preview fallback (font-based)
      setIsClientPreview(true);
      dispatch({
        type: "generation/generateHandwriting/pending",
      });
      // Simulate quick progress
      setTimeout(() => {
        dispatch({
          type: "generation/generateHandwriting/fulfilled",
          payload: "client-preview",
        });
      }, 500);
    }
  }, [dispatch, sessionId, content, paperStyle, penType, fontSize, lineSpacing]);

  // Pen ink colour for client-side preview
  const penColorMap: Record<string, string> = {
    ballpoint: "rgba(15, 15, 80, 0.85)",
    fountain: "rgba(10, 10, 45, 0.88)",
    gel: "rgba(20, 20, 60, 0.9)",
    pencil: "rgba(60, 60, 60, 0.65)",
    felt_tip: "rgba(25, 25, 25, 0.92)",
  };
  const previewInkColor = penColorMap[penType] || penColorMap.ballpoint;

  const handleRegenerate = useCallback(() => {
    dispatch(resetGeneration());
    setTimeout(() => handleGenerate(), 100);
  }, [dispatch, handleGenerate]);

  // Split text into lines based on line spacing
  const textLines = useMemo(() => {
    if (!content) return [];
    return content.split("\n");
  }, [content]);

  const isReady = content.trim().length > 0;
  const isGenerated = generationStatus === "succeeded";
  const isGenerating = generationStatus === "generating";
  const hasFailed = generationStatus === "failed";

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-semibold text-white">Preview</h2>
          <p className="text-sm text-white/50">
            {isGenerated
              ? "Your handwritten text is ready"
              : "Generate a preview of your handwritten text"}
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom((z) => Math.max(0.5, z - 0.1))}
            className="h-8 w-8 flex items-center justify-center rounded-lg glass-button"
          >
            <ZoomOut className="h-3.5 w-3.5 text-white/60" />
          </button>
          <span className="text-xs text-white/40 w-10 text-center font-mono">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom((z) => Math.min(2, z + 0.1))}
            className="h-8 w-8 flex items-center justify-center rounded-lg glass-button"
          >
            <ZoomIn className="h-3.5 w-3.5 text-white/60" />
          </button>
        </div>
      </div>

      {/* Generate button */}
      {!isGenerated && !isGenerating && (
        <div className="space-y-3">
          <div className="flex justify-center">
            <GlassButton
              variant="primary"
              size="lg"
              icon={<Sparkles className="h-4 w-4" />}
              onClick={handleGenerate}
              disabled={!isReady}
            >
              {isReady ? "Generate Preview" : "Enter text first"}
            </GlassButton>
          </div>

          {/* Error message */}
          {hasFailed && error && (
            <div className="text-center">
              <p className="text-xs text-red-400/70 bg-red-400/[0.06] rounded-lg px-3 py-2">
                {error}
              </p>
            </div>
          )}

          {/* Client mode info */}
          {!sessionId && isReady && (
            <p className="text-center text-[10px] text-white/25">
              Client-side preview mode • Upload samples for AI-powered generation
            </p>
          )}
        </div>
      )}

      {/* Progress bar */}
      {isGenerating && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs text-white/50">{progressStep || "Generating handwriting..."}</p>
            <span className="text-xs text-white/40 font-mono">{progress}%</span>
          </div>
          <div className="h-1 w-full rounded-full bg-white/[0.06] overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-white/30 to-white/60 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Preview area */}
      <GlassCard
        hoverable={false}
        padding="none"
        className="overflow-auto"
        style={{ maxHeight: "480px" }}
      >
        <div
          className={cn(
            "min-h-[400px] p-8 transition-transform duration-200 origin-top-left",
            paperStyle === "lined" && "notebook-lines",
            paperStyle === "grid" && "notebook-grid"
          )}
          style={{ transform: `scale(${zoom})` }}
          id="preview-content"
        >
          {isGenerated && textLines.length > 0 ? (
            <div
              className="space-y-0"
              style={{
                fontFamily: "'Caveat', cursive",
                fontSize: `${fontSize}px`,
                lineHeight: `${lineSpacing}px`,
              }}
            >
              {textLines.map((line, i) => (
                <p
                  key={i}
                  style={{
                    color: previewInkColor,
                    // Add natural variation
                    transform: `translateX(${Math.sin(i * 1.3) * 2}px) rotate(${Math.sin(i * 0.7) * 0.3}deg)`,
                    letterSpacing: `${0.5 + Math.sin(i * 2.1) * 0.3}px`,
                  }}
                >
                  {line || "\u00A0"}
                </p>
              ))}
            </div>
          ) : !isGenerating ? (
            <div className="flex flex-col items-center justify-center h-[400px] gap-3">
              <div className="h-12 w-12 rounded-2xl bg-white/[0.04] border border-white/[0.06] flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white/20" />
              </div>
              <p className="text-sm text-white/20">
                Preview will appear here
              </p>
            </div>
          ) : null}
        </div>
      </GlassCard>

      {/* Regenerate button */}
      {isGenerated && (
        <div className="flex justify-center">
          <GlassButton
            variant="secondary"
            size="md"
            icon={<RefreshCw className="h-3.5 w-3.5" />}
            onClick={handleRegenerate}
          >
            Regenerate
          </GlassButton>
        </div>
      )}
    </div>
  );
}

export const PreviewPanel = React.memo(PreviewPanelInner);
