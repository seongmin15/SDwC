import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TemplateDownloadButton } from "./TemplateDownloadButton";

describe("TemplateDownloadButton", () => {
  it("should render a download link", () => {
    render(<TemplateDownloadButton />);

    const link = screen.getByRole("link", { name: /download template/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/api/v1/template");
    expect(link).toHaveAttribute("download", "intake_template.yaml");
  });

  it("should be visually disabled when isDisabled is true", () => {
    render(<TemplateDownloadButton isDisabled />);

    const link = screen.getByRole("link", { name: /download template/i });
    expect(link).toHaveAttribute("aria-disabled", "true");
    expect(link.className).toContain("pointer-events-none");
  });
});
