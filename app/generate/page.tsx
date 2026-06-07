"use client";

import React, { lazy, Suspense, useCallback, useMemo } from "react";
import { cn } from "@/lib/utils";
import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { nextStep, prevStep } from "@/store/slices/uiSlice";
import { uploadSamplesToServer } from "@/store/slices/samplesSlice";
import { AnimatedBackground } from "@/components/ui/animated-background";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { StepIndicator } from "@/components/ui/step-indicator";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassCard } from "@/components/ui/glass-card";
import { ArrowLeft, ArrowRight } from "lucide-react";

// ─── Lazy-loaded step components for code-splitting ────
const SampleUploader = lazy(() =>
  import("@/components/handwriting/sample-uploader").then((m) => ({
    default: m.SampleUploader,
  }))
);
const DrawingCanvas = lazy(() =>
  import("@/components/handwriting/drawing-canvas").then((m) => ({
    default: m.DrawingCanvas,
  }))
);
const TextInput = lazy(() =>
  import("@/components/handwriting/text-input").then((m) => ({
    default: m.TextInput,
  }))
);
const PreviewPanel = lazy(() =>
  import("@/components/handwriting/preview-panel").then((m) => ({
    default: m.PreviewPanel,
  }))
);
const DownloadPanel = lazy(() =>
  import("@/components/handwriting/download-panel").then((m) => ({
    default: m.DownloadPanel,
  }))
);

// ─── Loading skeleton ──────────────────────────────────
function StepSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-6 w-48 rounded-lg bg-white/[0.06]" />
      <div className="h-4 w-72 rounded-lg bg-white/[0.04]" />
      <div className="h-64 rounded-2xl bg-white/[0.03]" />
    </div>
  );
}

// ─── Step titles for navigation ────────────────────────
const STEP_CONFIG = [
  { title: "Upload Samples", canProceed: "samples" as const },
  { title: "Enter Text", canProceed: "text" as const },
  { title: "Preview", canProceed: "generation" as const },
  { title: "Download", canProceed: null },
];

export default function GeneratePage() {
  const dispatch = useAppDispatch();
  const currentStep = useAppSelector((state) => state.ui.currentStep);
  const samples = useAppSelector((state) => state.samples.samples);
  const samplesCount = samples.length;
  const uploadStatus = useAppSelector((state) => state.samples.uploadStatus);
  const sessionId = useAppSelector((state) => state.samples.sessionId);
  const textContent = useAppSelector((state) => state.text.content);
  const generationStatus = useAppSelector(
    (state) => state.generation.generationStatus
  );

  // Determine if the user can proceed to next step
  const canProceed = useMemo(() => {
    switch (currentStep) {
      case 0:
        return samplesCount > 0;
      case 1:
        return textContent.trim().length > 0;
      case 2:
        return generationStatus === "succeeded";
      case 3:
        return false; // Last step
      default:
        return false;
    }
  }, [currentStep, samplesCount, textContent, generationStatus]);

  const handleNext = useCallback(() => {
    if (!canProceed) return;

    // When leaving step 0: upload samples to backend to get sessionId
    if (currentStep === 0 && !sessionId) {
      dispatch(uploadSamplesToServer(samples)).then((result) => {
        if (uploadSamplesToServer.fulfilled.match(result)) {
          dispatch(nextStep());
        }
      });
      return;
    }

    dispatch(nextStep());
  }, [dispatch, canProceed, currentStep, sessionId, samples]);

  const handlePrev = useCallback(() => {
    dispatch(prevStep());
  }, [dispatch]);

  return (
    <AnimatedBackground>
      <Navbar />

      <main className="min-h-screen pt-24 pb-16 px-4">
        <div className="max-w-3xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center animate-fade-in">
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
              Generate Handwriting
            </h1>
            <p className="text-sm text-white/40">
              Follow the steps below to create your handwritten document
            </p>
          </div>

          {/* Step Indicator */}
          <StepIndicator />

          {/* Step Content */}
          <GlassCard hoverable={false} padding="lg" className="min-h-[400px]">
            <Suspense fallback={<StepSkeleton />}>
              <div
                key={currentStep}
                className={cn(
                  "animate-fade-in"
                )}
              >
                {currentStep === 0 && (
                  <div className="space-y-8">
                    <SampleUploader />
                    <div className="border-t border-white/[0.06] pt-6">
                      <DrawingCanvas />
                    </div>
                  </div>
                )}
                {currentStep === 1 && <TextInput />}
                {currentStep === 2 && <PreviewPanel />}
                {currentStep === 3 && <DownloadPanel />}
              </div>
            </Suspense>
          </GlassCard>

          {/* Navigation buttons */}
          <div className="flex items-center justify-between">
            <GlassButton
              variant="secondary"
              size="md"
              icon={<ArrowLeft className="h-4 w-4" />}
              onClick={handlePrev}
              disabled={currentStep === 0}
            >
              Back
            </GlassButton>

            <div className="flex items-center gap-2">
              <span className="text-xs text-white/30">
                Step {currentStep + 1} of 4
              </span>
            </div>

            {currentStep < 3 && (
              <GlassButton
                variant="primary"
                size="md"
                onClick={handleNext}
                disabled={!canProceed || uploadStatus === "loading"}
                isLoading={uploadStatus === "loading"}
              >
                {uploadStatus === "loading"
                  ? "Uploading samples..."
                  : currentStep === 2
                  ? "Continue to Download"
                  : "Next"}
                {uploadStatus !== "loading" && (
                  <ArrowRight className="h-4 w-4 ml-1" />
                )}
              </GlassButton>
            )}

            {currentStep === 3 && <div className="w-[120px]" />}
          </div>
        </div>
      </main>

      <Footer />
    </AnimatedBackground>
  );
}
