import { useCallback, useRef, useState } from "react";

interface FileUploaderProps {
  onUpload: (file: File) => void;
  isDisabled?: boolean;
}

export function FileUploader({ onUpload, isDisabled = false }: FileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file || isDisabled) return;
      onUpload(file);
    },
    [onUpload, isDisabled],
  );

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    if (!isDisabled) setIsDragOver(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    handleFile(e.target.files?.[0]);
    // Reset so the same file can be re-uploaded
    if (inputRef.current) inputRef.current.value = "";
  }

  function handleClick() {
    if (!isDisabled) inputRef.current?.click();
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  }

  return (
    <div
      role="button"
      tabIndex={isDisabled ? -1 : 0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      aria-disabled={isDisabled}
      aria-label="Upload YAML file"
      className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
        isDisabled
          ? "cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400"
          : isDragOver
            ? "border-blue-500 bg-blue-50 text-blue-600"
            : "border-gray-300 bg-white text-gray-500 hover:border-gray-400 hover:bg-gray-50"
      }`}
    >
      <svg
        className="mb-3 h-10 w-10"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      <p className="mb-1 text-sm font-medium">
        {isDragOver ? "Drop your file here" : "Drag & drop your intake_data.yaml"}
      </p>
      <p className="text-xs">or click to browse</p>
      <input
        ref={inputRef}
        type="file"
        accept=".yaml,.yml"
        onChange={handleChange}
        className="hidden"
        aria-hidden="true"
        tabIndex={-1}
      />
    </div>
  );
}
