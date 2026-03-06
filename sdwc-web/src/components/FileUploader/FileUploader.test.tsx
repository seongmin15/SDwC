import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FileUploader } from "./FileUploader";

describe("FileUploader", () => {
  it("should render the upload area", () => {
    render(<FileUploader onUpload={vi.fn()} />);

    expect(screen.getByRole("button", { name: /upload yaml file/i })).toBeInTheDocument();
    expect(screen.getByText(/drag & drop/i)).toBeInTheDocument();
  });

  it("should call onUpload when a file is selected via file picker", async () => {
    const onUpload = vi.fn();
    render(<FileUploader onUpload={onUpload} />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["project: test"], "intake_data.yaml", { type: "application/x-yaml" });

    await userEvent.upload(input, file);

    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it("should be disabled when isDisabled is true", () => {
    render(<FileUploader onUpload={vi.fn()} isDisabled />);

    const button = screen.getByRole("button", { name: /upload yaml file/i });
    expect(button).toHaveAttribute("aria-disabled", "true");
  });
});
