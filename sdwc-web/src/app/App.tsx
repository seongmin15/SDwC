import { useEffect, useRef, useState } from "react";

import { ErrorDisplay } from "@/components/ErrorDisplay/ErrorDisplay";
import { FileTreePreview } from "@/components/FileTreePreview/FileTreePreview";
import { FileUploader } from "@/components/FileUploader/FileUploader";
import { GenerateButton } from "@/components/GenerateButton/GenerateButton";
import { TemplateDownloadButton } from "@/components/TemplateDownloadButton/TemplateDownloadButton";
import { ValidationResult } from "@/components/ValidationResult/ValidationResult";
import type { PreviewResponse, Rfc7807Error, ValidationResponse } from "@/types/api";

import { Providers } from "./providers";

type UiState =
  | "idle"
  | "uploading"
  | "validating"
  | "validation_error"
  | "previewing"
  | "preview_ready"
  | "generating"
  | "complete"
  | "generation_error";

export function App() {
  const [uiState, setUiState] = useState<UiState>("idle");
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null);
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);
  const [error, setError] = useState<Rfc7807Error | null>(null);
  const uploadedFileRef = useRef<File | null>(null);

  async function handleUpload(file: File) {
    uploadedFileRef.current = file;
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

      if (data.valid) {
        setUiState("previewing");
      } else {
        setUiState("validation_error");
      }
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

  // Auto-trigger preview after validation passes
  useEffect(() => {
    if (uiState !== "previewing" || !uploadedFileRef.current) return;

    let cancelled = false;

    async function fetchPreview() {
      const formData = new FormData();
      formData.append("file", uploadedFileRef.current!);

      try {
        const response = await fetch("/api/v1/preview", {
          method: "POST",
          body: formData,
        });

        if (cancelled) return;

        if (!response.ok) {
          const errData = (await response.json()) as Rfc7807Error;
          setError(errData);
          setUiState("generation_error");
          return;
        }

        const data = (await response.json()) as PreviewResponse;
        setPreviewData(data);
        setUiState("preview_ready");
      } catch {
        if (cancelled) return;
        setError({
          type: "https://sdwc.dev/errors/network-error",
          title: "Network Error",
          status: 0,
          detail: "Could not connect to the server. Please check your connection.",
          instance: "/api/v1/preview",
        });
        setUiState("generation_error");
      }
    }

    void fetchPreview();
    return () => {
      cancelled = true;
    };
  }, [uiState]);

  async function handleGenerate() {
    if (!uploadedFileRef.current) return;
    setUiState("generating");

    const formData = new FormData();
    formData.append("file", uploadedFileRef.current);

    try {
      const response = await fetch("/api/v1/generate", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = (await response.json()) as Rfc7807Error;
        setError(errData);
        setUiState("generation_error");
        return;
      }

      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition") ?? "";
      const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch?.[1] ?? "output.zip";

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      setUiState("complete");
    } catch {
      setError({
        type: "https://sdwc.dev/errors/network-error",
        title: "Network Error",
        status: 0,
        detail: "Could not connect to the server. Please check your connection.",
        instance: "/api/v1/generate",
      });
      setUiState("generation_error");
    }
  }

  function handleReset() {
    setUiState("idle");
    setValidationResult(null);
    setPreviewData(null);
    setError(null);
    uploadedFileRef.current = null;
  }

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
              {uiState === "uploading" && "Uploading..."}
              {uiState === "validating" && "Validating..."}
              {uiState === "previewing" && "Loading preview..."}
            </div>
          )}

          {uiState === "validation_error" && validationResult && (
            <ValidationResult result={validationResult} onReset={handleReset} />
          )}

          {(uiState === "preview_ready" || uiState === "generating" || uiState === "complete") &&
            previewData && <FileTreePreview preview={previewData} />}

          {(uiState === "preview_ready" || uiState === "generating") && (
            <GenerateButton onGenerate={handleGenerate} isGenerating={uiState === "generating"} />
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
                onClick={handleReset}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
              >
                Generate another
              </button>
            </div>
          )}

          {uiState === "generation_error" && error && (
            <ErrorDisplay error={error} onReset={handleReset} />
          )}
        </div>
      </main>
    </Providers>
  );
}
