import { FileSearch } from "lucide-react";

interface EmptyStateProps {
  query?: string;
}

export default function EmptyState({ query }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
      <FileSearch className="h-12 w-12 text-gray-300" />
      {query ? (
        <>
          <p className="text-gray-600 font-medium">No results found</p>
          <p className="text-gray-400 text-sm max-w-md">
            No studies matched &quot;{query}&quot;. Try different keywords or a
            broader search term.
          </p>
        </>
      ) : (
        <>
          <p className="text-gray-600 font-medium">
            Search for medical evidence
          </p>
          <p className="text-gray-400 text-sm max-w-md">
            Enter a medical topic, drug, condition, or treatment above to search
            across multiple evidence databases.
          </p>
        </>
      )}
    </div>
  );
}
