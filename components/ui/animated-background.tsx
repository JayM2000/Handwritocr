import React from "react";

function AnimatedBackgroundInner({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Gradient orbs */}
      <div className="pointer-events-none fixed inset-0 z-0">
        {/* Top-left orb */}
        <div
          className="absolute -top-40 -left-40 h-[500px] w-[500px] rounded-full opacity-[0.03]"
          style={{
            background:
              "radial-gradient(circle, white 0%, transparent 70%)",
            animation: "orb-float-1 20s ease-in-out infinite",
          }}
        />
        {/* Bottom-right orb */}
        <div
          className="absolute -bottom-32 -right-32 h-[600px] w-[600px] rounded-full opacity-[0.025]"
          style={{
            background:
              "radial-gradient(circle, white 0%, transparent 70%)",
            animation: "orb-float-2 25s ease-in-out infinite",
          }}
        />
        {/* Center faint orb */}
        <div
          className="absolute top-1/2 left-1/2 h-[400px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-[0.015]"
          style={{
            background:
              "radial-gradient(circle, white 0%, transparent 60%)",
            animation: "orb-float-1 30s ease-in-out infinite reverse",
          }}
        />

        {/* Subtle grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}

export const AnimatedBackground = React.memo(AnimatedBackgroundInner);
