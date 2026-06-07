"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  icon?: React.ReactNode;
}

const variantClasses: Record<string, string> = {
  primary:
    "bg-white/[0.08] border-white/[0.15] text-white hover:bg-white/[0.14] hover:border-white/[0.3] hover:shadow-[0_0_24px_4px_rgba(255,255,255,0.07)]",
  secondary:
    "bg-white/[0.04] border-white/[0.08] text-white/80 hover:bg-white/[0.08] hover:border-white/[0.15] hover:text-white",
  ghost:
    "bg-transparent border-transparent text-white/70 hover:bg-white/[0.06] hover:text-white",
  danger:
    "bg-red-500/[0.1] border-red-400/[0.2] text-red-300 hover:bg-red-500/[0.2] hover:border-red-400/[0.3]",
};

const sizeClasses: Record<string, string> = {
  sm: "h-8 px-3 text-xs gap-1.5 rounded-lg",
  md: "h-10 px-5 text-sm gap-2 rounded-xl",
  lg: "h-12 px-7 text-base gap-2.5 rounded-xl",
};

function GlassButtonInner({
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  className,
  children,
  disabled,
  ...props
}: GlassButtonProps) {
  return (
    <button
      className={cn(
        "glass-button relative inline-flex items-center justify-center font-medium",
        "backdrop-blur-xl transition-all duration-300 ease-out",
        "select-none outline-none cursor-pointer",
        "focus-visible:ring-2 focus-visible:ring-white/20 focus-visible:ring-offset-2 focus-visible:ring-offset-black",
        "disabled:opacity-40 disabled:pointer-events-none disabled:cursor-not-allowed",
        "active:scale-[0.98]",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {/* Shimmer overlay */}
      <span
        className="pointer-events-none absolute inset-0 rounded-[inherit] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          background:
            "linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent)",
          backgroundSize: "200% 100%",
          animation: "shimmer 3s ease-in-out infinite",
        }}
      />

      {/* Content */}
      <span className="relative z-10 flex items-center gap-2">
        {isLoading ? (
          <svg
            className="h-4 w-4 animate-spin"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="3"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        ) : icon ? (
          <span className="flex-shrink-0">{icon}</span>
        ) : null}
        {children}
      </span>
    </button>
  );
}

export const GlassButton = React.memo(GlassButtonInner);
