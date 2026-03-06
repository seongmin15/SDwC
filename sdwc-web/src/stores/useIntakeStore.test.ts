import { beforeEach, describe, expect, it, vi } from "vitest";

import type { PreviewResponse, ValidationResponse } from "@/types/api";

// Mock the API service before importing the store
vi.mock("@/services/intakeApi", () => ({
  validateYaml: vi.fn(),
  fetchPreview: vi.fn(),
  generateZip: vi.fn(),
}));

// Import after mock setup
const { validateYaml, fetchPreview, generateZip } = await import("@/services/intakeApi");
const { useIntakeStore } = await import("./useIntakeStore");

const mockFile = new File(["test"], "intake.yaml", { type: "application/x-yaml" });

const validResponse: ValidationResponse = { valid: true, errors: [], warnings: [] };
const invalidResponse: ValidationResponse = {
  valid: false,
  errors: [
    {
      type: "https://sdwc.dev/errors/validation-failed",
      title: "Validation Failed",
      status: 422,
      detail: "Missing required field",
      instance: "/api/v1/validate",
    },
  ],
  warnings: [],
};
const mockPreview: PreviewResponse = {
  file_tree: { "docs/": {} },
  file_count: 3,
  services: [{ name: "api", type: "backend_api", framework: "fastapi" }],
};

beforeEach(() => {
  vi.clearAllMocks();
  useIntakeStore.getState().reset();
});

describe("useIntakeStore", () => {
  describe("initial state", () => {
    it("should start in idle state with null data", () => {
      const state = useIntakeStore.getState();
      expect(state.uiState).toBe("idle");
      expect(state.validationResult).toBeNull();
      expect(state.previewData).toBeNull();
      expect(state.error).toBeNull();
      expect(state.uploadedFile).toBeNull();
    });
  });

  describe("upload", () => {
    it("should validate and auto-chain to preview on valid input", async () => {
      vi.mocked(validateYaml).mockResolvedValue(validResponse);
      vi.mocked(fetchPreview).mockResolvedValue(mockPreview);

      await useIntakeStore.getState().upload(mockFile);

      const state = useIntakeStore.getState();
      expect(state.uiState).toBe("preview_ready");
      expect(state.validationResult).toEqual(validResponse);
      expect(state.previewData).toEqual(mockPreview);
      expect(state.uploadedFile).toBe(mockFile);
    });

    it("should stop at validation_error on invalid input", async () => {
      vi.mocked(validateYaml).mockResolvedValue(invalidResponse);

      await useIntakeStore.getState().upload(mockFile);

      const state = useIntakeStore.getState();
      expect(state.uiState).toBe("validation_error");
      expect(state.validationResult).toEqual(invalidResponse);
      expect(fetchPreview).not.toHaveBeenCalled();
    });

    it("should set generation_error when preview fails", async () => {
      const previewError = {
        type: "https://sdwc.dev/errors/rendering-failed",
        title: "Rendering Failed",
        status: 500,
        detail: "Template error",
        instance: "/api/v1/preview",
      };
      vi.mocked(validateYaml).mockResolvedValue(validResponse);
      vi.mocked(fetchPreview).mockRejectedValue(previewError);

      await useIntakeStore.getState().upload(mockFile);

      const state = useIntakeStore.getState();
      expect(state.uiState).toBe("generation_error");
      expect(state.error).toEqual(previewError);
    });
  });

  describe("generate", () => {
    it("should download ZIP and transition to complete", async () => {
      // Set up state as if preview is ready
      vi.mocked(validateYaml).mockResolvedValue(validResponse);
      vi.mocked(fetchPreview).mockResolvedValue(mockPreview);
      await useIntakeStore.getState().upload(mockFile);

      const mockBlob = new Blob(["zip"], { type: "application/zip" });
      vi.mocked(generateZip).mockResolvedValue({ blob: mockBlob, filename: "project.zip" });

      // Mock DOM methods for download
      const mockClick = vi.fn();
      const mockRemove = vi.fn();
      vi.spyOn(document, "createElement").mockReturnValue({
        href: "",
        download: "",
        click: mockClick,
        remove: mockRemove,
      } as unknown as HTMLAnchorElement);
      vi.spyOn(document.body, "appendChild").mockReturnValue(null as unknown as HTMLAnchorElement);
      vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:mock-url");
      vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);

      await useIntakeStore.getState().generate();

      expect(useIntakeStore.getState().uiState).toBe("complete");
      expect(mockClick).toHaveBeenCalled();
      expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock-url");
    });

    it("should set generation_error when generate fails", async () => {
      // Set up state with uploaded file
      vi.mocked(validateYaml).mockResolvedValue(validResponse);
      vi.mocked(fetchPreview).mockResolvedValue(mockPreview);
      await useIntakeStore.getState().upload(mockFile);

      const genError = {
        type: "https://sdwc.dev/errors/rendering-failed",
        title: "Rendering Failed",
        status: 500,
        detail: "Timeout",
        instance: "/api/v1/generate",
      };
      vi.mocked(generateZip).mockRejectedValue(genError);

      await useIntakeStore.getState().generate();

      const state = useIntakeStore.getState();
      expect(state.uiState).toBe("generation_error");
      expect(state.error).toEqual(genError);
    });

    it("should do nothing when no file is uploaded", async () => {
      await useIntakeStore.getState().generate();

      expect(useIntakeStore.getState().uiState).toBe("idle");
      expect(generateZip).not.toHaveBeenCalled();
    });
  });

  describe("reset", () => {
    it("should return to idle state with all data cleared", async () => {
      vi.mocked(validateYaml).mockResolvedValue(validResponse);
      vi.mocked(fetchPreview).mockResolvedValue(mockPreview);
      await useIntakeStore.getState().upload(mockFile);

      useIntakeStore.getState().reset();

      const state = useIntakeStore.getState();
      expect(state.uiState).toBe("idle");
      expect(state.validationResult).toBeNull();
      expect(state.previewData).toBeNull();
      expect(state.error).toBeNull();
      expect(state.uploadedFile).toBeNull();
    });
  });
});
