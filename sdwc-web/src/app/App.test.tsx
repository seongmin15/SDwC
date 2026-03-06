import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { useIntakeStore } from "@/stores/useIntakeStore";

import { App } from "./App";

afterEach(() => {
  useIntakeStore.getState().reset();
});

describe("App", () => {
  it("should render the SDwC heading", () => {
    render(<App />);
    expect(screen.getByText("SDwC")).toBeInTheDocument();
  });

  it("should render the template download button", () => {
    render(<App />);
    expect(screen.getByRole("link", { name: /download template/i })).toBeInTheDocument();
  });

  it("should render the file uploader", () => {
    render(<App />);
    expect(screen.getByRole("button", { name: /upload yaml file/i })).toBeInTheDocument();
  });
});
