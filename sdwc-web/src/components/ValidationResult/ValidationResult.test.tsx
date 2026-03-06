import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ValidationResponse } from "@/types/api";

import { ValidationResult } from "./ValidationResult";

const validResult: ValidationResponse = {
  valid: true,
  errors: [],
  warnings: [],
};

const errorResult: ValidationResponse = {
  valid: false,
  errors: [
    {
      type: "https://sdwc.dev/errors/validation-failed",
      title: "Validation Failed",
      status: 422,
      detail: "project.name: Field required",
      instance: "/api/v1/validate",
    },
    {
      type: "https://sdwc.dev/errors/validation-failed",
      title: "Validation Failed",
      status: 422,
      detail: "services: Field required",
      instance: "/api/v1/validate",
    },
  ],
  warnings: [],
};

describe("ValidationResult", () => {
  it("should display success when valid", () => {
    render(<ValidationResult result={validResult} onReset={vi.fn()} />);

    expect(screen.getByText(/validation passed/i)).toBeInTheDocument();
  });

  it("should display error count when invalid", () => {
    render(<ValidationResult result={errorResult} onReset={vi.fn()} />);

    expect(screen.getByText(/validation failed \(2 errors\)/i)).toBeInTheDocument();
  });

  it("should display error details", () => {
    render(<ValidationResult result={errorResult} onReset={vi.fn()} />);

    expect(screen.getByText("project.name: Field required")).toBeInTheDocument();
    expect(screen.getByText("services: Field required")).toBeInTheDocument();
  });

  it("should call onReset when try again is clicked", async () => {
    const onReset = vi.fn();
    render(<ValidationResult result={errorResult} onReset={onReset} />);

    await userEvent.click(screen.getByRole("button", { name: /try again/i }));

    expect(onReset).toHaveBeenCalledOnce();
  });

  it("should display warnings when present", () => {
    const resultWithWarnings: ValidationResponse = {
      valid: false,
      errors: [
        {
          type: "t",
          title: "t",
          status: 422,
          detail: "some error",
          instance: "/api/v1/validate",
        },
      ],
      warnings: [
        {
          type: "t",
          title: "t",
          status: 422,
          detail: "some warning",
          instance: "/api/v1/validate",
        },
      ],
    };

    render(<ValidationResult result={resultWithWarnings} onReset={vi.fn()} />);

    expect(screen.getByText("some warning")).toBeInTheDocument();
    expect(screen.getByText(/warnings \(1\)/i)).toBeInTheDocument();
  });
});
