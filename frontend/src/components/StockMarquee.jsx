import React from "react";
import Marquee from "react-fast-marquee";
import { TrendingUp, TrendingDown } from "lucide-react";

const TICKERS = [
  { sym: "RELIANCE", name: "Reliance Industries", price: "1,302.40", chg: 0.85, up: true },
  { sym: "TCS", name: "Tata Consultancy", price: "3,612.20", chg: -0.42, up: false },
  { sym: "HDFCBANK", name: "HDFC Bank", price: "1,712.55", chg: 1.13, up: true },
  { sym: "INFY", name: "Infosys", price: "1,489.10", chg: -1.07, up: false },
  { sym: "ICICIBANK", name: "ICICI Bank", price: "1,233.80", chg: 0.62, up: true },
  { sym: "JSWENERGY", name: "JSW Energy", price: "541.25", chg: 2.04, up: true },
  { sym: "LTTS", name: "L\u0026T Technology", price: "4,820.55", chg: -0.92, up: false },
  { sym: "BHARTIARTL", name: "Bharti Airtel", price: "1,612.40", chg: 0.31, up: true },
  { sym: "POCL", name: "Pondy Oxides", price: "972.65", chg: -2.18, up: false },
  { sym: "ASIANPAINT", name: "Asian Paints", price: "2,361.80", chg: 0.74, up: true },
  { sym: "ETERNAL", name: "Eternal Ltd", price: "324.10", chg: 1.92, up: true },
  { sym: "MARUTI", name: "Maruti Suzuki", price: "11,205.40", chg: -0.55, up: false },
  { sym: "WIPRO", name: "Wipro", price: "554.30", chg: 0.18, up: true },
  { sym: "ADANIENT", name: "Adani Enterprises", price: "2,488.90", chg: -1.46, up: false },
  { sym: "SBIN", name: "State Bank of India", price: "812.15", chg: 0.68, up: true },
];

function TickerItem({ t }) {
  const Arrow = t.up ? TrendingUp : TrendingDown;
  const color = t.up ? "text-[#00E676]" : "text-[#FF3366]";
  return (
    <div
      data-testid="marquee-item"
      className="flex items-center gap-3 px-8 border-r border-white/10 h-full"
    >
      <span className="font-mono text-xs text-white tracking-tight">{t.sym}</span>
      <span className="font-sans text-xs text-[#8C9BB0] hidden md:inline">{t.name}</span>
      <span className="font-mono text-xs text-white">{t.price}</span>
      <span className={`font-mono text-xs flex items-center gap-1 ${color}`}>
        <Arrow size={11} />
        {t.up ? "+" : ""}
        {t.chg}%
      </span>
    </div>
  );
}

export default function StockMarquee() {
  return (
    <div
      data-testid="stock-marquee"
      className="relative bg-black border-y border-white/10 py-3"
    >
      <Marquee gradient={false} speed={45} pauseOnHover>
        {TICKERS.map((t, i) => <TickerItem key={i} t={t} />)}
      </Marquee>
    </div>
  );
}
