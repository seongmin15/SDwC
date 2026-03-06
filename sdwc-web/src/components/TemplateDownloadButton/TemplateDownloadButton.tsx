interface TemplateDownloadButtonProps {
  isDisabled?: boolean;
}

export function TemplateDownloadButton({ isDisabled = false }: TemplateDownloadButtonProps) {
  return (
    <a
      href="/api/v1/template"
      download="intake_template.yaml"
      className={`inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 ${isDisabled ? "pointer-events-none opacity-50" : ""}`}
      aria-disabled={isDisabled}
    >
      <svg
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
      Download Template
    </a>
  );
}
