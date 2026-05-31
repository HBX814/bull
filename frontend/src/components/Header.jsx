import React, { useState, useEffect } from "react";
import { Command, Menu } from "lucide-react";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <header
      data-testid="site-header"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "backdrop-blur-xl bg-[#050A10]/80 border-b border-white/10"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-10 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 border border-[#00F0FF] flex items-center justify-center">
            <span className="font-serif text-[#00F0FF] text-lg leading-none">B</span>
          </div>
          <div>
            <div className="font-serif text-xl leading-none tracking-tight">Bull-AI</div>
            <div className="font-mono text-[0.55rem] uppercase tracking-[0.25em] text-[#8C9BB0] mt-0.5">
              Research
            </div>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-10 font-mono text-xs uppercase tracking-[0.2em] text-[#8C9BB0]">
          <a href="#generator" className="hover:text-white transition-colors" data-testid="nav-generator">Generator</a>
          <a href="#features" className="hover:text-white transition-colors" data-testid="nav-features">Engine</a>
          <a href="#recent" className="hover:text-white transition-colors" data-testid="nav-recent">Recent</a>
        </nav>

        <div className="hidden md:flex items-center gap-3 px-3 py-1.5 border border-white/15 font-mono text-xs text-[#8C9BB0]">
          <Command size={12} />
          <span>K</span>
        </div>
        <button className="md:hidden text-white" data-testid="mobile-menu-button">
          <Menu size={22} />
        </button>
      </div>
    </header>
  );
}
