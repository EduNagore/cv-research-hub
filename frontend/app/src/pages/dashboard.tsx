import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Code, 
  TrendingUp, 
  Star, 
  Zap,
  Calendar,
  ArrowRight,
  RefreshCcw,
  Database,
  Clock
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { getDashboardStats, getIngestionStatus, triggerCategoryIngestion, triggerIngestion } from '@/lib/api';
import { toast } from 'sonner';
import type { ResearchItemBrief } from '@/types';

function StatCard({ 
  title, 
  value, 
  description, 
  icon: Icon 
}: { 
  title: string; 
  value: number; 
  description: string;
  icon: React.ElementType;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString()}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

function ItemCard({ item }: { item: ResearchItemBrief }) {
  return (
    <Card className="hover:bg-muted/50 transition-colors">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <Link 
              to={`/items/${item.slug}`}
              className="font-medium hover:underline line-clamp-2"
            >
              {item.title}
            </Link>
            {item.short_summary && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {item.short_summary}
              </p>
            )}
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <Badge variant="secondary" className="text-xs">
                {item.source}
              </Badge>
              {item.github_stars !== undefined && item.github_stars > 0 && (
                <Badge variant="outline" className="text-xs flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  {item.github_stars.toLocaleString()}
                </Badge>
              )}
              <span className="text-xs text-muted-foreground">
                Score: {item.relevance_score.toFixed(1)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function Section({ 
  title, 
  items, 
  viewAllLink 
}: { 
  title: string; 
  items: ResearchItemBrief[]; 
  viewAllLink?: string;
}) {
  if (items.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{title}</h3>
        {viewAllLink && (
          <Button variant="ghost" size="sm" asChild>
            <Link to={viewAllLink} className="flex items-center gap-1">
              View All <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        )}
      </div>
      <div className="grid gap-3">
        {items.slice(0, 5).map((item) => (
          <ItemCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}

export function Dashboard() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => getDashboardStats(),
  });
  const { data: ingestionStatus, isLoading: ingestionLoading } = useQuery({
    queryKey: ['ingestion-status'],
    queryFn: getIngestionStatus,
    refetchInterval: 30000,
  });
  const refreshMutation = useMutation({
    mutationFn: (source?: string) => triggerIngestion(source),
    onSuccess: (result) => {
      toast.success(result.message);
      queryClient.invalidateQueries({ queryKey: ['ingestion-status'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to trigger refresh');
    },
  });
  const refreshCategoryMutation = useMutation({
    mutationFn: (categorySlug: string) => triggerCategoryIngestion('gemini', categorySlug),
    onSuccess: (result) => {
      toast.success(result.message);
      queryClient.invalidateQueries({ queryKey: ['ingestion-status'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      queryClient.invalidateQueries({ queryKey: ['category-feed'] });
      queryClient.invalidateQueries({ queryKey: ['research-items'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to refresh category');
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Failed to load dashboard data</p>
        </div>
      </div>
    );
  }

  const { daily_summary, total_items, items_last_7_days, items_last_30_days } = data;
  const geminiStatus = ingestionStatus?.gemini_discovery;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Daily updates in image processing, computer vision, and generative image AI
          </p>
          <p className="text-sm text-muted-foreground mt-2 flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Last ingestion: {data.latest_ingestion_at ? new Date(data.latest_ingestion_at).toLocaleString() : 'Not yet ingested'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={() => refreshMutation.mutate(undefined)}
            disabled={refreshMutation.isPending}
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Refresh Gemini feeds
          </Button>
          <Button
            variant="ghost"
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
              queryClient.invalidateQueries({ queryKey: ['ingestion-status'] });
            }}
          >
            Reload dashboard
          </Button>
        </div>
      </div>

      {/* Daily Summary */}
      <Card className="bg-gradient-to-r from-primary/10 to-primary/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            Today's Summary
          </CardTitle>
          <CardDescription>
            {new Date(daily_summary.date).toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-5">
            <div className="text-center">
              <div className="text-3xl font-bold">{daily_summary.total_new_items}</div>
              <div className="text-sm text-muted-foreground">New Items</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{daily_summary.top_papers_count}</div>
              <div className="text-sm text-muted-foreground">Papers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{daily_summary.new_models_count}</div>
              <div className="text-sm text-muted-foreground">Models</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{daily_summary.new_datasets_count}</div>
              <div className="text-sm text-muted-foreground">Datasets</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{daily_summary.new_benchmarks_count}</div>
              <div className="text-sm text-muted-foreground">Benchmarks</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-primary" />
              Feed Refresh Status
            </CardTitle>
            <CardDescription>
              Check whether your Gemini-driven category feeds are populated and trigger refreshes when needed.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {ingestionLoading ? (
              <div className="grid gap-3 md:grid-cols-3">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-28" />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <Card className="border-dashed">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">Gemini Discovery</h4>
                      <Badge variant={geminiStatus?.configured ? 'secondary' : 'outline'}>
                        {geminiStatus?.configured ? 'Ready' : 'Needs setup'}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <p>{(geminiStatus?.total_items || 0).toLocaleString()} Gemini items indexed</p>
                      <p>Model: {geminiStatus?.model || 'Not configured'}</p>
                      <p>
                        Last run:{' '}
                        {geminiStatus?.latest_ingestion
                          ? new Date(geminiStatus.latest_ingestion).toLocaleString()
                          : 'Never'}
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full"
                      onClick={() => refreshMutation.mutate('gemini')}
                      disabled={refreshMutation.isPending || !geminiStatus?.configured}
                    >
                      Refresh Gemini
                    </Button>
                  </CardContent>
                </Card>

                <div className="grid gap-3 md:grid-cols-3">
                  {(geminiStatus?.categories || []).map((category) => (
                    <Card key={category.slug} className="border-dashed">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">{category.name}</h4>
                        <Badge variant={category.item_count > 0 ? 'secondary' : 'outline'}>
                          {category.item_count > 0 ? 'Has items' : 'Empty'}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <p>{category.item_count.toLocaleString()} items indexed</p>
                        <p>
                          Last run:{' '}
                          {category.latest_ingestion
                            ? new Date(category.latest_ingestion).toLocaleString()
                            : 'Never'}
                        </p>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full"
                        onClick={() => refreshCategoryMutation.mutate(category.slug)}
                        disabled={refreshCategoryMutation.isPending || !geminiStatus?.configured}
                      >
                        Refresh {category.name}
                      </Button>
                    </CardContent>
                  </Card>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Routine</CardTitle>
            <CardDescription>Suggested flow for checking the site each day.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>1. Refresh all sources to pull the latest arXiv, Papers with Code, and GitHub items.</p>
            <p>2. Start with “Top 10 Today” for the strongest overall signal.</p>
            <p>3. Use “Most Promising Papers” for research and “Useful Repositories” for implementation ideas.</p>
            <p>4. Bookmark or favorite items you want to revisit in your library.</p>
          </CardContent>
        </Card>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          title="Total Items" 
          value={total_items} 
          description="All time research items"
          icon={FileText}
        />
        <StatCard 
          title="Last 7 Days" 
          value={items_last_7_days} 
          description="Recent additions"
          icon={TrendingUp}
        />
        <StatCard 
          title="Last 30 Days" 
          value={items_last_30_days} 
          description="Monthly activity"
          icon={Calendar}
        />
        <StatCard 
          title="Repositories" 
          value={data.total_repositories} 
          description="With code available"
          icon={Code}
        />
      </div>

      {/* Content Sections */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Section 
          title="Top 10 Today" 
          items={data.top_10_today}
          viewAllLink="/items"
        />
        <Section 
          title="Most Promising Papers" 
          items={data.most_promising_papers}
          viewAllLink="/items?contribution_type=paper"
        />
        <Section 
          title="Useful Repositories" 
          items={data.useful_repositories}
          viewAllLink="/items?has_github=true"
        />
        <Section 
          title="New Architectures" 
          items={data.new_architectures}
          viewAllLink="/items?contribution_type=model"
        />
        <Section 
          title="Worth Looking At" 
          items={data.worth_looking_at}
        />
        <Section 
          title="Benchmarks & Datasets" 
          items={data.new_benchmarks_datasets}
        />
      </div>
    </div>
  );
}
