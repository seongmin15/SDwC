import type { ValidationResponse } from "@/types/api";

interface ValidationResultProps {
  result: ValidationResponse;
  onReset: () => void;
}

export function ValidationResult({ result, onReset }: ValidationResultProps) {
  if (result.valid) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 p-4">
        <div className="flex items-center gap-2">
          <svg
            className="h-5 w-5 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <p className="text-sm font-medium text-green-800">Validation passed</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <svg
            className="h-5 w-5 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
          <p className="text-sm font-medium text-red-800">
            Validation failed ({result.errors.length} error{result.errors.length !== 1 ? "s" : ""})
          </p>
        </div>
        <button onClick={onReset} className="text-sm text-red-600 underline hover:text-red-800">
          Try again
        </button>
      </div>
      <ul className="space-y-1">
        {result.errors.map((error, index) => (
          <li key={index} className="text-sm text-red-700">
            <span className="font-mono text-xs">{error.detail}</span>
          </li>
        ))}
      </ul>
      {result.warnings.length > 0 && (
        <div className="mt-3 border-t border-red-200 pt-3">
          <p className="mb-1 text-sm font-medium text-amber-700">
            Warnings ({result.warnings.length})
          </p>
          <ul className="space-y-1">
            {result.warnings.map((warning, index) => (
              <li key={index} className="text-sm text-amber-600">
                {warning.detail}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
