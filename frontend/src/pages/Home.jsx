import React from "react";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import StockMarquee from "@/components/StockMarquee";
import ReportGenerator from "@/components/ReportGenerator";
import RecentReports from "@/components/RecentReports";
import Features from "@/components/Features";
import TrustedBy from "@/components/TrustedBy";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div data-testid="home-page" className="min-h-screen bg-[#050A10] text-white overflow-x-hidden">
      <Header />
      <Hero />
      <StockMarquee />
      <ReportGenerator />
      <RecentReports />
      <TrustedBy />
      <Features />
      <Footer />
    </div>
  );
}
