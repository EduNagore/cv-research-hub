import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  CheckCircle, 
  XCircle, 
  Cpu, 
  ArrowRight
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { getComparisons, getComparisonTasks, getComparisonsByTask } from '@/lib/api';
import type { Comparison } from '@/types';

type ComparisonListResponse = Awaited<ReturnType<typeof getComparisons>>;
type ComparisonsByTaskResponse = Awaited<ReturnType<typeof getComparisonsByTask>>;
type ComparisonQueryResult = ComparisonListResponse | ComparisonsByTaskResponse;

function ComparisonCard({ comparison }: { comparison: Comparison }) {
  const maturityColors: Record<string, string> = {
    experimental: 'bg-red-100 text-red-800',
    research: 'bg-yellow-100 text-yellow-800',
    beta: 'bg-blue-100 text-blue-800',
    production: 'bg-green-100 text-green-800',
    mature: 'bg-purple-100 text-purple-800',
  };

  const costLabels: Record<string, string> = {
    very_low: 'Very Low',
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    very_high: 'Very High',
  };

  return (
    <Card className="hover:bg-muted/50 transition-colors">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{comparison.model_name}</CardTitle>
            <CardDescription>{comparison.description}</CardDescription>
          </div>
          {comparison.maturity_level && (
            <Badge className={maturityColors[comparison.maturity_level] || ''}>
              {comparison.maturity_level}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {comparison.architecture_family && (
            <Badge variant="outline">{comparison.architecture_family}</Badge>
          )}
          {comparison.computational_cost && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Cpu className="h-3 w-3" />
              {costLabels[comparison.computational_cost]}
            </Badge>
          )}
        </div>

        {comparison.strengths && comparison.strengths.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
              <CheckCircle className="h-4 w-4 text-green-600" />
              Strengths
            </h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              {comparison.strengths.slice(0, 3).map((strength, i) => (
                <li key={i}>{strength}</li>
              ))}
            </ul>
          </div>
        )}

        {comparison.limitations && comparison.limitations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
              <XCircle className="h-4 w-4 text-red-600" />
              Limitations
            </h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              {comparison.limitations.slice(0, 3).map((limitation, i) => (
                <li key={i}>{limitation}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <span className="text-sm text-muted-foreground">
            {comparison.view_count.toLocaleString()} views
          </span>
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/comparisons/${comparison.slug}`}>
              Details <ArrowRight className="h-4 w-4 ml-1" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function Comparisons() {
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  const { data: tasks } = useQuery({
    queryKey: ['comparison-tasks'],
    queryFn: getComparisonTasks,
  });

  const { data: comparisons, isLoading: comparisonsLoading } = useQuery<ComparisonQueryResult>({
    queryKey: ['comparisons', selectedTask],
    queryFn: () => selectedTask ? getComparisonsByTask(selectedTask) : getComparisons(),
  });

  const comparisonList: Comparison[] =
    !comparisons ? [] :
    selectedTask
      ? ('comparisons' in comparisons ? comparisons.comparisons : [])
      : ('items' in comparisons ? comparisons.items : []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Comparisons</h1>
        <p className="text-muted-foreground">
          Compare different approaches and models for computer vision tasks
        </p>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="flex flex-wrap h-auto">
          <TabsTrigger 
            value="all" 
            onClick={() => setSelectedTask(null)}
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
          >
            All
          </TabsTrigger>
          {tasks?.tasks.map((task) => (
            <TabsTrigger 
              key={task} 
              value={task}
              onClick={() => setSelectedTask(task)}
              className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              {task}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="all" className="space-y-6">
          {comparisonsLoading ? (
            <div className="grid gap-4 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-64" />
              ))}
            </div>
          ) : comparisonList?.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No comparisons found</p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {comparisonList?.map((comparison: Comparison) => (
                <ComparisonCard key={comparison.id} comparison={comparison} />
              ))}
            </div>
          )}
        </TabsContent>

        {tasks?.tasks.map((task) => (
          <TabsContent key={task} value={task} className="space-y-6">
            {comparisonsLoading ? (
              <div className="grid gap-4 md:grid-cols-2">
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-64" />
                ))}
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {comparisonList?.map((comparison: Comparison) => (
                  <ComparisonCard key={comparison.id} comparison={comparison} />
                ))}
              </div>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
