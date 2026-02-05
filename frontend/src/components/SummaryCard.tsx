import { Sparkles } from "lucide-react";

interface SummaryCardProps {
  summary: string;
  sourcesQueried: string[];
  totalResults: number;
}

export default function SummaryCard({
  summary,
  sourcesQueried,
  totalResults,
}: SummaryCardProps) {
  if (!summary) {
    return null;
  }

  return (
    <div className="w-full max-w-3xl mx-auto rounded-xl border border-blue-100 bg-blue-50 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="h-5 w-5 text-blue-600" />
        <h2 className="text-sm font-semibold text-blue-900 uppercase tracking-wide">
          AI Evidence Summary
        </h2>
      </div>
      <p className="text-gray-800 text-base leading-relaxed">{summary}</p>
      <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-gray-500">
        <span>{totalResults} studies found</span>
        <span className="text-gray-300">|</span>
        <span>Sources: {sourcesQueried.join(", ")}</span>
      </div>
    </div>
  );
}
