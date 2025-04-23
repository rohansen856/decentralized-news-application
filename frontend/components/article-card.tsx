import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Heart, Bookmark, Share2, Clock, User, Eye, BarChart } from 'lucide-react';
import { Article, useStore } from '@/lib/store';
import { interactionsAPI } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface ArticleCardProps {
  article: Article;
  variant?: 'default' | 'featured' | 'compact';
  className?: string;
}

export function ArticleCard({ article, variant = 'default', className }: ArticleCardProps) {
  const { user } = useStore();
  const timeAgo = formatDistanceToNow(new Date(article.published_at), { addSuffix: true });
  
  const [liked, setLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [stats, setStats] = useState({
    likes: article.likes || 0,
    views: article.view_count || 0,
    shares: article.share_count || 0,
    comments: article.comment_count || 0
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user && article.id) {
      loadInteractionStatus();
    }
  }, [user, article.id]);

  const loadInteractionStatus = async () => {
    try {
      const response = await interactionsAPI.getStatus(article.id);
      if (response.success) {
        setLiked(response.liked);
        setBookmarked(response.bookmarked);
        setStats(response.stats);
      }
    } catch (error) {
      console.error('Failed to load interaction status:', error);
    }
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!user || loading) return;
    
    setLoading(true);
    try {
      const response = await interactionsAPI.like(article.id);
      if (response.success) {
        setLiked(response.liked);
        setStats(prev => ({
          ...prev,
          likes: response.liked ? prev.likes + 1 : prev.likes - 1
        }));
      }
    } catch (error) {
      console.error('Failed to like article:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBookmark = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!user || loading) return;
    
    setLoading(true);
    try {
      const response = await interactionsAPI.bookmark(article.id);
      if (response.success) {
        setBookmarked(response.bookmarked);
      }
    } catch (error) {
      console.error('Failed to bookmark article:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!user || loading) return;
    
    setLoading(true);
    try {
      // Use Web Share API if available, otherwise copy to clipboard
      if (navigator.share) {
        await navigator.share({
          title: article.title,
          text: article.excerpt,
          url: window.location.origin + `/articles/${article.id}`
        });
        await interactionsAPI.share(article.id, 'native');
      } else {
        // Fallback to copying URL to clipboard
        await navigator.clipboard.writeText(window.location.origin + `/articles/${article.id}`);
        await interactionsAPI.share(article.id, 'clipboard');
      }
      
      setStats(prev => ({
        ...prev,
        shares: prev.shares + 1
      }));
    } catch (error) {
      console.error('Failed to share article:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Link href={`/articles/${article.id}`} className="block">
    <Card className={cn("h-full overflow-hidden transition-all hover:shadow-md", 
      variant === 'featured' ? 'md:flex' : '',
      variant === 'compact' ? 'p-2' : '',
      className,
    )}
    >
      {article.image_url && variant !== 'compact' && (
        <div className={cn("overflow-hidden bg-muted h-48", 
          variant === 'featured' ? 'md:h-auto md:w-1/3' : ''
        )}>
          <img 
            src={article.image_url} 
            alt={article.title}
            className="w-full h-full object-cover transition-all hover:scale-105"
          />
        </div>
      )}
      
      <div className={variant === 'featured' ? 'md:w-2/3' : 'w-full'}>
        <CardHeader className={variant === 'compact' ? 'p-2' : 'p-4'}>
          <div className="flex gap-2 mb-2">
            {article.category && (
              <Badge variant="outline" className="capitalize">
                {article.category}
              </Badge>
            )}
            {article.subcategory && (
              <Badge variant="outline" className="capitalize text-muted-foreground">
                {article.subcategory}
              </Badge>
            )}
          </div>
          
          <h3 className={cn("font-bold tracking-tight",
            variant === 'featured' ? 'text-2xl' : 'text-lg',
            variant === 'compact' ? 'text-base' : ''
          )}>
            {article.title}
          </h3>
          
          {variant !== 'compact' && (
            <p className="text-muted-foreground line-clamp-2">{article.excerpt}</p>
          )}
        </CardHeader>
        
        <CardContent className={variant === 'compact' ? 'p-2' : 'p-4'}>
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground mb-3">
            <div className="flex items-center gap-1">
              <User size={14} />
              <span>{article.author_anonymous ? 'Anonymous' : article.author}</span>
            </div>
            
            <div className="flex items-center gap-1">
              <Clock size={14} />
              <span>{timeAgo}</span>
            </div>
            
            {article.reading_time && (
              <div className="flex items-center gap-1">
                <Clock size={14} />
                <span>{article.reading_time} min read</span>
              </div>
            )}
            
            {stats.views > 0 && (
              <div className="flex items-center gap-1">
                <Eye size={14} />
                <span>{stats.views} views</span>
              </div>
            )}

            {article.trending_score && article.trending_score > 10 && (
              <div className="flex items-center gap-1">
                <BarChart size={14} />
                <span>Trending</span>
              </div>
            )}
          </div>
          
          {variant !== 'compact' && article.tags && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-4">
              {article.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {article.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{article.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
          
          <div className="flex items-center justify-between mt-auto">
            <Button 
              variant="ghost" 
              size="sm" 
              className={cn("gap-1", bookmarked && "text-primary")}
              onClick={handleBookmark}
              disabled={loading || !user}
            >
              <Bookmark size={16} className={bookmarked ? "fill-current" : ""} />
              <span className="sr-only">Bookmark</span>
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              className={cn("gap-1", liked && "text-red-500")}
              onClick={handleLike}
              disabled={loading || !user}
            >
              <Heart size={16} className={liked ? "fill-current" : ""} />
              <span>{stats.likes}</span>
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              className="gap-1"
              onClick={handleShare}
              disabled={loading || !user}
            >
              <Share2 size={16} />
              <span>{stats.shares}</span>
            </Button>
          </div>
        </CardContent>
      </div>
    </Card>
    </Link>
  );
}