import React from "react";
import { PenLine } from "lucide-react";

function FooterInner() {
  return (
    <footer className="relative mt-auto border-t border-white/[0.06]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Brand */}
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-white/[0.06] border border-white/[0.08]">
              <PenLine className="h-3 w-3 text-white/60" />
            </div>
            <span className="text-sm font-medium text-white/40">
              HandwritOCR
            </span>
          </div>

          {/* Copyright */}
          <p className="text-xs text-white/25">
            © {new Date().getFullYear()} HandwritOCR. Transform text into handwriting.
          </p>
        </div>
      </div>
    </footer>
  );
}

export const Footer = React.memo(FooterInner);
