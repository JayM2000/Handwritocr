"use client";

import React, { useCallback, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppSelector } from "@/store/hooks";
import { GlassButton } from "@/components/ui/glass-button";
import { GlassCard } from "@/components/ui/glass-card";
import { Download, FileImage, FileText, Check } from "lucide-react";

type ExportFormat = "pdf" | "png";

function DownloadPanelInner() {
  const { content, paperStyle, penType, fontSize, lineSpacing } = useAppSelector(
    (state) => state.text
  );
  const { generationStatus, downloadUrl } = useAppSelector(
    (state) => state.generation
  );
  const [format, setFormat] = useState<ExportFormat>("pdf");
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloaded, setIsDownloaded] = useState(false);

  const handleDownload = useCallback(async () => {
    if (generationStatus !== "succeeded") return;

    setIsDownloading(true);
    setIsDownloaded(false);

    try {
      // ─── Server-side download (preferred) ────────
      if (downloadUrl) {
        const url = downloadUrl.includes("?")
          ? `${downloadUrl}&format=${format}`
          : `${downloadUrl}?format=${format}`;
        const res = await fetch(url);
        if (res.ok) {
          const blob = await res.blob();
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = `handwriting.${format}`;
          link.click();
          URL.revokeObjectURL(link.href);
          setIsDownloaded(true);
          setTimeout(() => setIsDownloaded(false), 3000);
          return;
        }
        // If server download fails, fall back to client-side
      }

      // ─── Client-side fallback ────────────────────
      if (format === "pdf") {
        // Dynamic import for optimization — only load jspdf when needed
        const { jsPDF } = await import("jspdf");
        const doc = new jsPDF({
          orientation: "portrait",
          unit: "mm",
          format: "a4",
        });

        // Set up notebook style background
        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();

        // Light paper background
        doc.setFillColor(252, 252, 250);
        doc.rect(0, 0, pageWidth, pageHeight, "F");

        // Draw lines for lined paper
        if (paperStyle === "lined" || paperStyle === "grid") {
          doc.setDrawColor(220, 220, 220);
          doc.setLineWidth(0.1);
          const lineSpacingMm = lineSpacing * 0.265; // px to mm
          for (let y = 25; y < pageHeight - 15; y += lineSpacingMm) {
            doc.line(15, y, pageWidth - 15, y);
          }
        }

        // Grid vertical lines
        if (paperStyle === "grid") {
          doc.setDrawColor(220, 220, 220);
          doc.setLineWidth(0.1);
          const lineSpacingMm = lineSpacing * 0.265;
          for (let x = 15; x < pageWidth - 15; x += lineSpacingMm) {
            doc.line(x, 25, x, pageHeight - 15);
          }
        }

        // Red margin line for lined paper
        if (paperStyle === "lined") {
          doc.setDrawColor(255, 180, 180);
          doc.setLineWidth(0.3);
          doc.line(25, 10, 25, pageHeight - 10);
        }

        // Write text
        doc.setFont("helvetica", "normal");
        doc.setFontSize(fontSize * 0.75);
        doc.setTextColor(30, 30, 60);

        const lines = content.split("\n");
        const lineSpacingMm = lineSpacing * 0.265;
        let y = 25 + lineSpacingMm;
        const startX = paperStyle === "lined" ? 28 : 18;

        for (const line of lines) {
          if (y > pageHeight - 20) {
            doc.addPage();
            // Redraw background
            doc.setFillColor(252, 252, 250);
            doc.rect(0, 0, pageWidth, pageHeight, "F");

            if (paperStyle === "lined" || paperStyle === "grid") {
              doc.setDrawColor(220, 220, 220);
              doc.setLineWidth(0.1);
              for (
                let ly = 25;
                ly < pageHeight - 15;
                ly += lineSpacingMm
              ) {
                doc.line(15, ly, pageWidth - 15, ly);
              }
            }
            if (paperStyle === "grid") {
              doc.setDrawColor(220, 220, 220);
              doc.setLineWidth(0.1);
              for (
                let lx = 15;
                lx < pageWidth - 15;
                lx += lineSpacingMm
              ) {
                doc.line(lx, 25, lx, pageHeight - 15);
              }
            }
            if (paperStyle === "lined") {
              doc.setDrawColor(255, 180, 180);
              doc.setLineWidth(0.3);
              doc.line(25, 10, 25, pageHeight - 10);
            }

            doc.setFont("helvetica", "normal");
            doc.setFontSize(fontSize * 0.75);
            doc.setTextColor(30, 30, 60);
            y = 25 + lineSpacingMm;
          }

          // Split long lines
          const maxWidth = pageWidth - startX - 15;
          const splitLines = doc.splitTextToSize(line || " ", maxWidth);
          for (const sl of splitLines) {
            doc.text(sl, startX, y);
            y += lineSpacingMm;
          }
        }

        doc.save("handwriting.pdf");
      } else {
        // PNG export from preview
        const previewEl = document.getElementById("preview-content");
        if (previewEl) {
          // Use html2canvas-like approach with canvas
          const canvas = document.createElement("canvas");
          const rect = previewEl.getBoundingClientRect();
          canvas.width = rect.width * 2;
          canvas.height = rect.height * 2;
          const ctx = canvas.getContext("2d");
          if (ctx) {
            ctx.scale(2, 2);
            ctx.fillStyle = "#0a0a0a";
            ctx.fillRect(0, 0, rect.width, rect.height);
            ctx.fillStyle = "rgba(255,255,255,0.8)";
            ctx.font = `${fontSize}px 'Caveat', cursive`;

            const lines = content.split("\n");
            let y = lineSpacing;
            for (const line of lines) {
              ctx.fillText(line, 32, y);
              y += lineSpacing;
            }

            const link = document.createElement("a");
            link.download = "handwriting.png";
            link.href = canvas.toDataURL("image/png");
            link.click();
          }
        }
      }

      setIsDownloaded(true);
      setTimeout(() => setIsDownloaded(false), 3000);
    } catch (err) {
      console.error("Download failed:", err);
    } finally {
      setIsDownloading(false);
    }
  }, [format, content, paperStyle, fontSize, lineSpacing, generationStatus, downloadUrl]);

  const isReady = generationStatus === "succeeded";

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h2 className="text-xl font-semibold text-white">Download</h2>
        <p className="text-sm text-white/50">
          Export your handwritten text as a file.
        </p>
      </div>

      {/* Format selection */}
      <div className="grid grid-cols-2 gap-4">
        <GlassCard
          hoverable
          padding="md"
          className={cn(
            "cursor-pointer text-center transition-all duration-300",
            format === "pdf" &&
              "border-white/[0.25] bg-white/[0.08] shadow-[0_0_20px_rgba(255,255,255,0.04)]"
          )}
          onClick={() => setFormat("pdf")}
        >
          <div className="flex flex-col items-center gap-3">
            <div
              className={cn(
                "h-12 w-12 rounded-xl flex items-center justify-center",
                "transition-all duration-300",
                format === "pdf"
                  ? "bg-white/[0.12] border border-white/[0.2]"
                  : "bg-white/[0.04] border border-white/[0.06]"
              )}
            >
              <FileText
                className={cn(
                  "h-5 w-5 transition-colors duration-300",
                  format === "pdf" ? "text-white" : "text-white/40"
                )}
              />
            </div>
            <div>
              <p
                className={cn(
                  "text-sm font-medium transition-colors duration-300",
                  format === "pdf" ? "text-white" : "text-white/50"
                )}
              >
                PDF
              </p>
              <p className="text-[10px] text-white/30 mt-0.5">
                Notebook-style document
              </p>
            </div>
          </div>
        </GlassCard>

        <GlassCard
          hoverable
          padding="md"
          className={cn(
            "cursor-pointer text-center transition-all duration-300",
            format === "png" &&
              "border-white/[0.25] bg-white/[0.08] shadow-[0_0_20px_rgba(255,255,255,0.04)]"
          )}
          onClick={() => setFormat("png")}
        >
          <div className="flex flex-col items-center gap-3">
            <div
              className={cn(
                "h-12 w-12 rounded-xl flex items-center justify-center",
                "transition-all duration-300",
                format === "png"
                  ? "bg-white/[0.12] border border-white/[0.2]"
                  : "bg-white/[0.04] border border-white/[0.06]"
              )}
            >
              <FileImage
                className={cn(
                  "h-5 w-5 transition-colors duration-300",
                  format === "png" ? "text-white" : "text-white/40"
                )}
              />
            </div>
            <div>
              <p
                className={cn(
                  "text-sm font-medium transition-colors duration-300",
                  format === "png" ? "text-white" : "text-white/50"
                )}
              >
                PNG
              </p>
              <p className="text-[10px] text-white/30 mt-0.5">
                Image export
              </p>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Settings summary */}
      <GlassCard hoverable={false} padding="sm">
        <div className="flex items-center justify-between text-xs">
          <span className="text-white/40">Paper</span>
          <span className="text-white/70 capitalize">{paperStyle.replace("_", " ")}</span>
        </div>
        <div className="flex items-center justify-between text-xs mt-2">
          <span className="text-white/40">Pen Type</span>
          <span className="text-white/70 capitalize">{penType.replace("_", " ")}</span>
        </div>
        <div className="flex items-center justify-between text-xs mt-2">
          <span className="text-white/40">Font Size</span>
          <span className="text-white/70">{fontSize}px</span>
        </div>
        <div className="flex items-center justify-between text-xs mt-2">
          <span className="text-white/40">Line Spacing</span>
          <span className="text-white/70">{lineSpacing}px</span>
        </div>
      </GlassCard>

      {/* Download button */}
      <GlassButton
        variant="primary"
        size="lg"
        className="w-full"
        icon={
          isDownloaded ? (
            <Check className="h-4 w-4" />
          ) : (
            <Download className="h-4 w-4" />
          )
        }
        onClick={handleDownload}
        isLoading={isDownloading}
        disabled={!isReady}
      >
        {isDownloaded
          ? "Downloaded!"
          : isDownloading
          ? "Preparing..."
          : !isReady
          ? "Generate preview first"
          : `Download ${format.toUpperCase()}`}
      </GlassButton>
    </div>
  );
}

export const DownloadPanel = React.memo(DownloadPanelInner);
