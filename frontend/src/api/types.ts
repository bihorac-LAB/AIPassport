/** Wire types mirroring the backend Pydantic response models. */

export type Track = 'clinical' | 'basic';
export type UserRole = 'learner' | 'instructor' | 'admin';
export type ProgressStatus = 'not_started' | 'in_progress' | 'completed';
export type PageKind = 'explore' | 'apply';

export type QuestionType =
  | 'single_choice'
  | 'multi_choice'
  | 'free_text'
  | 'numeric'
  | 'likert'
  | 'slider_estimate'
  | 'structured';

export type User = {
  id: string;
  email: string;
  display_name: string;
  role: UserRole;
  track_pref: Track;
  email_verified: boolean;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  csrf_token: string;
  user: User;
};

export type PageProgress = {
  page_key: string;
  module_key: string;
  status: ProgressStatus;
  sections_completed: string[];
  last_section_id: string | null;
  seconds_spent: number;
  visit_count: number;
  completed_at: string | null;
  updated_at: string;
};

export type QuestionWire = {
  key: string;
  position: number;
  type: QuestionType;
  prompt: string;
  spec: Record<string, unknown>;
  version: number;
  is_graded: boolean;
};

export type ModulePageWire = {
  key: string;
  module_key: string;
  position: number;
  slug: string;
  title: string;
  kicker: string;
  kind: PageKind;
  objectives: string[];
  required_sections: string[];
  estimated_minutes: number;
  content_version: number;
  questions?: QuestionWire[];
  progress?: PageProgress | null;
};

export type ModuleWire = {
  key: string;
  position: number;
  title: string;
  subtitle: string;
  summary: string;
  accent: string;
  content_version: number;
  pages: ModulePageWire[];
};

export type ModuleSummaryWire = ModuleWire & {
  pages_completed: number;
  pages_total: number;
  status: ProgressStatus;
};

export type ResponseRecord = {
  id: string;
  question_key: string;
  question_version: number;
  module_key: string;
  page_key: string;
  attempt_no: number;
  answer: Record<string, unknown>;
  is_final: boolean;
  is_correct: boolean | null;
  score: number | null;
  created_at: string;
};

export type ResponseResult = {
  response: ResponseRecord;
  feedback: string | null;
  explanation: string | null;
  correct_answer: unknown;
};

export type ActivityResultRecord = {
  id: string;
  activity_key: string;
  module_key: string;
  page_key: string;
  attempt_no: number;
  payload: Record<string, unknown>;
  created_at: string;
};

export type ProgressOverview = {
  pages: PageProgress[];
  modules_completed: string[];
  total_seconds: number;
  resume: { module_key: string; page_key: string; section_id: string | null } | null;
};

export type LearningSession = {
  id: string;
  started_at: string;
  last_seen_at: string;
  ended_at: string | null;
  is_embedded: boolean;
};

export type AiUsage = {
  model: string;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  latency_ms: number | null;
};

export type AiChatResponse = {
  content: string;
  conversation_id: string;
  usage: AiUsage;
};

export type AiActivityResponse = {
  prompt_key: string;
  content: string | null;
  structured: Record<string, unknown> | null;
  conversation_id: string;
  usage: AiUsage;
};

export type FactOrFictionVerdict = {
  verdict: string | null;
  summary: string | null;
  correction: string | null;
  examples: string[] | null;
  limitations: string[] | null;
  concepts: string[] | null;
  datasets: string[] | null;
  research_directions: string[] | null;
  citations: string[] | null;
};
