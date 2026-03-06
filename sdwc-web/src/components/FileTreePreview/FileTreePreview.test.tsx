import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { PreviewResponse } from "@/types/api";

import { FileTreePreview } from "./FileTreePreview";

const mockPreview: PreviewResponse = {
  file_tree: {
    "CLAUDE.md": {},
    docs: {
      common: {
        "00-project-overview.md": {},
        "01-requirements.md": {},
      },
    },
    skills: {
      common: {
        "git.md": {},
      },
    },
  },
  file_count: 4,
  services: [{ name: "test-api", type: "backend_api", framework: "fastapi" }],
};

describe("FileTreePreview", () => {
  it("should display the file count", () => {
    render(<FileTreePreview preview={mockPreview} />);
    expect(screen.getByText("4 files")).toBeInTheDocument();
  });

  it("should display service badges", () => {
    render(<FileTreePreview preview={mockPreview} />);
    expect(screen.getByText("test-api")).toBeInTheDocument();
    expect(screen.getByText("(fastapi)")).toBeInTheDocument();
  });

  it("should display file names", () => {
    render(<FileTreePreview preview={mockPreview} />);
    expect(screen.getByText("CLAUDE.md")).toBeInTheDocument();
  });

  it("should display folder names", () => {
    render(<FileTreePreview preview={mockPreview} />);
    expect(screen.getByText("docs")).toBeInTheDocument();
    expect(screen.getByText("skills")).toBeInTheDocument();
  });

  it("should collapse a folder when clicked", async () => {
    render(<FileTreePreview preview={mockPreview} />);

    // "common" under docs should be visible initially
    expect(screen.getByText("00-project-overview.md")).toBeInTheDocument();

    // Click the "docs" folder to collapse
    await userEvent.click(screen.getByRole("button", { name: /docs/i }));

    // Nested files should be hidden
    expect(screen.queryByText("00-project-overview.md")).not.toBeInTheDocument();
  });
});
