'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Heart, 
  Bookmark, 
  Share2, 
  MessageCircle, 
  Clock, 
  User, 
  ArrowLeft,
  Eye,
  ThumbsUp
} from 'lucide-react';
import { Article, useStore } from '@/lib/store';
import { articlesAPI, interactionsAPI } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';
import Image from 'next/image';

export default function ArticlePage() {
  const params = useParams();
  const { toggleChat, user } = useStore();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [stats, setStats] = useState({
    likes: 0,
    views: 0,
    shares: 0,
    comments: 0
  });
  const [interactionLoading, setInteractionLoading] = useState(false);
  const [viewTracked, setViewTracked] = useState(false);

  useEffect(() => {
    const loadArticle = async () => {
      try {
        setLoading(true);
        
        // Use the real API to fetch article data
        const articleData = await articlesAPI.getById(params.id as string);
        
        if (articleData) {
          setArticle(articleData);
          setStats({
            likes: articleData.likes || 0,
            views: articleData.view_count || 0,
            shares: articleData.share_count || 0,
            comments: articleData.comment_count || 0
          });
          
          // Load interaction status if user is logged in
          if (user) {
            await loadInteractionStatus(params.id as string);
          }
          
          // Track view after a short delay if user is authenticated
          if (user && !viewTracked) {
            setTimeout(() => {
              trackView(params.id as string);
              setViewTracked(true);
            }, 3000);
          }
        } else {
          setArticle(null);
        }
      } catch (error) {
        console.error('Error loading article:', error);
        setArticle(null);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      loadArticle();
    }
  }, [params.id, user, viewTracked]);

  const loadInteractionStatus = async (articleId: string) => {
    try {
      const response = await interactionsAPI.getStatus(articleId);
      if (response.success) {
        setLiked(response.liked);
        setBookmarked(response.bookmarked);
        setStats(response.stats);
      }
    } catch (error) {
      console.error('Failed to load interaction status:', error);
    }
  };

  const trackView = async (articleId: string) => {
    try {
      await interactionsAPI.recordView(articleId, 0, 0);
      setStats(prev => ({ ...prev, views: prev.views + 1 }));
    } catch (error) {
      console.error('Failed to track view:', error);
    }
  };

  const handleLike = async () => {
    if (!article || !user || interactionLoading) return;
    
    setInteractionLoading(true);
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
      console.error('Error liking article:', error);
    } finally {
      setInteractionLoading(false);
    }
  };

  const handleBookmark = async () => {
    if (!article || !user || interactionLoading) return;
    
    setInteractionLoading(true);
    try {
      const response = await interactionsAPI.bookmark(article.id);
      if (response.success) {
        setBookmarked(response.bookmarked);
      }
    } catch (error) {
      console.error('Error bookmarking article:', error);
    } finally {
      setInteractionLoading(false);
    }
  };

  const handleShare = async () => {
    if (!article || !user || interactionLoading) return;
    
    setInteractionLoading(true);
    try {
      // Use Web Share API if available, otherwise copy to clipboard
      if (navigator.share) {
        await navigator.share({
          title: article.title,
          text: article.excerpt,
          url: window.location.href,
        });
        await interactionsAPI.share(article.id, 'native');
      } else {
        // Fallback to copying URL to clipboard
        await navigator.clipboard.writeText(window.location.href);
        await interactionsAPI.share(article.id, 'clipboard');
      }
      
      setStats(prev => ({ ...prev, shares: prev.shares + 1 }));
    } catch (error) {
      console.error('Error sharing article:', error);
    } finally {
      setInteractionLoading(false);
    }
  };

  const handleChatWithArticle = () => {
    if (article) {
      toggleChat(article);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-3/4"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
          <div className="h-64 bg-muted rounded"></div>
          <div className="space-y-2">
            <div className="h-4 bg-muted rounded"></div>
            <div className="h-4 bg-muted rounded"></div>
            <div className="h-4 bg-muted rounded w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Article Not Found</h1>
        <p className="text-muted-foreground mb-6">
          The article you're looking for doesn't exist or has been removed.
        </p>
        <Button asChild>
          <Link href="/articles">Back to Articles</Link>
        </Button>
      </div>
    );
  }

  const timeAgo = formatDistanceToNow(new Date(article.published_at), { addSuffix: true });

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Back Button */}
      <Button variant="ghost" asChild className="mb-6">
        <Link href="/articles" className="flex items-center space-x-2">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Articles</span>
        </Link>
      </Button>

      {/* Article Header */}
      <header className="mb-8">
        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {article.tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              {tag}
            </Badge>
          ))}
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-5xl font-bold mb-6 font-serif leading-tight">
          {article.title}
        </h1>

        {/* Author and Meta Info */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center space-x-4">
            <Avatar className="w-12 h-12">
              <AvatarFallback>
                {article.author_anonymous ? <User className="w-6 h-6" /> : "FN"}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">
                {article.author_anonymous ? 'Anonymous Author' : article.author}
              </p>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span>{timeAgo}</span>
                <span>•</span>
                <Eye className="w-4 h-4" />
                <span>{stats.views} views</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <Button
              variant={liked ? "default" : "outline"}
              size="sm"
              onClick={handleLike}
              disabled={interactionLoading || !user}
              className="flex items-center space-x-2"
            >
              <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
              <span>{stats.likes}</span>
            </Button>
            <Button
              variant={bookmarked ? "default" : "outline"}
              size="sm"
              onClick={handleBookmark}
              disabled={interactionLoading || !user}
            >
              <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-current' : ''}`} />
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleShare}
              disabled={interactionLoading || !user}
            >
              <Share2 className="w-4 h-4" />
            </Button>
            <Button variant="default" size="sm" onClick={handleChatWithArticle}>
              <MessageCircle className="w-4 h-4 mr-2" />
              Chat with Article
            </Button>
          </div>
        </div>

        {/* Featured Image */}
        {article.image_url && (
          <div className="aspect-video relative overflow-hidden rounded-lg mb-8">
            <Image
              src={article.image_url}
              alt={article.title}
              fill
              className="object-cover"
              priority
            />
          </div>
        )}
      </header>

      <Separator className="mb-8" />

      {/* Article Content */}
      <article className="prose prose-lg dark:prose-invert max-w-none">
        <div className="font-serif text-lg leading-relaxed whitespace-pre-line">
          {article.content}
        </div>
      </article>

      <Separator className="my-12" />

      {/* Article Footer */}
      <footer className="space-y-6">
        {/* Engagement Actions */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Button
                  variant={liked ? "default" : "outline"}
                  onClick={handleLike}
                  disabled={interactionLoading || !user}
                  className="flex items-center space-x-2"
                >
                  <Heart className={`w-5 h-5 ${liked ? 'fill-current' : ''}`} />
                  <span>{stats.likes} Likes</span>
                </Button>
                <Button variant="outline" onClick={handleChatWithArticle}>
                  <MessageCircle className="w-5 h-5 mr-2" />
                  Discuss with AI
                </Button>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant={bookmarked ? "default" : "outline"}
                  size="sm"
                  onClick={handleBookmark}
                  disabled={interactionLoading || !user}
                >
                  <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-current' : ''}`} />
                  {bookmarked ? 'Saved' : 'Save'}
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleShare}
                  disabled={interactionLoading || !user}
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  Share
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Author Info */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start space-x-4">
              <Avatar className="w-16 h-16">
                <AvatarFallback className="text-lg">
                  {article.author_anonymous ? <User className="w-8 h-8" /> : "FN"}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h4 className="font-semibold text-lg mb-2">
                  {article.author_anonymous ? 'Anonymous Author' : article.author}
                </h4>
                {article.author_anonymous ? (
                  <p className="text-muted-foreground">
                    This article was published anonymously using decentralized identity (DID) technology 
                    to protect the author's privacy while maintaining content authenticity.
                  </p>
                ) : (
                  <p className="text-muted-foreground">
                    Sarah is a technology journalist specializing in blockchain and decentralized systems. 
                    She has been covering the intersection of technology and media for over 8 years.
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Related Articles Placeholder */}
        <Card>
          <CardContent className="p-6">
            <h4 className="font-semibold text-lg mb-4">More from this topic</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Placeholder for related articles */}
              <div className="space-y-2">
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-3 bg-muted rounded w-1/2"></div>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-3 bg-muted rounded w-1/2"></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </footer>
    </div>
  );
}