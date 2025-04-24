'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArticleCard } from '@/components/article-card';
import { Sparkles, TrendingUp, Clock, User, Settings, Loader2 } from 'lucide-react';
import { Article, useStore } from '@/lib/store';
import { articlesAPI, recommendationsAPI } from '@/lib/api';
import Link from 'next/link';


export default function RecommendationsPage() {
  const { user } = useStore();
  const [activeTab, setActiveTab] = useState('for-you');
  const [recommendedArticles, setRecommendedArticles] = useState<Article[]>([]);
  const [trendingArticles, setTrendingArticles] = useState<Article[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<any[]>([]);
  const [readingHistory, setReadingHistory] = useState<Article[]>([]);
  const [userStats, setUserStats] = useState({
    articlesRead: 0,
    readingStreak: '0 days',
    favoriteTopic: 'General'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      loadRecommendations();
    }
  }, [user]);

  const loadRecommendations = async () => {
    if (!user) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Load all recommendation data in parallel
      const [
        personalizedRecs,
        trendingArticlesData,
        trendingTopicsData,
        readingHistoryData,
        userStatsData
      ] = await Promise.all([
        recommendationsAPI.getPersonalized({ limit: 6 }),
        articlesAPI.getAll({ sort_by: 'trending_score', sort_order: 'desc', per_page: 6 }),
        recommendationsAPI.getTrendingTopics(),
        recommendationsAPI.getReadingHistory(),
        recommendationsAPI.getUserStats()
      ]);

      setRecommendedArticles(personalizedRecs.recommendations || []);
      setTrendingArticles(trendingArticlesData || []);
      setTrendingTopics(trendingTopicsData.topics || []);
      setReadingHistory(readingHistoryData.articles || []);
      setUserStats(userStatsData.stats || {
        articlesRead: 0,
        readingStreak: '0 days',
        favoriteTopic: 'General'
      });
    } catch (error) {
      console.error('Error loading recommendations:', error);
      setError('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="text-center py-12">
          <CardContent>
            <User className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-xl font-semibold mb-2">Sign in for Personalized Recommendations</h3>
            <p className="text-muted-foreground mb-6">
              Get AI-powered article recommendations tailored to your interests and reading history.
            </p>
            <div className="flex justify-center space-x-4">
              <Button asChild>
                <Link href="/login">Sign In</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/register">Create Account</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Recommendations</h1>
        <p className="text-xl text-muted-foreground">
          Discover articles tailored to your interests
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-3">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="for-you" className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>For You</span>
              </TabsTrigger>
              <TabsTrigger value="trending" className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4" />
                <span>Trending</span>
              </TabsTrigger>
              <TabsTrigger value="history" className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>History</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="for-you" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Sparkles className="w-5 h-5" />
                    <span>Personalized for You</span>
                  </CardTitle>
                  <CardDescription>
                    Articles selected based on your reading history and interests
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                      <p className="text-muted-foreground">Loading personalized recommendations...</p>
                    </div>
                  ) : error ? (
                    <div className="text-center py-8">
                      <p className="text-red-500 mb-4">{error}</p>
                      <Button onClick={loadRecommendations}>Try Again</Button>
                    </div>
                  ) : recommendedArticles.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {recommendedArticles.map((article) => (
                        <ArticleCard key={article.id} article={article} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Sparkles className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-semibold mb-2">No recommendations yet</h3>
                      <p className="text-muted-foreground mb-4">
                        Start reading articles to get personalized recommendations
                      </p>
                      <Button asChild>
                        <Link href="/articles">Browse Articles</Link>
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="trending" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5" />
                    <span>Trending Now</span>
                  </CardTitle>
                  <CardDescription>
                    Popular articles and topics in the community
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                      <p className="text-muted-foreground">Loading trending articles...</p>
                    </div>
                  ) : trendingArticles.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {trendingArticles.map((article) => (
                        <ArticleCard key={article.id} article={article} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <TrendingUp className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-semibold mb-2">No trending articles</h3>
                      <p className="text-muted-foreground">Check back later for trending content</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Clock className="w-5 h-5" />
                    <span>Reading History</span>
                  </CardTitle>
                  <CardDescription>
                    Articles you've read recently
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {readingHistory.length > 0 ? (
                    <div className="space-y-4">
                      {readingHistory.map((article) => (
                        <ArticleCard key={article.id} article={article} variant="compact" />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Clock className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-semibold mb-2">No reading history yet</h3>
                      <p className="text-muted-foreground">
                        Start reading articles to see your history here
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Trending Topics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Trending Topics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {trendingTopics.map((topic, index) => (
                <div key={topic.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-muted-foreground">
                      #{index + 1}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {topic.name}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{topic.count}</p>
                    <p className="text-xs text-green-600">{topic.trend}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Recommendation Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center space-x-2">
                <Settings className="w-4 h-4" />
                <span>Preferences</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Customize your recommendation experience
              </p>
              <Button variant="outline" size="sm" className="w-full">
                Manage Interests
              </Button>
              <Button variant="outline" size="sm" className="w-full">
                Notification Settings
              </Button>
            </CardContent>
          </Card>

          {/* Your Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Your Activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Articles Read</span>
                <span className="text-sm font-medium">{userStats.articlesRead}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Reading Streak</span>
                <span className="text-sm font-medium">{userStats.readingStreak}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Favorite Topic</span>
                <Badge variant="secondary" className="text-xs">{userStats.favoriteTopic}</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}