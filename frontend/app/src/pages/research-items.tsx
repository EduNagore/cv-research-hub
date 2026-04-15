import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Star, 
  Calendar,
  ExternalLink,
  Github,
  FileText,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { getResearchItems, getCategories } from '@/lib/api';
import type { ResearchItem } from '@/types';

function ResearchItemCard({ item }: { item: ResearchItem }) {
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
              <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                {item.short_summary}
              </p>
            )}
            
            <div className="flex items-center gap-2 mt-3 flex-wrap">
              <Badge variant="secondary">
                {item.source}
              </Badge>
              <Badge variant="outline">
                {item.contribution_type}
              </Badge>
              {item.modality && (
                <Badge variant="outline" className="capitalize">
                  {item.modality}
                </Badge>
              )}
              {item.github_stars !== undefined && item.github_stars > 0 && (
                <Badge variant="outline" className="flex items-center gap-1">
                  <Star className="h-3 w-3" />
                  {item.github_stars.toLocaleString()}
                </Badge>
              )}
            </div>
            
            <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {new Date(item.published_date).toLocaleDateString()}
              </span>
              <span>Score: {item.relevance_score.toFixed(1)}</span>
              
              <div className="flex items-center gap-2 ml-auto">
                {item.paper_url && (
                  <a 
                    href={item.paper_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <FileText className="h-4 w-4" />
                  </a>
                )}
                {item.github_url && (
                  <a 
                    href={item.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Github className="h-4 w-4" />
                  </a>
                )}
                {item.abstract_url && (
                  <a 
                    href={item.abstract_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function FilterPanel({ 
  filters, 
  setFilters,
  categories 
}: { 
  filters: Record<string, any>;
  setFilters: (filters: Record<string, any>) => void;
  categories: any[];
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium">Source</label>
        <Select 
          value={filters.source || 'all'} 
          onValueChange={(v) => setFilters({ ...filters, source: v === 'all' ? '' : v })}
        >
          <SelectTrigger>
            <SelectValue placeholder="All sources" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sources</SelectItem>
            <SelectItem value="arxiv">arXiv</SelectItem>
            <SelectItem value="papers_with_code">Papers with Code</SelectItem>
            <SelectItem value="github">GitHub</SelectItem>
            <SelectItem value="huggingface">Hugging Face</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="text-sm font-medium">Type</label>
        <Select 
          value={filters.contribution_type || 'all'} 
          onValueChange={(v) => setFilters({ ...filters, contribution_type: v === 'all' ? '' : v })}
        >
          <SelectTrigger>
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            <SelectItem value="paper">Paper</SelectItem>
            <SelectItem value="model">Model</SelectItem>
            <SelectItem value="dataset">Dataset</SelectItem>
            <SelectItem value="benchmark">Benchmark</SelectItem>
            <SelectItem value="repository">Repository</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="text-sm font-medium">Category</label>
        <Select 
          value={filters.category || 'all'} 
          onValueChange={(v) => setFilters({ ...filters, category: v === 'all' ? '' : v })}
        >
          <SelectTrigger>
            <SelectValue placeholder="All categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat.slug} value={cat.slug}>
                {cat.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="text-sm font-medium">Has Code</label>
        <Select 
          value={filters.has_code === undefined ? 'all' : filters.has_code ? 'yes' : 'no'} 
          onValueChange={(v) => setFilters({ 
            ...filters, 
            has_code: v === 'all' ? undefined : v === 'yes' 
          })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Any" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any</SelectItem>
            <SelectItem value="yes">Yes</SelectItem>
            <SelectItem value="no">No</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="text-sm font-medium">Sort By</label>
        <Select 
          value={filters.sort_by || 'published_date'} 
          onValueChange={(v) => setFilters({ ...filters, sort_by: v })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="published_date">Date</SelectItem>
            <SelectItem value="relevance_score">Relevance</SelectItem>
            <SelectItem value="github_stars">GitHub Stars</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}

export function ResearchItems() {
  const { slug } = useParams();
  const [searchParams] = useSearchParams();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, any>>({
    category: slug || searchParams.get('category') || '',
    contribution_type: searchParams.get('contribution_type') || '',
    source: searchParams.get('source') || '',
    has_code: searchParams.get('has_code') === 'true' ? true : 
              searchParams.get('has_code') === 'false' ? false : undefined,
    sort_by: 'published_date',
    sort_order: 'desc',
    page: 1,
    page_size: 20,
  });

  const { data: itemsData, isLoading: itemsLoading } = useQuery({
    queryKey: ['research-items', filters],
    queryFn: () => getResearchItems(filters),
  });

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search: searchQuery, page: 1 });
  };

  const handlePageChange = (newPage: number) => {
    setFilters({ ...filters, page: newPage });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Research Items</h1>
        <p className="text-muted-foreground">
          Browse and search through the latest computer vision research
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <Input
            placeholder="Search papers, models, datasets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1"
          />
          <Button type="submit">
            <Search className="h-4 w-4" />
          </Button>
        </form>

        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Filters</SheetTitle>
            </SheetHeader>
            <div className="mt-4">
              <FilterPanel 
                filters={filters} 
                setFilters={setFilters}
                categories={categoriesData || []}
              />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Results */}
      {itemsLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : itemsData?.items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No items found</p>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Showing {(filters.page - 1) * filters.page_size + 1} - {Math.min(filters.page * filters.page_size, itemsData?.total || 0)} of {itemsData?.total || 0} items
            </span>
          </div>

          <div className="space-y-3">
            {itemsData?.items.map((item) => (
              <ResearchItemCard key={item.id} item={item} />
            ))}
          </div>

          {/* Pagination */}
          {itemsData && itemsData.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(filters.page - 1)}
                disabled={filters.page <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <span className="text-sm">
                Page {filters.page} of {itemsData.total_pages}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(filters.page + 1)}
                disabled={filters.page >= itemsData.total_pages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
