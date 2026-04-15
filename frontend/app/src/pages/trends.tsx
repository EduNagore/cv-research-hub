import { useQuery } from '@tanstack/react-query';
import { TrendingUp, BarChart3, Zap, Layers, Tag } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { getTrendStatistics, getTrends } from '@/lib/api';
import type { Trend } from '@/types';

function TrendCard({ trend }: { trend: Trend }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-medium">{trend.name}</h4>
            <p className="text-sm text-muted-foreground mt-1">
              {trend.description}
            </p>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold">{trend.frequency}</div>
            <div className="text-xs text-muted-foreground">mentions</div>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-3">
          <Badge variant="outline">Score: {trend.popularity_score.toFixed(1)}</Badge>
          {trend.growth_rate !== undefined && trend.growth_rate > 0 && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              +{(trend.growth_rate * 100).toFixed(0)}%
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function TrendSection({ 
  title, 
  icon: Icon, 
  trends, 
  isLoading 
}: { 
  title: string; 
  icon: React.ElementType;
  trends?: Trend[];
  isLoading: boolean;
}) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <Icon className="h-5 w-5 text-primary" />
        {title}
      </h3>
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : trends?.length === 0 ? (
        <p className="text-muted-foreground">No trends found</p>
      ) : (
        <div className="space-y-3">
          {trends?.slice(0, 10).map((trend) => (
            <TrendCard key={trend.id} trend={trend} />
          ))}
        </div>
      )}
    </div>
  );
}

export function Trends() {
  const period = 'weekly';

  const { data: statistics, isLoading: statsLoading } = useQuery({
    queryKey: ['trend-statistics', period],
    queryFn: () => getTrendStatistics(period),
  });

  const { data: architectureTrends } = useQuery({
    queryKey: ['trends', 'architecture', period],
    queryFn: () => getTrends('architecture', period),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Trends</h1>
        <p className="text-muted-foreground">
          Discover emerging topics and patterns in computer vision research
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="architectures">Architectures</TabsTrigger>
          <TabsTrigger value="topics">Topics</TabsTrigger>
          <TabsTrigger value="methods">Methods</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <TrendSection
              title="Top Architectures"
              icon={Layers}
              trends={statistics?.top_architectures}
              isLoading={statsLoading}
            />
            <TrendSection
              title="Top Topics"
              icon={Tag}
              trends={statistics?.top_topics}
              isLoading={statsLoading}
            />
            <TrendSection
              title="Top Methods"
              icon={Zap}
              trends={statistics?.top_methods}
              isLoading={statsLoading}
            />
            <TrendSection
              title="Emerging Keywords"
              icon={BarChart3}
              trends={statistics?.emerging_keywords}
              isLoading={statsLoading}
            />
          </div>
        </TabsContent>

        <TabsContent value="architectures" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            {architectureTrends?.map((trend) => (
              <TrendCard key={trend.id} trend={trend} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="topics" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            {statistics?.top_topics.map((trend) => (
              <TrendCard key={trend.id} trend={trend} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="methods" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            {statistics?.top_methods.map((trend) => (
              <TrendCard key={trend.id} trend={trend} />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
