import { ErrorDisplay } from "@/components/ErrorDisplay/ErrorDisplay";
import { FileTreePreview } from "@/components/FileTreePreview/FileTreePreview";
import { FileUploader } from "@/components/FileUploader/FileUploader";
import { GenerateButton } from "@/components/GenerateButton/GenerateButton";
import { TemplateDownloadButton } from "@/components/TemplateDownloadButton/TemplateDownloadButton";
import { ValidationResult } from "@/components/ValidationResult/ValidationResult";
import { useIntakeStore } from "@/stores/useIntakeStore";

import { Providers } from "./providers";

export function App() {
  const uiState = useIntakeStore((s) => s.uiState);
  const validationResult = useIntakeStore((s) => s.validationResult);
  const previewData = useIntakeStore((s) => s.previewData);
  const error = useIntakeStore((s) => s.error);
  const upload = useIntakeStore((s) => s.upload);
  const generate = useIntakeStore((s) => s.generate);
  const reset = useIntakeStore((s) => s.reset);

  const isProcessing =
    uiState === "uploading" || uiState === "validating" || uiState === "previewing";

  return (
    <Providers>
      <main className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
        <div className="w-full max-w-lg space-y-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">SDwC</h1>
            <p className="mt-1 text-sm text-gray-500">Survey-driven documentation generator</p>
          </div>

          <div className="flex justify-center">
            <TemplateDownloadButton isDisabled={isProcessing} />
          </div>

          {(uiState === "idle" || isProcessing) && (
            <FileUploader onUpload={upload} isDisabled={isProcessing} />
          )}

          {isProcessing && (
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
              <svg
                className="h-4 w-4 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              {uiState === "uploading" && "Uploading..."}
              {uiState === "validating" && "Validating..."}
              {uiState === "previewing" && "Loading preview..."}
            </div>
          )}

          {uiState === "validation_error" && validationResult && (
            <ValidationResult result={validationResult} onReset={reset} />
          )}

          {(uiState === "preview_ready" || uiState === "generating" || uiState === "complete") &&
            previewData && <FileTreePreview preview={previewData} />}

          {(uiState === "preview_ready" || uiState === "generating") && (
            <GenerateButton onGenerate={generate} isGenerating={uiState === "generating"} />
          )}

          {uiState === "complete" && (
            <div className="space-y-3">
              <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                <div className="flex items-center gap-2">
                  <svg
                    className="h-5 w-5 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <p className="text-sm font-medium text-green-800">ZIP downloaded successfully</p>
                </div>
              </div>
              <button
                onClick={reset}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
              >
                Generate another
              </button>
            </div>
          )}

          {uiState === "generation_error" && error && (
            <ErrorDisplay error={error} onReset={reset} />
          )}
        </div>
      </main>
    </Providers>
  );
}
