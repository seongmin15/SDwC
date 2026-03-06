import { create } from "zustand";

import { fetchPreview, generateZip, validateYaml } from "@/services/intakeApi";
import type { PreviewResponse, Rfc7807Error, ValidationResponse } from "@/types/api";

export type UiState =
  | "idle"
  | "uploading"
  | "validating"
  | "validation_error"
  | "previewing"
  | "preview_ready"
  | "generating"
  | "complete"
  | "generation_error";

interface IntakeState {
  uiState: UiState;
  validationResult: ValidationResponse | null;
  previewData: PreviewResponse | null;
  error: Rfc7807Error | null;
  uploadedFile: File | null;

  upload: (file: File) => Promise<void>;
  generate: () => Promise<void>;
  reset: () => void;
}

export const useIntakeStore = create<IntakeState>()((set, get) => ({
  uiState: "idle",
  validationResult: null,
  previewData: null,
  error: null,
  uploadedFile: null,

  async upload(file: File) {
    set({ uploadedFile: file, uiState: "uploading" });
    set({ uiState: "validating" });

    const result = await validateYaml(file);
    set({ validationResult: result });

    if (!result.valid) {
      set({ uiState: "validation_error" });
      return;
    }

    // Auto-chain to preview
    set({ uiState: "previewing" });

    try {
      const preview = await fetchPreview(file);
      set({ previewData: preview, uiState: "preview_ready" });
    } catch (err) {
      set({ error: err as Rfc7807Error, uiState: "generation_error" });
    }
  },

  async generate() {
    const { uploadedFile } = get();
    if (!uploadedFile) return;

    set({ uiState: "generating" });

    try {
      const { blob, filename } = await generateZip(uploadedFile);

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      set({ uiState: "complete" });
    } catch (err) {
      set({ error: err as Rfc7807Error, uiState: "generation_error" });
    }
  },

  reset() {
    set({
      uiState: "idle",
      validationResult: null,
      previewData: null,
      error: null,
      uploadedFile: null,
    });
  },
}));
