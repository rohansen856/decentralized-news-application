import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Heart, Bookmark, Share2, Clock, User, Eye, BarChart } from 'lucide-react';
import { Article } from '@/lib/store';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface ArticleCardProps {
  article: Article;
  variant?: 'default' | 'featured' | 'compact';
  className?: string;
}

export function ArticleCard({ article, variant = 'default', className }: ArticleCardProps) {
  const timeAgo = formatDistanceToNow(new Date(article.published_at), { addSuffix: true });

  const handleLike = (e: React.MouseEvent) => {
    e.preventDefault();
    // TODO: Implement like functionality
  };

  const handleBookmark = (e: React.MouseEvent) => {
    e.preventDefault();
    // TODO: Implement bookmark functionality
  };

  const handleShare = (e: React.MouseEvent) => {
    e.preventDefault();
    // TODO: Implement share functionality
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
            
            {article.view_count && (
              <div className="flex items-center gap-1">
                <Eye size={14} />
                <span>{article.view_count} views</span>
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
              className={cn("gap-1", article.bookmarked && "text-primary")}
              onClick={handleBookmark}
            >
              <Bookmark size={16} className={article.bookmarked ? "fill-current" : ""} />
              <span className="sr-only">Bookmark</span>
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              className="gap-1"
              onClick={handleLike}
            >
              <Heart size={16} />
              <span>{article.likes || 0}</span>
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              className="gap-1"
              onClick={handleShare}
            >
              <Share2 size={16} />
              <span>{article.share_count || 0}</span>
            </Button>
          </div>
        </CardContent>
      </div>
    </Card>
    </Link>
  );
}