import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FolderOpen, ArrowRight, ExternalLink, Github, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { getCategoryFeed } from '@/lib/api';

export function Categories() {
  const { data: feed, isLoading } = useQuery({
    queryKey: ['category-feed'],
    queryFn: () => getCategoryFeed(3),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Categories</h1>
          <p className="text-muted-foreground">Browse by research category</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Categories</h1>
        <p className="text-muted-foreground">
          {feed?.uses_gemini_snapshot
            ? 'Browse Gemini-prepared category feeds and open the linked sources directly'
            : 'Browse saved category feeds while the next Gemini snapshot is still pending'}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {feed?.categories.map((group) => (
          <Card key={group.category.slug} className="hover:bg-muted/50 transition-colors h-full">
            <Link to={`/categories/${group.category.slug}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FolderOpen className="h-5 w-5 text-primary" />
                  {group.category.name}
                </CardTitle>
                {group.category.description && (
                  <CardDescription>{group.category.description}</CardDescription>
                )}
              </CardHeader>
            </Link>

            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">{group.category.item_count}</span>
                <Link to={`/categories/${group.category.slug}`} className="text-sm text-muted-foreground flex items-center gap-1">
                  View items <ArrowRight className="h-4 w-4" />
                </Link>
              </div>

              {group.items.length > 0 && (
                <div className="space-y-3">
                  {group.items.slice(0, 2).map((item) => (
                    <div key={item.id} className="rounded-md border p-3 space-y-2">
                      <Link to={`/items/${item.slug}`} className="font-medium hover:underline line-clamp-2 text-sm">
                        {item.title}
                      </Link>
                      {item.short_summary && (
                        <p className="text-xs text-muted-foreground line-clamp-2">{item.short_summary}</p>
                      )}
                      <div className="flex gap-2">
                        {item.source_url && (
                          <Button variant="outline" size="sm" asChild>
                            <a href={item.source_url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-3 w-3 mr-1" />
                              Source
                            </a>
                          </Button>
                        )}
                        {item.paper_url && (
                          <Button variant="outline" size="sm" asChild>
                            <a href={item.paper_url} target="_blank" rel="noopener noreferrer">
                              <FileText className="h-3 w-3 mr-1" />
                              Paper
                            </a>
                          </Button>
                        )}
                        {item.github_url && (
                          <Button variant="outline" size="sm" asChild>
                            <a href={item.github_url} target="_blank" rel="noopener noreferrer">
                              <Github className="h-3 w-3 mr-1" />
                              GitHub
                            </a>
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
