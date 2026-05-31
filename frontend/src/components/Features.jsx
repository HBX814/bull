import React from "react";
import { Database, LineChart, FileOutput } from "lucide-react";

const FEATURES = [
  {
    icon: Database,
    overline: "Document Parsing",
    title: "Every filing, parsed.",
    body: "PDF earnings updates, investor presentations, CSV historicals, raw transcripts — Bull-AI pulls structured numbers out of all of them, page by page.",
  },
  {
    icon: LineChart,
    overline: "Valuation Engine",
    title: "Numbers, mapped to charts.",
    body: "Revenue trends, EBITDA bridges, PAT walks, segment breakdowns — auto-charted in the report. No more pasting matplotlib outputs into Word.",
  },
  {
    icon: FileOutput,
    overline: "Output",
    title: "A real PDF. Not a chat.",
    body: "Geojit-style 4-page layout: rating block, narrative, quarterly table, annual P&L, balance sheet, cashflow and ratios. Press a button. Download.",
  },
];

export default function Features() {
  return (
    <section id="features" data-testid="features-section" className="py-24 md:py-32 border-t border-white/10 relative">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <div className="mb-16 max-w-3xl">
          <p className="text-overline mb-4">// What's inside the engine</p>
          <h2 className="font-serif text-4xl md:text-5xl tracking-tight leading-[1.05]">
            Most tools surface raw data. <br />
            <span className="italic text-[#D4AF37]">Bull-AI hands you a report.</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/10 border border-white/10">
          {FEATURES.map((f) => {
            const Icon = f.icon;
            return (
              <div
                key={f.title}
                data-testid="feature-card"
                className="bg-[#0A111A] p-8 md:p-10 hover:bg-[#111A26] transition-colors duration-300 group"
              >
                <div className="w-12 h-12 border border-[#00F0FF]/40 flex items-center justify-center mb-8 group-hover:border-[#00F0FF] transition-colors">
                  <Icon size={20} className="text-[#00F0FF]" />
                </div>
                <p className="text-overline mb-3">// {f.overline}</p>
                <h3 className="font-serif text-2xl md:text-3xl text-white tracking-tight leading-tight">
                  {f.title}
                </h3>
                <p className="mt-4 text-[#8C9BB0] leading-relaxed text-sm">{f.body}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
