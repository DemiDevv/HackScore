export type UserRole = "participant" | "jury" | "organizer";

export type User = {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  avatar_url: string | null;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type HackathonStatus = "draft" | "registration" | "in_progress" | "judging" | "finished";

export type Hackathon = {
  id: string;
  title: string;
  description: string | null;
  status: HackathonStatus;
  start_date: string | null;
  end_date: string | null;
  created_by: string;
  created_at: string;
};

export type TeamMember = {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_captain: boolean;
};

export type Team = {
  id: string;
  name: string;
  hackathon_id: string;
  created_at: string;
  members: TeamMember[];
};

export type CheckType = "code" | "documentation" | "presentation" | "screencast";
export type CheckStatus = "pending" | "running" | "completed" | "failed";
export type SubmissionStatus = "draft" | "submitted" | "checking" | "checked";

export type CheckResult = {
  id: string;
  submission_id: string;
  check_type: CheckType;
  status: CheckStatus;
  score: number | null;
  report: Record<string, unknown> | null;
  started_at: string | null;
  completed_at: string | null;
};

export type Submission = {
  id: string;
  team_id: string;
  hackathon_id: string;
  repo_url: string | null;
  repo_archive: string | null;
  doc_file: string | null;
  presentation: string | null;
  screencast_file: string | null;
  screencast_url: string | null;
  status: SubmissionStatus;
  submitted_at: string | null;
  updated_at: string;
  check_results: CheckResult[];
};

export type AlgoLanguage = "python" | "cpp" | "java";
export type AlgoVerdict = "pending" | "OK" | "WA" | "TL" | "ML" | "RE" | "CE";

export type AlgoTest = {
  id: string;
  task_id: string;
  input_data: string;
  expected_output: string;
  is_sample: boolean;
  order_index: number | null;
};

export type AlgoTask = {
  id: string;
  hackathon_id: string;
  title: string;
  description: string;
  time_limit_ms: number;
  memory_limit_mb: number;
  created_by: string;
  tests: AlgoTest[];
};

export type AlgoSubmission = {
  id: string;
  task_id: string;
  user_id: string;
  team_id: string;
  language: AlgoLanguage;
  source_code: string;
  verdict: AlgoVerdict;
  execution_time: number | null;
  memory_used: number | null;
  test_passed: number;
  test_total: number;
  error_message: string | null;
  submitted_at: string;
};

export type Criterion = {
  id: string;
  hackathon_id: string;
  name: string;
  description: string | null;
  weight: number;
  max_score: number;
  is_auto: boolean;
  order_index: number | null;
};

export type ExpertScore = {
  id: string;
  submission_id: string;
  criterion_id: string;
  jury_id: string;
  score: number;
  comment: string | null;
  created_at: string;
};

export type ReviewSubmissionSummary = {
  submission_id: string;
  team_id: string;
  team_name: string;
  status: SubmissionStatus;
  auto_score: number | null;
  my_score: number | null;
  checks: Array<{
    check_type: CheckType;
    status: CheckStatus;
    score: number | null;
  }>;
};

export type AIReview = {
  model_name: string;
  model_version: string;
  score: number;
  confidence: number;
  verdict: "strong_candidate" | "promising" | "needs_manual_review" | "high_risk" | string;
  summary: string;
  strengths: string[];
  risks: string[];
  missing_parts: string[];
  jury_questions: string[];
  feature_weights: Record<string, number>;
  signals: Record<string, number>;
};

export type ReviewDetail = ReviewSubmissionSummary & {
  repo_url: string | null;
  repo_archive: string | null;
  doc_file: string | null;
  presentation: string | null;
  screencast_file: string | null;
  screencast_url: string | null;
  ai_review: AIReview;
  my_scores: ExpertScore[];
};

export type LeaderboardRow = {
  rank: number;
  team_id: string;
  team_name: string;
  auto_scores: Record<string, number | null>;
  expert_scores: Array<{
    criterion: string;
    avg_score: number | null;
    jury_count: number;
  }>;
  total_score: number;
};
