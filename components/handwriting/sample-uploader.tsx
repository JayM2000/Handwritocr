"use client";

import React, { useCallback, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { addSample, removeSample } from "@/store/slices/samplesSlice";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassCard } from "@/components/ui/glass-card";
import { Upload, X, ImagePlus, Trash2 } from "lucide-react";

/**
 * Resize an image client-side to max 800px dimension before storing in Redux.
 * Returns a data URL string.
 */
function resizeImage(file: File, maxSize = 800): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        let { width, height } = img;
        if (width > maxSize || height > maxSize) {
          if (width > height) {
            height = (height / width) * maxSize;
            width = maxSize;
          } else {
            width = (width / height) * maxSize;
            height = maxSize;
          }
        }
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx?.drawImage(img, 0, 0, width, height);
        resolve(canvas.toDataURL("image/jpeg", 0.85));
      };
      img.onerror = reject;
      img.src = e.target?.result as string;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function SampleUploaderInner() {
  const dispatch = useAppDispatch();
  const samples = useAppSelector((state) => state.samples.samples);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFiles = useCallback(
    async (files: FileList | File[]) => {
      const fileArray = Array.from(files).filter((f) =>
        f.type.startsWith("image/")
      );
      for (const file of fileArray) {
        try {
          const dataUrl = await resizeImage(file);
          dispatch(
            addSample({
              id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
              name: file.name,
              dataUrl,
              timestamp: Date.now(),
            })
          );
        } catch {
          console.error("Failed to process file:", file.name);
        }
      }
    },
    [dispatch]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (e.dataTransfer.files.length) {
        processFiles(e.dataTransfer.files);
      }
    },
    [processFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files?.length) {
        processFiles(e.target.files);
      }
      // Reset so same file can be selected again
      e.target.value = "";
    },
    [processFiles]
  );

  const handleRemove = useCallback(
    (id: string) => {
      dispatch(removeSample(id));
    },
    [dispatch]
  );

  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-white">
          Upload Handwriting Samples
        </h2>
        <p className="text-sm text-white/50">
          Upload clear photos of your handwriting. The more samples, the better
          the result.
        </p>
      </div>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          "relative flex flex-col items-center justify-center gap-4 py-12 px-6",
          "rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer",
          isDragOver
            ? "border-white/40 bg-white/[0.06] shadow-[0_0_30px_rgba(255,255,255,0.06)]"
            : "border-white/[0.1] bg-white/[0.02] hover:border-white/[0.2] hover:bg-white/[0.04]"
        )}
        onClick={handleBrowseClick}
      >
        <div
          className={cn(
            "flex h-14 w-14 items-center justify-center rounded-2xl",
            "bg-white/[0.06] border border-white/[0.1]",
            "transition-all duration-300",
            isDragOver && "scale-110 bg-white/[0.1]"
          )}
        >
          <Upload className="h-6 w-6 text-white/60" />
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-white/70">
            {isDragOver ? "Drop your images here" : "Drag & drop images here"}
          </p>
          <p className="text-xs text-white/30 mt-1">
            or click to browse • PNG, JPG, WebP • Max 5MB each
          </p>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>

      {/* Sample previews */}
      {samples.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-white/40 uppercase tracking-wider">
              {samples.length} sample{samples.length > 1 ? "s" : ""} uploaded
            </p>
            {samples.length > 1 && (
              <GlassButton
                variant="ghost"
                size="sm"
                icon={<Trash2 className="h-3 w-3" />}
                onClick={() => {
                  samples.forEach((s) => dispatch(removeSample(s.id)));
                }}
              >
                Clear all
              </GlassButton>
            )}
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            {samples.map((sample) => (
              <GlassCard
                key={sample.id}
                padding="none"
                hoverable
                className="group relative aspect-square overflow-hidden"
              >
                <img
                  src={sample.dataUrl}
                  alt={sample.name}
                  className="h-full w-full object-cover rounded-2xl"
                />
                {/* Remove overlay */}
                <div className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-2xl">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemove(sample.id);
                    }}
                    className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.15] border border-white/[0.2] hover:bg-red-500/30 hover:border-red-400/40 transition-all duration-200"
                  >
                    <X className="h-4 w-4 text-white" />
                  </button>
                </div>
                {/* Name */}
                <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60 to-transparent rounded-b-2xl">
                  <p className="text-[10px] text-white/60 truncate">
                    {sample.name}
                  </p>
                </div>
              </GlassCard>
            ))}

            {/* Add more button */}
            <button
              onClick={handleBrowseClick}
              className={cn(
                "flex flex-col items-center justify-center gap-1 aspect-square",
                "rounded-2xl border-2 border-dashed border-white/[0.08]",
                "bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/[0.15]",
                "transition-all duration-300 cursor-pointer"
              )}
            >
              <ImagePlus className="h-5 w-5 text-white/30" />
              <span className="text-[10px] text-white/30">Add more</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export const SampleUploader = React.memo(SampleUploaderInner);
