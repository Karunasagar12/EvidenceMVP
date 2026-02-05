import { Loader2 } from "lucide-react";

export default function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
      <p className="text-gray-500 text-sm">
        Searching across PubMed, ClinicalTrials.gov, Europe PMC, and OpenAlex...
      </p>
    </div>
  );
}
