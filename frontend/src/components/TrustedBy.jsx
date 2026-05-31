import React from "react";

const LOGOS = [
  "https://www.bull-ai.in/images/trusted-logos/b2v-ventures.png",
  "https://www.bull-ai.in/images/trusted-logos/mga-ventures.png",
  "https://www.bull-ai.in/images/trusted-logos/oculus-capital.png",
  "https://www.bull-ai.in/images/trusted-logos/kotak-securities.png",
  "https://www.bull-ai.in/images/trusted-logos/morgan-stanley.png",
  "https://www.bull-ai.in/images/trusted-logos/motilal-oswal.png",
  "https://www.bull-ai.in/images/trusted-logos/iifl-capital.png",
  "https://www.bull-ai.in/images/trusted-logos/arihant-capital.png",
];

export default function TrustedBy() {
  return (
    <section data-testid="trusted-by-section" className="py-16 border-t border-white/10 bg-black/40">
      <div className="max-w-6xl mx-auto px-6 lg:px-10 text-center">
        <p className="font-mono text-[0.65rem] uppercase tracking-[0.3em] text-[#8C9BB0]">
          Designed for analysts at top brokerages
        </p>
        <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-10 items-center opacity-70">
          {LOGOS.map((url) => (
            <img
              key={url}
              src={url}
              alt="logo"
              className="h-7 md:h-8 mx-auto object-contain grayscale brightness-200 contrast-50 hover:grayscale-0 hover:opacity-100 transition-all duration-300"
              data-testid="trusted-logo"
            />
          ))}
        </div>
        <p className="mt-6 font-mono text-[0.6rem] text-[#8C9BB0]/60">
          Logos shown for representative purposes only
        </p>
      </div>
    </section>
  );
}
