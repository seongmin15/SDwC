/** RFC 7807 Problem Details error item. */
export interface Rfc7807Error {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
}

/** POST /api/v1/validate response. */
export interface ValidationResponse {
  valid: boolean;
  errors: Rfc7807Error[];
  warnings: Rfc7807Error[];
}

/** Service info from POST /api/v1/preview response. */
export interface ServiceInfo {
  name: string;
  type: string;
  framework: string;
}

/** POST /api/v1/preview response. */
export interface PreviewResponse {
  file_tree: Record<string, unknown>;
  file_count: number;
  services: ServiceInfo[];
}
