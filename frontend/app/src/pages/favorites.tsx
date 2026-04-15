import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Heart, Bookmark, Clock, ExternalLink } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { getFavorites, getBookmarks, getReviewLater } from '@/lib/api';

function ItemCard({ item }: { item: any }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <Link 
              to={`/items/${item.research_item_id}`}
              className="font-medium hover:underline line-clamp-2"
            >
              {item.research_item_title}
            </Link>
            <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
              <span>
                {new Date(item.research_item_published_date).toLocaleDateString()}
              </span>
              <span>•</span>
              <span>Score: {item.research_item_relevance_score?.toFixed(1)}</span>
            </div>
            {item.notes && (
              <p className="text-sm text-muted-foreground mt-2">
                Notes: {item.notes}
              </p>
            )}
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/items/${item.research_item_id}`}>
              <ExternalLink className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function Favorites() {
  const { data: favorites, isLoading: favoritesLoading } = useQuery({
    queryKey: ['favorites'],
    queryFn: getFavorites,
  });

  const { data: bookmarks, isLoading: bookmarksLoading } = useQuery({
    queryKey: ['bookmarks'],
    queryFn: getBookmarks,
  });

  const { data: reviewLater, isLoading: reviewLaterLoading } = useQuery({
    queryKey: ['review-later'],
    queryFn: getReviewLater,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Library</h1>
        <p className="text-muted-foreground">
          Manage your favorites, bookmarks, and reading list
        </p>
      </div>

      <Tabs defaultValue="favorites" className="space-y-6">
        <TabsList>
          <TabsTrigger value="favorites" className="flex items-center gap-2">
            <Heart className="h-4 w-4" />
            Favorites
            {favorites?.items && (
              <Badge variant="secondary" className="ml-1">
                {favorites.items.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="bookmarks" className="flex items-center gap-2">
            <Bookmark className="h-4 w-4" />
            Bookmarks
            {bookmarks?.items && (
              <Badge variant="secondary" className="ml-1">
                {bookmarks.items.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="review-later" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Review Later
            {reviewLater?.items && (
              <Badge variant="secondary" className="ml-1">
                {reviewLater.items.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="favorites" className="space-y-4">
          {favoritesLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : favorites?.items.length === 0 ? (
            <div className="text-center py-12">
              <Heart className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">No favorites yet</h3>
              <p className="text-muted-foreground mb-4">
                Items you favorite will appear here
              </p>
              <Button asChild>
                <Link to="/items">Browse items</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {favorites?.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="bookmarks" className="space-y-4">
          {bookmarksLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : bookmarks?.items.length === 0 ? (
            <div className="text-center py-12">
              <Bookmark className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">No bookmarks yet</h3>
              <p className="text-muted-foreground mb-4">
                Items you bookmark will appear here
              </p>
              <Button asChild>
                <Link to="/items">Browse items</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {bookmarks?.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="review-later" className="space-y-4">
          {reviewLaterLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : reviewLater?.items.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium">No items to review</h3>
              <p className="text-muted-foreground mb-4">
                Items marked for later review will appear here
              </p>
              <Button asChild>
                <Link to="/items">Browse items</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {reviewLater?.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
