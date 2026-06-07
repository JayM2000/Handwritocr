"use client";

import React, { useRef, useState, useCallback, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useAppDispatch } from "@/store/hooks";
import { addSample } from "@/store/slices/samplesSlice";
import { GlassButton } from "@/components/ui/glass-button";
import { Undo2, Trash2, Save, Minus, Plus } from "lucide-react";

interface Point {
  x: number;
  y: number;
}

interface Stroke {
  points: Point[];
  width: number;
}

function DrawingCanvasInner() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const dispatch = useAppDispatch();
  const [isDrawing, setIsDrawing] = useState(false);
  const [brushSize, setBrushSize] = useState(2);
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const currentStrokeRef = useRef<Point[]>([]);
  const animFrameRef = useRef<number>();

  // Resize canvas to match container
  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.scale(dpr, dpr);
    }
  }, []);

  useEffect(() => {
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    return () => window.removeEventListener("resize", resizeCanvas);
  }, [resizeCanvas]);

  // Redraw all strokes
  const redraw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

    const allStrokes = [...strokes];
    if (currentStrokeRef.current.length > 0) {
      allStrokes.push({
        points: currentStrokeRef.current,
        width: brushSize,
      });
    }

    for (const stroke of allStrokes) {
      if (stroke.points.length < 2) continue;
      ctx.beginPath();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
      ctx.lineWidth = stroke.width;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      for (let i = 1; i < stroke.points.length; i++) {
        ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
      }
      ctx.stroke();
    }
  }, [strokes, brushSize]);

  useEffect(() => {
    redraw();
  }, [redraw]);

  const getPos = useCallback(
    (e: React.MouseEvent | React.TouchEvent): Point => {
      const canvas = canvasRef.current;
      if (!canvas) return { x: 0, y: 0 };
      const rect = canvas.getBoundingClientRect();
      if ("touches" in e) {
        return {
          x: e.touches[0].clientX - rect.left,
          y: e.touches[0].clientY - rect.top,
        };
      }
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    },
    []
  );

  const handleStart = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      e.preventDefault();
      setIsDrawing(true);
      const pos = getPos(e);
      currentStrokeRef.current = [pos];
    },
    [getPos]
  );

  const handleMove = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (!isDrawing) return;
      e.preventDefault();
      const pos = getPos(e);
      currentStrokeRef.current.push(pos);

      // Use requestAnimationFrame for smooth drawing
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = requestAnimationFrame(redraw);
    },
    [isDrawing, getPos, redraw]
  );

  const handleEnd = useCallback(() => {
    if (!isDrawing) return;
    setIsDrawing(false);
    if (currentStrokeRef.current.length > 1) {
      setStrokes((prev) => [
        ...prev,
        { points: [...currentStrokeRef.current], width: brushSize },
      ]);
    }
    currentStrokeRef.current = [];
  }, [isDrawing, brushSize]);

  const handleUndo = useCallback(() => {
    setStrokes((prev) => prev.slice(0, -1));
  }, []);

  const handleClear = useCallback(() => {
    setStrokes([]);
    currentStrokeRef.current = [];
  }, []);

  const handleSave = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || strokes.length === 0) return;

    const dataUrl = canvas.toDataURL("image/png");
    dispatch(
      addSample({
        id: `canvas-${Date.now()}`,
        name: `Drawing ${new Date().toLocaleTimeString()}`,
        dataUrl,
        timestamp: Date.now(),
      })
    );

    // Clear after saving
    handleClear();
  }, [strokes, dispatch, handleClear]);

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="space-y-2">
        <h3 className="text-base font-medium text-white/80">
          Or draw a sample
        </h3>
        <p className="text-xs text-white/40">
          Write naturally on the canvas below. Draw a few lines of text for best
          results.
        </p>
      </div>

      {/* Canvas */}
      <div
        ref={containerRef}
        className="relative rounded-2xl overflow-hidden border border-white/[0.08] bg-white/[0.02]"
      >
        <canvas
          ref={canvasRef}
          className="w-full cursor-crosshair touch-none"
          style={{ height: "240px" }}
          onMouseDown={handleStart}
          onMouseMove={handleMove}
          onMouseUp={handleEnd}
          onMouseLeave={handleEnd}
          onTouchStart={handleStart}
          onTouchMove={handleMove}
          onTouchEnd={handleEnd}
        />

        {/* Watermark */}
        {strokes.length === 0 && !isDrawing && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p className="text-sm text-white/15 select-none">
              Start writing here...
            </p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Brush size */}
        <div className="flex items-center gap-2 glass rounded-xl px-3 py-1.5">
          <span className="text-[10px] text-white/40 uppercase tracking-wider">
            Brush
          </span>
          <button
            onClick={() => setBrushSize((s) => Math.max(1, s - 1))}
            className="h-6 w-6 flex items-center justify-center rounded-lg hover:bg-white/[0.08] transition-colors"
          >
            <Minus className="h-3 w-3 text-white/60" />
          </button>
          <span className="text-xs text-white/70 w-4 text-center">
            {brushSize}
          </span>
          <button
            onClick={() => setBrushSize((s) => Math.min(8, s + 1))}
            className="h-6 w-6 flex items-center justify-center rounded-lg hover:bg-white/[0.08] transition-colors"
          >
            <Plus className="h-3 w-3 text-white/60" />
          </button>
        </div>

        <div className="flex-1" />

        <GlassButton
          variant="ghost"
          size="sm"
          icon={<Undo2 className="h-3.5 w-3.5" />}
          onClick={handleUndo}
          disabled={strokes.length === 0}
        >
          Undo
        </GlassButton>

        <GlassButton
          variant="ghost"
          size="sm"
          icon={<Trash2 className="h-3.5 w-3.5" />}
          onClick={handleClear}
          disabled={strokes.length === 0}
        >
          Clear
        </GlassButton>

        <GlassButton
          variant="primary"
          size="sm"
          icon={<Save className="h-3.5 w-3.5" />}
          onClick={handleSave}
          disabled={strokes.length === 0}
        >
          Save as Sample
        </GlassButton>
      </div>
    </div>
  );
}

export const DrawingCanvas = React.memo(DrawingCanvasInner);
