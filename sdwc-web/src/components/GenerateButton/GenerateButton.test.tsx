import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { GenerateButton } from "./GenerateButton";

describe("GenerateButton", () => {
  it("should render the generate button", () => {
    render(<GenerateButton onGenerate={vi.fn()} isGenerating={false} />);
    expect(screen.getByRole("button", { name: /generate & download zip/i })).toBeInTheDocument();
  });

  it("should call onGenerate when clicked", async () => {
    const onGenerate = vi.fn();
    render(<GenerateButton onGenerate={onGenerate} isGenerating={false} />);

    await userEvent.click(screen.getByRole("button"));
    expect(onGenerate).toHaveBeenCalledOnce();
  });

  it("should show generating state and be disabled", () => {
    render(<GenerateButton onGenerate={vi.fn()} isGenerating />);

    const button = screen.getByRole("button", { name: /generating/i });
    expect(button).toBeDisabled();
  });
});
