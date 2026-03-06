import { useState } from "react";

import type { PreviewResponse } from "@/types/api";

interface FileTreePreviewProps {
  preview: PreviewResponse;
}

export function FileTreePreview({ preview }: FileTreePreviewProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-900">Output Preview</h2>
        <span className="text-xs text-gray-500">{preview.file_count} files</span>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        {preview.services.map((svc) => (
          <span
            key={svc.name}
            className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
          >
            {svc.name}
            <span className="ml-1 text-blue-400">({svc.framework})</span>
          </span>
        ))}
      </div>
      <div className="rounded border border-gray-100 bg-gray-50 p-3 font-mono text-sm">
        <TreeNode name="" tree={preview.file_tree} isRoot />
      </div>
    </div>
  );
}

interface TreeNodeProps {
  name: string;
  tree: Record<string, unknown>;
  isRoot?: boolean;
}

function TreeNode({ name, tree, isRoot = false }: TreeNodeProps) {
  const entries = Object.entries(tree);
  const isFolder = entries.length > 0;
  const [isExpanded, setIsExpanded] = useState(true);

  if (isRoot) {
    return (
      <ul className="space-y-0.5">
        {entries.map(([childName, childTree]) => (
          <li key={childName}>
            <TreeNode name={childName} tree={childTree as Record<string, unknown>} />
          </li>
        ))}
      </ul>
    );
  }

  if (!isFolder) {
    return (
      <div className="flex items-center gap-1.5 py-0.5 pl-4 text-gray-700">
        <svg
          className="h-3.5 w-3.5 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        {name}
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center gap-1.5 rounded py-0.5 text-left text-gray-900 hover:bg-gray-100"
      >
        <svg
          className={`h-3 w-3 text-gray-500 transition-transform ${isExpanded ? "rotate-90" : ""}`}
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
            clipRule="evenodd"
          />
        </svg>
        <svg
          className="h-3.5 w-3.5 text-amber-500"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
        </svg>
        <span className="font-medium">{name}</span>
      </button>
      {isExpanded && (
        <ul className="ml-4 space-y-0.5 border-l border-gray-200 pl-2">
          {entries.map(([childName, childTree]) => (
            <li key={childName}>
              <TreeNode name={childName} tree={childTree as Record<string, unknown>} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
