export interface ResearchItem {
  id: number;
  title: string;
  slug: string;
  source: string;
  source_id?: string;
  source_url?: string;
  published_date: string;
  authors?: string[];
  abstract?: string;
  short_summary?: string;
  full_summary?: string;
  why_it_matters?: string;
  problem_solved?: string;
  contribution_description?: string;
  use_cases?: string[];
  paper_url?: string;
  abstract_url?: string;
  code_url?: string;
  github_url?: string;
  project_page_url?: string;
  demo_url?: string;
  contribution_type: string;
  modality?: string;
  architecture_family?: string;
  model_name?: string;
  status_label: string;
  is_official_code: boolean;
  is_unofficial_reimplementation: boolean;
  github_stars?: number;
  github_forks?: number;
  github_last_updated?: string;
  github_language?: string;
  relevance_score: number;
  recency_score: number;
  code_availability_score: number;
  source_quality_score: number;
  impact_score: number;
  clarity_score: number;
  venue?: string;
  venue_type?: string;
  categories: Category[];
  tags: Tag[];
  is_favorite?: boolean;
  is_bookmarked?: boolean;
  user_status?: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  item_count: number;
}

export interface CategoryFeedGroup {
  category: Category;
  items: ResearchItem[];
}

export interface CategoryFeedResponse {
  generated_at: string;
  categories: CategoryFeedGroup[];
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
  color?: string;
  item_count: number;
}

export interface DashboardStats {
  daily_summary: DailySummary;
  top_10_today: ResearchItemBrief[];
  most_promising_papers: ResearchItemBrief[];
  useful_repositories: ResearchItemBrief[];
  new_architectures: ResearchItemBrief[];
  new_benchmarks_datasets: ResearchItemBrief[];
  worth_looking_at: ResearchItemBrief[];
  total_items: number;
  total_papers: number;
  total_models: number;
  total_datasets: number;
  total_repositories: number;
  items_last_7_days: number;
  items_last_30_days: number;
  latest_ingestion_at?: string;
  sources_breakdown: Record<string, number>;
}

export interface DailySummary {
  date: string;
  total_new_items: number;
  top_papers_count: number;
  new_models_count: number;
  new_datasets_count: number;
  new_benchmarks_count: number;
  category_breakdown: CategoryCount[];
}

export interface CategoryCount {
  name: string;
  slug: string;
  count: number;
}

export interface ResearchItemBrief {
  id: number;
  title: string;
  slug: string;
  source: string;
  published_date: string;
  relevance_score: number;
  short_summary?: string;
  github_stars?: number;
  categories: string[];
  tags: string[];
}

export interface Trend {
  id: number;
  name: string;
  slug: string;
  trend_type: string;
  period: string;
  period_start: string;
  period_end: string;
  frequency: number;
  growth_rate?: number;
  popularity_score: number;
  related_papers_count: number;
  related_models_count: number;
  description?: string;
}

export interface Comparison {
  id: number;
  model_name: string;
  slug: string;
  task: string;
  description?: string;
  strengths?: string[];
  limitations?: string[];
  architecture_family?: string;
  computational_cost?: string;
  maturity_level?: string;
  performance_metrics?: Record<string, any>;
  best_use_cases?: string[];
  not_recommended_for?: string[];
  dataset_size_requirements?: string;
  annotation_requirements?: string;
  hardware_requirements?: string;
  paper_url?: string;
  code_url?: string;
  documentation_url?: string;
  view_count: number;
}

export interface DecisionRequest {
  task_type: string;
  dataset_size: string;
  annotation_amount: string;
  image_type: string;
  dimensionality: string;
  need_interpretability: boolean;
  real_time_required: boolean;
  accuracy_priority: string;
  problem_type: string;
  compute_budget?: string;
  memory_constraints?: string;
}

export interface Recommendation {
  approach_family: string;
  description: string;
  recommended_models: string[];
  relevant_papers: any[];
  strengths: string[];
  limitations: string[];
  practical_notes: string;
  suitability_score: number;
}

export interface DecisionResponse {
  task_summary: string;
  primary_recommendations: Recommendation[];
  alternative_approaches: Recommendation[];
  data_preparation_tips: string[];
  training_considerations: string[];
  evaluation_metrics: string[];
  suggested_reading: any[];
  useful_repositories: any[];
  trade_offs_summary: string;
}

export interface UserItem {
  id: number;
  research_item_id: number;
  status: string;
  is_favorite: boolean;
  is_bookmarked: boolean;
  notes?: string;
  rating?: number;
  first_seen_at: string;
  last_viewed_at?: string;
  read_at?: string;
  research_item_title?: string;
  research_item_published_date?: string;
  research_item_relevance_score?: number;
}

export interface IngestionSourceStatus {
  latest_ingestion?: string;
  total_items: number;
  configured: boolean;
}

export interface GeminiCategoryStatus {
  name: string;
  slug: string;
  item_count: number;
  latest_ingestion?: string | null;
}

export interface GeminiDiscoveryStatus {
  configured: boolean;
  model: string;
  results_per_category: number;
  lookback_days: number;
  latest_ingestion?: string | null;
  total_items: number;
  categories: GeminiCategoryStatus[];
}

export interface FilterOptions {
  search?: string;
  category?: string;
  source?: string;
  contribution_type?: string;
  status_label?: string;
  modality?: string;
  architecture_family?: string;
  has_code?: boolean;
  has_github?: boolean;
  date_from?: string;
  date_to?: string;
  min_score?: number;
  max_score?: number;
  tags?: string[];
  keywords?: string[];
  sort_by?: string;
  sort_order?: string;
  page?: number;
  page_size?: number;
}
