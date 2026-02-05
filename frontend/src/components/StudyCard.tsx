"use client";

import { useState } from "react";
import {
  ExternalLink,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Users,
  Calendar,
} from "lucide-react";
import type { Study } from "@/lib/api";

interface StudyCardProps {
  study: Study;
}

const SOURCE_COLORS: Record<string, string> = {
  PubMed: "bg-green-100 text-green-800",
  ClinicalTrials: "bg-purple-100 text-purple-800",
  EuropePMC: "bg-orange-100 text-orange-800",
  OpenAlex: "bg-cyan-100 text-cyan-800",
};

export default function StudyCard({ study }: StudyCardProps) {
  const [expanded, setExpanded] = useState(false);

  const badgeColor = SOURCE_COLORS[study.source] || "bg-gray-100 text-gray-800";
  const hasAbstract = study.abstract.length > 0;
  const displayAuthors =
    study.authors.length > 3
      ? `${study.authors.slice(0, 3).join(", ")} et al.`
      : study.authors.join(", ");

  return (
    <div className="w-full rounded-lg border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeColor}`}
            >
              {study.source}
            </span>
            {study.publication_date && (
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <Calendar className="h-3 w-3" />
                {study.publication_date}
              </span>
            )}
          </div>

          {study.url ? (
            <a
              href={study.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-base font-semibold text-gray-900 hover:text-blue-600 transition-colors leading-snug"
            >
              {study.title}
              <ExternalLink className="inline ml-1 h-3.5 w-3.5 text-gray-400" />
            </a>
          ) : (
            <h3 className="text-base font-semibold text-gray-900 leading-snug">
              {study.title}
            </h3>
          )}
        </div>
      </div>

      {/* Metadata */}
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500">
        {displayAuthors && (
          <span className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" />
            {displayAuthors}
          </span>
        )}
        {study.journal && (
          <span className="flex items-center gap-1">
            <BookOpen className="h-3.5 w-3.5" />
            {study.journal}
          </span>
        )}
      </div>

      {/* Abstract toggle */}
      {hasAbstract && (
        <div className="mt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            {expanded ? (
              <>
                Hide abstract <ChevronUp className="h-4 w-4" />
              </>
            ) : (
              <>
                Show abstract <ChevronDown className="h-4 w-4" />
              </>
            )}
          </button>
          {expanded && (
            <p className="mt-2 text-sm text-gray-600 leading-relaxed whitespace-pre-line">
              {study.abstract}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
