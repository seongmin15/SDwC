import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { PreviewResponse, ValidationResponse } from "@/types/api";

import { fetchPreview, generateZip, validateYaml } from "./intakeApi";

const mockFile = new File(["test"], "intake.yaml", { type: "application/x-yaml" });

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("validateYaml", () => {
  it("should POST file to /api/v1/validate and return response", async () => {
    const mockResponse: ValidationResponse = { valid: true, errors: [], warnings: [] };
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify(mockResponse)));

    const result = await validateYaml(mockFile);

    expect(fetch).toHaveBeenCalledWith("/api/v1/validate", {
      method: "POST",
      body: expect.any(FormData) as FormData,
    });
    expect(result).toEqual(mockResponse);
  });

  it("should return validation error response on network failure", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("Failed to fetch"));

    const result = await validateYaml(mockFile);

    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0]?.title).toBe("Network Error");
  });
});

describe("fetchPreview", () => {
  it("should POST file to /api/v1/preview and return preview data", async () => {
    const mockPreview: PreviewResponse = {
      file_tree: { "docs/": {} },
      file_count: 5,
      services: [{ name: "api", type: "backend_api", framework: "fastapi" }],
    };
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify(mockPreview)));

    const result = await fetchPreview(mockFile);

    expect(fetch).toHaveBeenCalledWith("/api/v1/preview", {
      method: "POST",
      body: expect.any(FormData) as FormData,
    });
    expect(result).toEqual(mockPreview);
  });

  it("should throw RFC 7807 error on non-OK response", async () => {
    const errorBody = {
      type: "https://sdwc.dev/errors/rendering-failed",
      title: "Rendering Failed",
      status: 500,
      detail: "Template error",
      instance: "/api/v1/preview",
    };
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify(errorBody), { status: 500 }));

    await expect(fetchPreview(mockFile)).rejects.toEqual(errorBody);
  });

  it("should throw network error on fetch failure", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(fetchPreview(mockFile)).rejects.toEqual(
      expect.objectContaining({ title: "Network Error", instance: "/api/v1/preview" }),
    );
  });
});

describe("generateZip", () => {
  it("should POST file to /api/v1/generate and return blob with filename", async () => {
    const blob = new Blob(["zipdata"], { type: "application/zip" });
    const headers = new Headers({ "Content-Disposition": 'attachment; filename="project.zip"' });
    vi.mocked(fetch).mockResolvedValue(new Response(blob, { status: 200, headers }));

    const result = await generateZip(mockFile);

    expect(fetch).toHaveBeenCalledWith("/api/v1/generate", {
      method: "POST",
      body: expect.any(FormData) as FormData,
    });
    expect(result.filename).toBe("project.zip");
    expect(result.blob).toBeInstanceOf(Blob);
  });

  it("should default filename to output.zip when Content-Disposition is missing", async () => {
    const blob = new Blob(["zipdata"], { type: "application/zip" });
    vi.mocked(fetch).mockResolvedValue(new Response(blob, { status: 200 }));

    const result = await generateZip(mockFile);

    expect(result.filename).toBe("output.zip");
  });

  it("should throw RFC 7807 error on non-OK response", async () => {
    const errorBody = {
      type: "https://sdwc.dev/errors/rendering-failed",
      title: "Rendering Failed",
      status: 500,
      detail: "Timeout",
      instance: "/api/v1/generate",
    };
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify(errorBody), { status: 500 }));

    await expect(generateZip(mockFile)).rejects.toEqual(errorBody);
  });

  it("should throw network error on fetch failure", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(generateZip(mockFile)).rejects.toEqual(
      expect.objectContaining({ title: "Network Error", instance: "/api/v1/generate" }),
    );
  });
});
