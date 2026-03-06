import type { Rfc7807Error } from "@/types/api";

interface ErrorDisplayProps {
  error: Rfc7807Error;
  onReset: () => void;
}

export function ErrorDisplay({ error, onReset }: ErrorDisplayProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="mb-2 flex items-center justify-between">
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
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
          <p className="text-sm font-medium text-red-800">{error.title}</p>
        </div>
        <button onClick={onReset} className="text-sm text-red-600 underline hover:text-red-800">
          Start over
        </button>
      </div>
      <p className="text-sm text-red-700">{error.detail}</p>
      {error.status > 0 && (
        <p className="mt-1 text-xs text-red-400">
          Status {error.status} &middot; {error.instance}
        </p>
      )}
    </div>
  );
}
