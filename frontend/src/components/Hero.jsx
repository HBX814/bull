import React from "react";
import { ArrowDown, Sparkles } from "lucide-react";

export default function Hero() {
  return (
    <section
      data-testid="hero-section"
      className="relative pt-32 pb-20 md:pt-44 md:pb-32 overflow-hidden grid-bg"
    >
      <div
        className="absolute inset-0 opacity-[0.18] pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle at 50% 30%, rgba(0, 240, 255, 0.15), transparent 70%)",
        }}
      />
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#00F0FF]/40 to-transparent" />

      <div className="relative max-w-6xl mx-auto px-6 lg:px-10 text-center animate-fade-up">
        <div className="inline-flex items-center gap-2 px-3 py-1 border border-white/15 bg-white/[0.02] font-mono text-[0.65rem] uppercase tracking-[0.25em] text-[#00F0FF] mb-8">
          <Sparkles size={11} />
          <span>Geojit-grade template &nbsp;{"\u2022"}&nbsp; Auto-filled</span>
        </div>

        <p className="font-mono text-xs uppercase tracking-[0.3em] text-[#8C9BB0] mb-6">
          Your research is ready before you are
        </p>

        <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl leading-[1.02] tracking-tight text-white max-w-5xl mx-auto">
          Automated Deep Research <br />
          <span className="italic text-[#D4AF37]">on any listed stock.</span>
        </h1>

        <p className="mt-8 max-w-2xl mx-auto text-base md:text-lg text-[#8C9BB0] leading-relaxed font-sans">
          Drop a result update, an investor presentation, or a raw CSV.
          Bull-AI parses the filings, extracts financials, and ships an analyst-grade
          PDF report — in seconds, with zero human prompting.
        </p>

        <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="#generator"
            data-testid="hero-cta-generate"
            className="group inline-flex items-center gap-3 bg-white text-[#050A10] font-semibold px-7 py-3.5 hover:bg-[#00F0FF] transition-colors duration-300"
          >
            Generate a report
            <ArrowDown size={16} className="group-hover:translate-y-1 transition-transform" />
          </a>
          <a
            href="#features"
            data-testid="hero-cta-learn"
            className="inline-flex items-center gap-2 border border-white/20 px-7 py-3.5 hover:bg-white/5 transition-colors duration-300 font-mono text-xs uppercase tracking-[0.2em]"
          >
            How it works
          </a>
        </div>

        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-px bg-white/10 border border-white/10">
          {[
            ["2L+", "Pages parsed"],
            ["30 sec", "Avg generation"],
            ["100%", "Template fidelity"],
            ["3", "Input formats"],
          ].map(([k, v]) => (
            <div key={v} className="bg-[#0A111A] px-6 py-7" data-testid={`hero-stat-${v.split(" ")[0].toLowerCase()}`}>
              <div className="font-serif text-3xl md:text-4xl text-white">{k}</div>
              <div className="mt-2 font-mono text-[0.65rem] uppercase tracking-[0.2em] text-[#8C9BB0]">{v}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
