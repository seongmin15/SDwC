import type { PreviewResponse, Rfc7807Error, ValidationResponse } from "@/types/api";

function networkError(instance: string): Rfc7807Error {
  return {
    type: "https://sdwc.dev/errors/network-error",
    title: "Network Error",
    status: 0,
    detail: "Could not connect to the server. Please check your connection.",
    instance,
  };
}

export async function validateYaml(file: File): Promise<ValidationResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch("/api/v1/validate", { method: "POST", body: formData });
  } catch {
    return {
      valid: false,
      errors: [networkError("/api/v1/validate")],
      warnings: [],
    };
  }

  return (await response.json()) as ValidationResponse;
}

export async function fetchPreview(file: File): Promise<PreviewResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch("/api/v1/preview", { method: "POST", body: formData });
  } catch {
    throw networkError("/api/v1/preview");
  }

  if (!response.ok) {
    throw (await response.json()) as Rfc7807Error;
  }

  return (await response.json()) as PreviewResponse;
}

export interface GenerateResult {
  blob: Blob;
  filename: string;
}

export async function generateZip(file: File): Promise<GenerateResult> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch("/api/v1/generate", { method: "POST", body: formData });
  } catch {
    throw networkError("/api/v1/generate");
  }

  if (!response.ok) {
    throw (await response.json()) as Rfc7807Error;
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch?.[1] ?? "output.zip";

  return { blob, filename };
}
