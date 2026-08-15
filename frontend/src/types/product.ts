export type AppMode = "landing" | "spec-flow" | "github-flow" | "demo" | "workspace";

export interface RepoDiscoveryState {
  repository: string;
  branch: string;
  commit: string;
  language: string;
  filesCount: number;
  ready: boolean;
}

export type PipelineStage =
  | "idle"
  | "spec_loaded"
  | "extracting_requirements"
  | "repo_discovered"
  | "ast_analyzing"
  | "trace_matching"
  | "calculating_compliance"
  | "completed";