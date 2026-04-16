import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, 
  ExternalLink, 
  Github, 
  FileText, 
  Star, 
  Heart, 
  Bookmark,
  Calendar,
  User,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { getResearchItem, toggleFavorite, toggleBookmark, updateItemStatus } from '@/lib/api';

export function ResearchItemDetail() {
  const { slug } = useParams<{ slug: string }>();
  const queryClient = useQueryClient();

  const { data: item, isLoading } = useQuery({
    queryKey: ['research-item', slug],
    queryFn: () => getResearchItem(slug!),
    enabled: !!slug,
  });

  const favoriteMutation = useMutation({
    mutationFn: () => toggleFavorite(item!.id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['research-item', slug] });
      toast.success(data.is_favorite ? 'Added to favorites' : 'Removed from favorites');
    },
  });

  const bookmarkMutation = useMutation({
    mutationFn: () => toggleBookmark(item!.id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['research-item', slug] });
      toast.success(data.is_bookmarked ? 'Bookmarked' : 'Removed bookmark');
    },
  });

  const statusMutation = useMutation({
    mutationFn: (status: string) => updateItemStatus(item!.id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['research-item', slug] });
      toast.success('Status updated');
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-12 w-3/4" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Item not found</p>
        <Button asChild className="mt-4">
          <Link to="/items">Back to items</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Button variant="ghost" asChild>
        <Link to="/items" className="flex items-center gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to items
        </Link>
      </Button>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{item.title}</h1>
        
        <div className="flex items-center gap-2 mt-3 flex-wrap">
          <Badge variant="secondary">{item.source}</Badge>
          <Badge variant="outline">{item.contribution_type}</Badge>
          {item.modality && (
            <Badge variant="outline" className="capitalize">
              {item.modality}
            </Badge>
          )}
          {item.architecture_family && (
            <Badge variant="outline" className="capitalize">
              {item.architecture_family}
            </Badge>
          )}
          <Badge 
            variant={item.status_label === 'trending' ? 'default' : 'outline'}
            className="capitalize"
          >
            {item.status_label.replace(/_/g, ' ')}
          </Badge>
        </div>

        <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            {new Date(item.published_date).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>
          {item.github_stars !== undefined && item.github_stars > 0 && (
            <span className="flex items-center gap-1">
              <Star className="h-4 w-4" />
              {item.github_stars.toLocaleString()} stars
            </span>
          )}
          <span>Relevance: {item.relevance_score.toFixed(1)}</span>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 mt-4">
          <Button
            variant={item.is_favorite ? 'default' : 'outline'}
            size="sm"
            onClick={() => favoriteMutation.mutate()}
          >
            <Heart className={`h-4 w-4 mr-2 ${item.is_favorite ? 'fill-current' : ''}`} />
            {item.is_favorite ? 'Favorited' : 'Favorite'}
          </Button>
          <Button
            variant={item.is_bookmarked ? 'default' : 'outline'}
            size="sm"
            onClick={() => bookmarkMutation.mutate()}
          >
            <Bookmark className={`h-4 w-4 mr-2 ${item.is_bookmarked ? 'fill-current' : ''}`} />
            {item.is_bookmarked ? 'Bookmarked' : 'Bookmark'}
          </Button>
          <Select
            value={item.user_status || 'unread'}
            onValueChange={(value) => statusMutation.mutate(value)}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="unread">Unread</SelectItem>
              <SelectItem value="reading">Reading</SelectItem>
              <SelectItem value="read">Read</SelectItem>
              <SelectItem value="review_later">Review Later</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Links */}
        <div className="flex items-center gap-2 mt-4">
          {item.source_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.source_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Open Source
              </a>
            </Button>
          )}
          {item.paper_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.paper_url} target="_blank" rel="noopener noreferrer">
                <FileText className="h-4 w-4 mr-2" />
                Paper
              </a>
            </Button>
          )}
          {item.abstract_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.abstract_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Abstract
              </a>
            </Button>
          )}
          {item.code_url && !item.github_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.code_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Code
              </a>
            </Button>
          )}
          {item.github_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.github_url} target="_blank" rel="noopener noreferrer">
                <Github className="h-4 w-4 mr-2" />
                Code
              </a>
            </Button>
          )}
          {item.project_page_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.project_page_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Project Page
              </a>
            </Button>
          )}
          {item.demo_url && (
            <Button variant="outline" size="sm" asChild>
              <a href={item.demo_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Demo
              </a>
            </Button>
          )}
        </div>
      </div>

      <Separator />

      {/* Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {/* Abstract */}
          {item.abstract && (
            <Card>
              <CardHeader>
                <CardTitle>Abstract</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {item.abstract}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Summary */}
          {item.full_summary && (
            <Card>
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {item.full_summary}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Why it matters */}
          {item.why_it_matters && (
            <Card>
              <CardHeader>
                <CardTitle>Why It Matters</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {item.why_it_matters}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Problem solved */}
          {item.problem_solved && (
            <Card>
              <CardHeader>
                <CardTitle>Problem Solved</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {item.problem_solved}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Use cases */}
          {item.use_cases && item.use_cases.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Use Cases</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                  {item.use_cases.map((useCase, index) => (
                    <li key={index}>{useCase}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Authors */}
          {item.authors && item.authors.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Authors
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {item.authors.slice(0, 10).map((author, index) => (
                    <li key={index}>{author}</li>
                  ))}
                  {item.authors.length > 10 && (
                    <li className="text-xs">
                      +{item.authors.length - 10} more
                    </li>
                  )}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Categories */}
          {item.categories && item.categories.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Categories</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {item.categories.map((category) => (
                    <Badge key={category.id} variant="secondary">
                      {category.name}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tags */}
          {item.tags && item.tags.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Tags</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {item.tags.map((tag) => (
                    <Badge 
                      key={tag.id} 
                      variant="outline"
                      style={{ borderColor: tag.color || undefined }}
                    >
                      {tag.name}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Scores */}
          <Card>
            <CardHeader>
              <CardTitle>Scores</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="flex justify-between text-sm">
                  <span>Relevance</span>
                  <span>{item.relevance_score.toFixed(1)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full mt-1">
                  <div 
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${item.relevance_score}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm">
                  <span>Recency</span>
                  <span>{item.recency_score.toFixed(1)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full mt-1">
                  <div 
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${item.recency_score * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm">
                  <span>Code Availability</span>
                  <span>{item.code_availability_score.toFixed(1)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full mt-1">
                  <div 
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${item.code_availability_score * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm">
                  <span>Impact</span>
                  <span>{item.impact_score.toFixed(1)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full mt-1">
                  <div 
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${item.impact_score * 100}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* GitHub Info */}
          {item.github_url && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Github className="h-4 w-4" />
                  GitHub
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {item.github_stars !== undefined && (
                  <div className="flex items-center gap-2 text-sm">
                    <Star className="h-4 w-4" />
                    <span>{item.github_stars.toLocaleString()} stars</span>
                  </div>
                )}
                {item.github_forks !== undefined && (
                  <div className="flex items-center gap-2 text-sm">
                    <ExternalLink className="h-4 w-4" />
                    <span>{item.github_forks.toLocaleString()} forks</span>
                  </div>
                )}
                {item.github_language && (
                  <div className="text-sm text-muted-foreground">
                    Language: {item.github_language}
                  </div>
                )}
                {item.is_official_code && (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span>Official code</span>
                  </div>
                )}
                {item.is_unofficial_reimplementation && (
                  <div className="flex items-center gap-2 text-sm text-yellow-600">
                    <AlertCircle className="h-4 w-4" />
                    <span>Unofficial reimplementation</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
