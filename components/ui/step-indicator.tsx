"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { useAppSelector } from "@/store/hooks";
import { Check } from "lucide-react";

const STEPS = [
  { label: "Upload", description: "Handwriting samples" },
  { label: "Text", description: "Enter your text" },
  { label: "Preview", description: "See the result" },
  { label: "Download", description: "Get your PDF" },
];

function StepIndicatorInner() {
  const currentStep = useAppSelector((state) => state.ui.currentStep);

  return (
    <div className="w-full px-4">
      <div className="flex items-center justify-between max-w-2xl mx-auto">
        {STEPS.map((step, index) => {
          const isCompleted = index < currentStep;
          const isActive = index === currentStep;
          const isUpcoming = index > currentStep;

          return (
            <React.Fragment key={step.label}>
              {/* Step circle + label */}
              <div className="flex flex-col items-center gap-2">
                <div
                  className={cn(
                    "relative flex h-10 w-10 items-center justify-center rounded-full",
                    "transition-all duration-500 ease-out",
                    "text-sm font-semibold",
                    isCompleted && [
                      "bg-white/[0.15] border border-white/[0.3] text-white",
                      "shadow-[0_0_16px_2px_rgba(255,255,255,0.08)]",
                    ],
                    isActive && [
                      "bg-white text-black",
                      "shadow-[0_0_24px_4px_rgba(255,255,255,0.15)]",
                      "animate-pulse-glow",
                    ],
                    isUpcoming && [
                      "bg-white/[0.04] border border-white/[0.08] text-white/40",
                    ]
                  )}
                >
                  {isCompleted ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </div>

                {/* Label */}
                <div className="flex flex-col items-center">
                  <span
                    className={cn(
                      "text-xs font-medium transition-colors duration-300",
                      isActive && "text-white",
                      isCompleted && "text-white/70",
                      isUpcoming && "text-white/30"
                    )}
                  >
                    {step.label}
                  </span>
                  <span
                    className={cn(
                      "text-[10px] transition-colors duration-300 hidden sm:block",
                      isActive && "text-white/60",
                      isCompleted && "text-white/40",
                      isUpcoming && "text-white/20"
                    )}
                  >
                    {step.description}
                  </span>
                </div>
              </div>

              {/* Connector line */}
              {index < STEPS.length - 1 && (
                <div className="flex-1 mx-3 mb-8">
                  <div className="h-px w-full relative overflow-hidden rounded-full bg-white/[0.06]">
                    <div
                      className={cn(
                        "absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out",
                        "bg-gradient-to-r from-white/40 to-white/10",
                        index < currentStep ? "w-full" : "w-0"
                      )}
                    />
                  </div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

export const StepIndicator = React.memo(StepIndicatorInner);
