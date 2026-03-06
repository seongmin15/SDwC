import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { Rfc7807Error } from "@/types/api";

import { ErrorDisplay } from "./ErrorDisplay";

const mockError: Rfc7807Error = {
  type: "https://sdwc.dev/errors/rendering-failed",
  title: "Rendering Failed",
  status: 500,
  detail: "Template rendering exceeded 30s timeout",
  instance: "/api/v1/generate",
};

describe("ErrorDisplay", () => {
  it("should display the error title", () => {
    render(<ErrorDisplay error={mockError} onReset={vi.fn()} />);
    expect(screen.getByText("Rendering Failed")).toBeInTheDocument();
  });

  it("should display the error detail", () => {
    render(<ErrorDisplay error={mockError} onReset={vi.fn()} />);
    expect(screen.getByText("Template rendering exceeded 30s timeout")).toBeInTheDocument();
  });

  it("should display status and instance", () => {
    render(<ErrorDisplay error={mockError} onReset={vi.fn()} />);
    expect(screen.getByText(/status 500/i)).toBeInTheDocument();
    expect(screen.getByText(/\/api\/v1\/generate/i)).toBeInTheDocument();
  });

  it("should call onReset when start over is clicked", async () => {
    const onReset = vi.fn();
    render(<ErrorDisplay error={mockError} onReset={onReset} />);

    await userEvent.click(screen.getByRole("button", { name: /start over/i }));
    expect(onReset).toHaveBeenCalledOnce();
  });

  it("should hide status line when status is 0", () => {
    const networkError: Rfc7807Error = {
      ...mockError,
      status: 0,
      title: "Network Error",
    };
    render(<ErrorDisplay error={networkError} onReset={vi.fn()} />);
    expect(screen.queryByText(/status 0/i)).not.toBeInTheDocument();
  });
});
