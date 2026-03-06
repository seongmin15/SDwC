import { useState } from "react";

import { FileUploader } from "@/components/FileUploader/FileUploader";
import { TemplateDownloadButton } from "@/components/TemplateDownloadButton/TemplateDownloadButton";
import { ValidationResult } from "@/components/ValidationResult/ValidationResult";
import type { ValidationResponse } from "@/types/api";

import { Providers } from "./providers";

type UiState = "idle" | "uploading" | "validating" | "validation_error" | "validated";

export function App() {
  const [uiState, setUiState] = useState<UiState>("idle");
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null);

  async function handleUpload(file: File) {
    setUiState("uploading");

    const formData = new FormData();
    formData.append("file", file);

    setUiState("validating");

    try {
      const response = await fetch("/api/v1/validate", {
        method: "POST",
        body: formData,
      });
      const data = (await response.json()) as ValidationResponse;
      setValidationResult(data);
      setUiState(data.valid ? "validated" : "validation_error");
    } catch {
      setValidationResult({
        valid: false,
        errors: [
          {
            type: "https://sdwc.dev/errors/network-error",
            title: "Network Error",
            status: 0,
            detail: "Could not connect to the server. Please check your connection.",
            instance: "/api/v1/validate",
          },
        ],
        warnings: [],
      });
      setUiState("validation_error");
    }
  }

  function handleReset() {
    setUiState("idle");
    setValidationResult(null);
  }

  const isProcessing = uiState === "uploading" || uiState === "validating";

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
            <FileUploader onUpload={handleUpload} isDisabled={isProcessing} />
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
              {uiState === "uploading" ? "Uploading..." : "Validating..."}
            </div>
          )}

          {(uiState === "validation_error" || uiState === "validated") && validationResult && (
            <ValidationResult result={validationResult} onReset={handleReset} />
          )}
        </div>
      </main>
    </Providers>
  );
}
