"use client";

import { useState, useCallback } from "react";
import Image from "next/image";
import SearchBar from "@/components/SearchBar";
import SummaryCard from "@/components/SummaryCard";
import StudyCard from "@/components/StudyCard";
import LoadingState from "@/components/LoadingState";
import EmptyState from "@/components/EmptyState";
import ErrorState from "@/components/ErrorState";
import { searchEvidence } from "@/lib/api";
import type { SearchResponse } from "@/lib/api";

export default function HomePage() {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchedQuery, setSearchedQuery] = useState("");

  const handleSearch = useCallback(async (query: string) => {
    setIsLoading(true);
    setError(null);
    setSearchedQuery(query);

    try {
      const data = await searchEvidence(query);
      setResults(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setError(message);
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    if (searchedQuery) {
      handleSearch(searchedQuery);
    }
  }, [searchedQuery, handleSearch]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <Image
            src="/logo.png"
            alt="Plato Evidence logo"
            width={44}
            height={44}
            className="rounded-lg"
            priority
          />
          <div>
            <h1 className="text-xl font-bold text-gray-900">Plato Evidence</h1>
            <p className="text-sm text-gray-500">
              Medical evidence search across multiple databases
            </p>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-4 py-8 flex flex-col gap-6">
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {/* Spell-correction banner */}
        {!isLoading && results && results.corrected_query && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-800">
            Showing results for{" "}
            <span className="font-semibold">{results.corrected_query}</span>{" "}
            instead of{" "}
            <span className="line-through text-amber-600">{results.query}</span>
          </div>
        )}

        {/* Content area */}
        {isLoading && <LoadingState />}

        {error && !isLoading && (
          <ErrorState message={error} onRetry={handleRetry} />
        )}

        {!isLoading && !error && results && results.studies.length === 0 && (
          <EmptyState query={searchedQuery} />
        )}

        {!isLoading && !error && results && results.studies.length > 0 && (
          <>
            <SummaryCard
              summary={results.summary}
              sourcesQueried={results.sources_queried}
              totalResults={results.total_results}
            />

            <div className="flex flex-col gap-4">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Studies ({results.total_results})
              </h2>
              {results.studies.map((study, index) => (
                <StudyCard key={`${study.source}-${index}`} study={study} />
              ))}
            </div>
          </>
        )}

        {!isLoading && !error && !results && <EmptyState />}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-100 bg-white mt-auto">
        <div className="max-w-5xl mx-auto px-4 py-4 text-center text-xs text-gray-400">
          Plato Evidence searches PubMed, ClinicalTrials.gov, Europe PMC, and
          OpenAlex. Not a substitute for professional medical advice.
        </div>
      </footer>
    </div>
  );
}
