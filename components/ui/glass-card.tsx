"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
  glowOnHover?: boolean;
  padding?: "sm" | "md" | "lg" | "none";
}

const paddingClasses: Record<string, string> = {
  none: "",
  sm: "p-4",
  md: "p-6",
  lg: "p-8",
};

function GlassCardInner({
  hoverable = true,
  glowOnHover = true,
  padding = "md",
  className,
  children,
  ...props
}: GlassCardProps) {
  return (
    <div
      className={cn(
        "glass rounded-2xl",
        paddingClasses[padding],
        hoverable && [
          "transition-all duration-300 ease-out",
          "hover:-translate-y-1",
          glowOnHover &&
            "hover:shadow-[0_0_30px_-5px_rgba(255,255,255,0.06)]",
        ],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export const GlassCard = React.memo(GlassCardInner);
