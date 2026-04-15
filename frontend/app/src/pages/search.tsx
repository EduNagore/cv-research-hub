import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { Search as SearchIcon, ArrowRight, Star, Calendar } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { searchResearchItems } from '@/lib/api';

function SearchResultCard({ item }: { item: any }) {
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
              <Badge variant="secondary">{item.source}</Badge>
              {item.github_stars !== undefined && item.github_stars > 0 && (
                <Badge variant="outline" className="flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  {item.github_stars.toLocaleString()}
                </Badge>
              )}
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {new Date(item.published_date).toLocaleDateString()}
              </span>
            </div>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/items/${item.slug}`}>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [page, setPage] = useState(1);

  const currentQuery = searchParams.get('q') || '';

  const { data, isLoading } = useQuery({
    queryKey: ['search', currentQuery, page],
    queryFn: () => searchResearchItems(currentQuery, page),
    enabled: currentQuery.length > 0,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query.trim() });
      setPage(1);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Search</h1>
        <p className="text-muted-foreground">
          Search across all research items, papers, and models
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <Input
          placeholder="Search papers, models, datasets..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <Button type="submit">
          <SearchIcon className="h-4 w-4 mr-2" />
          Search
        </Button>
      </form>

      {currentQuery && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {isLoading ? 'Searching...' : `${data?.total || 0} results for "${currentQuery}"`}
            </p>
          </div>

          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : data?.items.length === 0 ? (
            <div className="text-center py-12">
              <SearchIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">No results found</h3>
              <p className="text-muted-foreground">
                Try different keywords or check your spelling
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-3">
                {data?.items.map((item) => (
                  <SearchResultCard key={item.id} item={item} />
                ))}
              </div>

              {/* Pagination */}
              {data && data.total_pages > 1 && (
                <div className="flex items-center justify-center gap-2 pt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                  >
                    Previous
                  </Button>
                  <span className="text-sm">
                    Page {page} of {data.total_pages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page >= data.total_pages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {!currentQuery && (
        <div className="text-center py-12">
          <SearchIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium">Start searching</h3>
          <p className="text-muted-foreground">
            Enter keywords to find papers, models, and datasets
          </p>
        </div>
      )}
    </div>
  );
}
