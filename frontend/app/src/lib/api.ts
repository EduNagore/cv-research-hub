import type {
  ResearchItem, 
  DashboardStats, 
  Category, 
  Tag, 
  Trend, 
  Comparison, 
  DecisionRequest, 
  DecisionResponse,
  UserItem,
  IngestionSourceStatus,
  GeminiDiscoveryStatus,
  FilterOptions,
  CategoryFeedResponse,
} from '@/types';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000/api/v1';

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Dashboard
export async function getDashboardStats(date?: string): Promise<DashboardStats> {
  const params = date ? `?date=${date}` : '';
  return fetchApi<DashboardStats>(`/dashboard/stats${params}`);
}

// Research Items
export async function getResearchItems(filters: FilterOptions = {}): Promise<{
  items: ResearchItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}> {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        params.append(key, value.join(','));
      } else {
        params.append(key, String(value));
      }
    }
  });
  
  const queryString = params.toString();
  return fetchApi(`/items${queryString ? `?${queryString}` : ''}`);
}

export async function getResearchItem(slug: string): Promise<ResearchItem> {
  return fetchApi<ResearchItem>(`/items/${slug}`);
}

export async function searchResearchItems(
  query: string, 
  page: number = 1, 
  pageSize: number = 20
): Promise<{
  items: ResearchItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}> {
  return fetchApi(`/items/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`);
}

// Categories
export async function getCategories(): Promise<Category[]> {
  return fetchApi<Category[]>('/categories');
}

export async function getCategory(slug: string): Promise<Category> {
  return fetchApi<Category>(`/categories/${slug}`);
}

export async function getCategoryFeed(limitPerCategory: number = 6): Promise<CategoryFeedResponse> {
  return fetchApi<CategoryFeedResponse>(`/categories/feed?limit_per_category=${limitPerCategory}`);
}

// Tags
export async function getTags(search?: string, limit: number = 100): Promise<Tag[]> {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  params.append('limit', String(limit));
  return fetchApi<Tag[]>(`/tags?${params.toString()}`);
}

export async function getPopularTags(limit: number = 20): Promise<{ tags: Tag[] }> {
  return fetchApi(`/tags/popular?limit=${limit}`);
}

// Trends
export async function getTrends(
  trendType?: string, 
  period: string = 'weekly', 
  limit: number = 20
): Promise<Trend[]> {
  const params = new URLSearchParams();
  if (trendType) params.append('trend_type', trendType);
  params.append('period', period);
  params.append('limit', String(limit));
  return fetchApi<Trend[]>(`/trends?${params.toString()}`);
}

export async function getTrendStatistics(period: string = 'weekly'): Promise<{
  top_architectures: Trend[];
  top_topics: Trend[];
  top_methods: Trend[];
  top_datasets: Trend[];
  emerging_keywords: Trend[];
  period: string;
}> {
  return fetchApi(`/trends/statistics?period=${period}`);
}

// Comparisons
export async function getComparisons(filters: {
  task?: string;
  architecture_family?: string;
  maturity_level?: string;
  computational_cost?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<{
  items: Comparison[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}> {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value));
    }
  });
  
  return fetchApi(`/comparisons?${params.toString()}`);
}

export async function getComparison(slug: string): Promise<Comparison> {
  return fetchApi<Comparison>(`/comparisons/${slug}`);
}

export async function getComparisonTasks(): Promise<{ tasks: string[] }> {
  return fetchApi('/comparisons/tasks');
}

export async function getComparisonsByTask(task: string): Promise<{
  task: string;
  comparisons: Comparison[];
}> {
  return fetchApi(`/comparisons/by-task/${encodeURIComponent(task)}`);
}

// Decision Support
export async function getDecisionSupport(request: DecisionRequest): Promise<DecisionResponse> {
  return fetchApi<DecisionResponse>('/decision-support/recommend', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function getSupportedTasks(): Promise<{
  tasks: string[];
  image_types: string[];
  dataset_sizes: string[];
  annotation_amounts: string[];
}> {
  return fetchApi('/decision-support/tasks');
}

// User Items (Favorites, Bookmarks)
export async function getFavorites(): Promise<{ items: UserItem[] }> {
  return fetchApi('/user-items/favorites');
}

export async function getBookmarks(): Promise<{ items: UserItem[] }> {
  return fetchApi('/user-items/bookmarks');
}

export async function getReviewLater(): Promise<{ items: UserItem[] }> {
  return fetchApi('/user-items/review-later');
}

export async function toggleFavorite(itemId: number): Promise<{ success: boolean; is_favorite: boolean }> {
  return fetchApi(`/user-items/${itemId}/favorite`, { method: 'POST' });
}

export async function toggleBookmark(itemId: number): Promise<{ success: boolean; is_bookmarked: boolean }> {
  return fetchApi(`/user-items/${itemId}/bookmark`, { method: 'POST' });
}

export async function updateItemStatus(
  itemId: number, 
  status: string
): Promise<{ success: boolean; status: string }> {
  return fetchApi(`/user-items/${itemId}/status?status=${status}`, { method: 'POST' });
}

export async function updateItemNotes(itemId: number, notes: string): Promise<{ success: boolean; notes: string }> {
  return fetchApi(`/user-items/${itemId}/notes?notes=${encodeURIComponent(notes)}`, { method: 'POST' });
}

// Ingestion (Admin)
export async function triggerIngestion(source?: string): Promise<{
  success: boolean;
  message: string;
  timestamp: string;
}> {
  const params = new URLSearchParams();
  if (source) params.append('source', source);
  const query = params.toString();
  return fetchApi(`/ingestion/trigger${query ? `?${query}` : ''}`, { method: 'POST' });
}

export async function triggerCategoryIngestion(source: string, categorySlug: string): Promise<{
  success: boolean;
  message: string;
  timestamp: string;
}> {
  const params = new URLSearchParams();
  params.append('source', source);
  params.append('category_slug', categorySlug);
  return fetchApi(`/ingestion/trigger?${params.toString()}`, { method: 'POST' });
}

export async function getIngestionStatus(): Promise<{
  sources: Record<string, IngestionSourceStatus>;
  gemini_discovery: GeminiDiscoveryStatus;
  last_check: string;
}> {
  return fetchApi('/ingestion/status');
}
