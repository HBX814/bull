import React from "react";

export default function Footer() {
  return (
    <footer data-testid="site-footer" className="border-t border-white/10 py-12 mt-12">
      <div className="max-w-7xl mx-auto px-6 lg:px-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 border border-[#00F0FF] flex items-center justify-center">
              <span className="font-serif text-[#00F0FF] text-lg leading-none">B</span>
            </div>
            <div>
              <div className="font-serif text-lg leading-none">Bull-AI Research</div>
              <div className="font-mono text-[0.55rem] uppercase tracking-[0.25em] text-[#8C9BB0] mt-1">
                Auto-generated equity research
              </div>
            </div>
          </div>
        </div>

        <p className="font-mono text-[0.65rem] uppercase tracking-[0.2em] text-[#8C9BB0] max-w-md md:text-right">
          For research and educational purposes. <br />
          Not investment advice. Verify all numbers from official filings.
        </p>
      </div>
    </footer>
  );
}
