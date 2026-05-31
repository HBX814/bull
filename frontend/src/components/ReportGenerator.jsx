import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "sonner";
import axios from "axios";
import {
  UploadCloud, FileText, X, Loader2, Download, Check, Sparkles,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STEPS = [
  "Parsing uploaded documents…",
  "Extracting financial metrics with Groq LLM…",
  "Composing analyst narrative…",
  "Rendering charts & PDF template…",
  "Finalising report…",
];

function StatusStream({ active }) {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    if (!active) { setIdx(0); return; }
    const t = setInterval(() => setIdx((p) => (p + 1) % STEPS.length), 2500);
    return () => clearInterval(t);
  }, [active]);
  if (!active) return null;
  return (
    <div data-testid="status-stream" className="mt-6 border border-[#00F0FF]/30 bg-[#00F0FF]/[0.04] p-5 font-mono text-xs">
      {STEPS.map((s, i) => {
        const done = i < idx;
        const cur = i === idx;
        return (
          <div key={s} className={`flex items-center gap-3 py-1 transition-colors ${done ? "text-[#00E676]" : cur ? "text-[#00F0FF]" : "text-[#8C9BB0]/50"}`}>
            {done ? <Check size={12} /> : cur ? <Loader2 size={12} className="animate-spin" /> : <span className="w-3 h-3 inline-block" />}
            <span>{s}</span>
          </div>
        );
      })}
    </div>
  );
}

export default function ReportGenerator() {
  const [company, setCompany] = useState("");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);

  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length) {
      toast.error(`Rejected: ${rejected.map((r) => r.file.name).join(", ")}`);
    }
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name + f.size));
      const fresh = accepted.filter((f) => !existing.has(f.name + f.size));
      return [...prev, ...fresh];
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/csv": [".csv"],
      "text/plain": [".txt"],
    },
    maxSize: 25 * 1024 * 1024,
  });

  const removeFile = (idx) => setFiles((f) => f.filter((_, i) => i !== idx));

  const submit = async (e) => {
    e.preventDefault();
    if (!company.trim()) return toast.error("Please enter a company name");
    if (!files.length) return toast.error("Please upload at least one document");

    setLoading(true);
    setReport(null);
    const fd = new FormData();
    fd.append("company_name", company.trim());
    files.forEach((f) => fd.append("files", f));

    try {
      const { data } = await axios.post(`${API}/generate-report`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 180000,
      });
      setReport(data);
      toast.success("Report generated.");
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Generation failed";
      toast.error(String(msg));
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async () => {
    if (!report) return;
    try {
      const res = await axios.get(`${API}/report/${report.report_id}/pdf`, {
        responseType: "blob",
      });
      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `bull-ai-${(report.company_name || "report").replace(/\s+/g, "-").toLowerCase()}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Download failed");
    }
  };

  return (
    <section id="generator" data-testid="generator-section" className="relative py-24 md:py-32 border-t border-white/10">
      <div className="max-w-5xl mx-auto px-6 lg:px-10">
        <div className="mb-12">
          <p className="text-overline mb-4">// Report Generator</p>
          <h2 className="font-serif text-4xl md:text-5xl tracking-tight leading-[1.05] max-w-3xl">
            One company. One upload.<br />
            <span className="italic text-[#D4AF37]">One downloadable PDF.</span>
          </h2>
          <p className="mt-5 text-[#8C9BB0] max-w-2xl leading-relaxed">
            Upload an earnings deck, a CSV of historicals, or a raw text transcript — Bull-AI extracts the
            numbers, drafts the narrative, and ships the report in Geojit-style layout.
          </p>
        </div>

        <form onSubmit={submit} className="bg-[#0A111A] border border-white/10 p-8 md:p-10">
          <label className="block">
            <span className="text-overline">// Company Name</span>
            <div className="mt-3 flex items-center gap-3 bg-[#050A10] border border-white/15 px-4 py-3 focus-within:border-[#00F0FF] transition-colors">
              <Sparkles size={14} className="text-[#00F0FF]" />
              <input
                data-testid="company-input"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g. JSW Energy, ICICI Bank, Eternal Ltd"
                className="flex-1 bg-transparent outline-none font-mono text-sm text-white placeholder:text-[#8C9BB0]/50"
              />
              <kbd className="hidden md:block font-mono text-[0.6rem] text-[#8C9BB0] border border-white/15 px-1.5 py-0.5">
                ⌘K
              </kbd>
            </div>
          </label>

          <div className="mt-8">
            <span className="text-overline">// Context Documents (PDF / CSV / TXT)</span>
            <div
              {...getRootProps()}
              data-testid="file-dropzone"
              className={`mt-3 border-2 border-dashed transition-all duration-300 cursor-pointer flex flex-col items-center justify-center text-center py-14 px-6 ${
                isDragActive
                  ? "border-[#00F0FF] bg-[#00F0FF]/[0.06]"
                  : "border-white/20 bg-[#050A10] hover:border-[#00F0FF]/60 hover:bg-[#111A26]"
              }`}
            >
              <input {...getInputProps()} data-testid="file-input" />
              <UploadCloud size={32} className="text-[#00F0FF] mb-3" />
              <p className="font-serif text-xl text-white">
                {isDragActive ? "Drop files here" : "Drag & drop or click to upload"}
              </p>
              <p className="mt-2 font-mono text-xs text-[#8C9BB0]">
                PDF • CSV • TXT &nbsp;{"\u2022"}&nbsp; up to 25 MB each
              </p>
            </div>

            {!!files.length && (
              <ul data-testid="file-list" className="mt-4 space-y-2">
                {files.map((f, i) => (
                  <li
                    key={i}
                    data-testid={`file-item-${i}`}
                    className="flex items-center justify-between bg-[#050A10] border border-white/10 px-4 py-3 font-mono text-xs"
                  >
                    <span className="flex items-center gap-3 truncate">
                      <FileText size={14} className="text-[#00F0FF] flex-shrink-0" />
                      <span className="truncate">{f.name}</span>
                      <span className="text-[#8C9BB0]">{(f.size / 1024).toFixed(1)} KB</span>
                    </span>
                    <button
                      type="button"
                      data-testid={`remove-file-${i}`}
                      onClick={() => removeFile(i)}
                      className="text-[#8C9BB0] hover:text-[#FF3366] transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="mt-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <button
              type="submit"
              data-testid="generate-button"
              disabled={loading}
              className="flex-1 sm:flex-none bg-white text-[#050A10] font-semibold px-8 py-4 hover:bg-[#00F0FF] transition-colors duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Generating…
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Generate Research PDF
                </>
              )}
            </button>
            {report && (
              <button
                type="button"
                data-testid="download-pdf-button"
                onClick={downloadPdf}
                className="flex items-center justify-center gap-2 border border-[#D4AF37] text-[#D4AF37] px-8 py-4 hover:bg-[#D4AF37] hover:text-[#050A10] transition-colors"
              >
                <Download size={16} /> Download PDF
              </button>
            )}
          </div>

          <StatusStream active={loading} />

          {report && (
            <div
              data-testid="result-card"
              className="mt-6 border border-[#00E676]/30 bg-[#00E676]/[0.04] p-6"
            >
              <div className="flex items-center gap-3 mb-3">
                <Check size={14} className="text-[#00E676]" />
                <span className="text-overline" style={{ color: "#00E676" }}>// Report Ready</span>
              </div>
              <div className="font-serif text-2xl text-white">{report.company_name}</div>
              {report.headline && (
                <p className="mt-1 text-[#8C9BB0] text-sm italic">{report.headline}</p>
              )}
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
                <div>
                  <div className="text-[#8C9BB0] uppercase tracking-wider mb-1">Rating</div>
                  <div className="text-white font-semibold">{report.rating || "—"}</div>
                </div>
                <div>
                  <div className="text-[#8C9BB0] uppercase tracking-wider mb-1">Target</div>
                  <div className="text-white font-semibold">{report.target_price || "—"}</div>
                </div>
                <div>
                  <div className="text-[#8C9BB0] uppercase tracking-wider mb-1">CMP</div>
                  <div className="text-white font-semibold">{report.summary?.cmp || "—"}</div>
                </div>
                <div>
                  <div className="text-[#8C9BB0] uppercase tracking-wider mb-1">Title</div>
                  <div className="text-white font-semibold">{report.summary?.report_title || "—"}</div>
                </div>
              </div>
            </div>
          )}
        </form>
      </div>
    </section>
  );
}
