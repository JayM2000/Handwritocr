import Link from "next/link";
import { AnimatedBackground } from "@/components/ui/animated-background";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import {
  Upload,
  Sparkles,
  FileDown,
  ArrowRight,
  PenLine,
  Zap,
  Shield,
} from "lucide-react";

export default function Home() {
  return (
    <AnimatedBackground>
      <Navbar />

      {/* ─── Hero Section ─────────────────────────────────── */}
      <section className="relative flex flex-col items-center justify-center min-h-screen px-4 pt-20">
        {/* Decorative glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] rounded-full opacity-[0.04] blur-3xl bg-white pointer-events-none" />

        <div className="max-w-3xl mx-auto text-center space-y-8 animate-fade-in">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-xs font-medium text-white/60">
            <Zap className="h-3 w-3 text-white/50" />
            AI-Powered Handwriting Synthesis
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight leading-[1.1]">
            <span className="gradient-text">Turn Your Handwriting</span>
            <br />
            <span className="text-white">Into Digital Magic</span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-xl mx-auto text-base sm:text-lg text-white/50 leading-relaxed">
            Upload a few samples of your handwriting and we&apos;ll generate
            beautiful, realistic handwritten text — exported as PDFs that look
            like someone physically wrote in a notebook.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href="/generate"
              className="glass-button inline-flex items-center gap-2.5 h-12 px-8 rounded-xl text-sm font-semibold text-white bg-white/[0.1] border border-white/[0.15] hover:bg-white/[0.16] hover:border-white/[0.3] hover:shadow-[0_0_30px_4px_rgba(255,255,255,0.08)] transition-all duration-300"
            >
              Get Started
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="#how-it-works"
              className="inline-flex items-center gap-2 h-12 px-6 rounded-xl text-sm font-medium text-white/50 hover:text-white/80 transition-colors duration-300"
            >
              See how it works
            </a>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-float">
          <div className="w-5 h-8 rounded-full border border-white/[0.15] flex justify-center pt-1.5">
            <div className="w-1 h-2 rounded-full bg-white/30 animate-bounce" />
          </div>
        </div>
      </section>

      {/* ─── Features Section ─────────────────────────────── */}
      <section className="relative py-24 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Section header */}
          <div className="text-center mb-16 animate-fade-in">
            <p className="text-[10px] font-medium text-white/30 uppercase tracking-[0.2em] mb-3">
              Features
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">
              Everything You Need
            </h2>
          </div>

          {/* Feature cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              {
                icon: Upload,
                title: "Upload Samples",
                description:
                  "Upload photos of your handwriting or draw directly in the browser. A few samples is all it takes.",
                delay: "stagger-1",
              },
              {
                icon: Sparkles,
                title: "AI Generation",
                description:
                  "Our ML engine learns your unique style and generates new text that matches your handwriting perfectly.",
                delay: "stagger-2",
              },
              {
                icon: FileDown,
                title: "Export as PDF",
                description:
                  "Download realistic handwritten documents on notebook-lined paper. Multiple paper styles available.",
                delay: "stagger-3",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className={`glass rounded-2xl p-6 group hover:-translate-y-2 hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.06)] transition-all duration-500 animate-slide-up ${feature.delay}`}
              >
                <div className="h-12 w-12 rounded-xl bg-white/[0.06] border border-white/[0.08] flex items-center justify-center mb-5 group-hover:bg-white/[0.1] group-hover:border-white/[0.15] transition-all duration-300">
                  <feature.icon className="h-5 w-5 text-white/60 group-hover:text-white/90 transition-colors duration-300" />
                </div>
                <h3 className="text-base font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-white/40 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ─────────────────────────────────── */}
      <section id="how-it-works" className="relative py-24 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Section header */}
          <div className="text-center mb-16">
            <p className="text-[10px] font-medium text-white/30 uppercase tracking-[0.2em] mb-3">
              Process
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">
              How It Works
            </h2>
          </div>

          {/* Steps */}
          <div className="relative">
            {/* Connecting line */}
            <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-white/[0.15] via-white/[0.08] to-transparent hidden sm:block" />

            <div className="space-y-12">
              {[
                {
                  step: "01",
                  title: "Upload Your Handwriting",
                  description:
                    "Take photos of your handwriting on paper, or use our in-browser drawing canvas to write samples directly.",
                  icon: PenLine,
                },
                {
                  step: "02",
                  title: "Enter Your Text",
                  description:
                    "Type or paste the text you want converted. Choose your paper style, font size, and line spacing.",
                  icon: Sparkles,
                },
                {
                  step: "03",
                  title: "Preview & Generate",
                  description:
                    "Our AI analyzes your handwriting style and generates realistic handwritten text. Preview it in real-time.",
                  icon: Zap,
                },
                {
                  step: "04",
                  title: "Download Your Document",
                  description:
                    "Export as a beautiful PDF with notebook-style paper or as a PNG image. Ready to print or share.",
                  icon: Shield,
                },
              ].map((item, i) => (
                <div
                  key={item.step}
                  className={`flex gap-6 sm:gap-8 items-start animate-slide-up stagger-${i + 1}`}
                >
                  {/* Step number */}
                  <div className="relative z-10 flex-shrink-0">
                    <div className="h-16 w-16 rounded-2xl glass flex items-center justify-center">
                      <span className="text-lg font-bold text-white/40 font-mono">
                        {item.step}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="pt-2">
                    <div className="flex items-center gap-3 mb-2">
                      <item.icon className="h-4 w-4 text-white/40" />
                      <h3 className="text-lg font-semibold text-white">
                        {item.title}
                      </h3>
                    </div>
                    <p className="text-sm text-white/40 leading-relaxed max-w-lg">
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ─── Bottom CTA ───────────────────────────────────── */}
      <section className="relative py-24 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="glass rounded-3xl p-10 sm:p-14 text-center">
            {/* Decorative glow */}
            <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-px bg-gradient-to-r from-transparent via-white/[0.2] to-transparent" />
            </div>

            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
              Ready to Create?
            </h2>
            <p className="text-sm text-white/40 mb-8 max-w-md mx-auto">
              Transform your typed text into beautiful, realistic handwriting in
              just a few clicks.
            </p>
            <Link
              href="/generate"
              className="glass-button inline-flex items-center gap-2.5 h-12 px-8 rounded-xl text-sm font-semibold text-white bg-white/[0.1] border border-white/[0.15] hover:bg-white/[0.16] hover:border-white/[0.3] hover:shadow-[0_0_30px_4px_rgba(255,255,255,0.08)] transition-all duration-300"
            >
              Start Creating
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </AnimatedBackground>
  );
}
