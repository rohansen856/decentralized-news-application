'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArticleCard } from '@/components/article-card';
import { Sparkles, TrendingUp, Clock, User, Settings } from 'lucide-react';
import { Article, useStore } from '@/lib/store';
import { articlesAPI } from '@/lib/api';
import Link from 'next/link';

// Mock recommendation data
const mockRecommendedArticles: Article[] = [
  {
    id: '1',
    title: 'Understanding Zero-Knowledge Proofs in Journalism',
    content: 'Full content...',
    excerpt: 'A deep dive into how zero-knowledge proofs can revolutionize source protection and fact verification.',
    author: 'Dr. Alice Wang',
    author_anonymous: false,
    tags: ['cryptography', 'journalism', 'privacy'],
    published_at: '2025-01-08T07:00:00Z',
    likes: 92,
    image_url: 'https://images.pexels.com/photos/5380664/pexels-photo-5380664.jpeg'
  },
  {
    id: '2',
    title: 'The Rise of Citizen Journalism in the Digital Age',
    content: 'Full content...',
    excerpt: 'How everyday people are becoming the new voice of news reporting through social media and digital platforms.',
    author: 'Anonymous',
    author_anonymous: true,
    tags: ['citizen journalism', 'digital media', 'social media'],
    published_at: '2025-01-08T06:00:00Z',
    likes: 156,
    image_url: 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg'
  },
  {
    id: '3',
    title: 'Blockchain Verification: The Future of Fact-Checking',
    content: 'Full content...',
    excerpt: 'Exploring how blockchain technology can create immutable records for fact-checking and source verification.',
    author: 'Tech Reporter',
    author_anonymous: false,
    tags: ['blockchain', 'fact-checking', 'verification'],
    published_at: '2025-01-08T05:00:00Z',
    likes: 203,
    image_url: 'https://images.pexels.com/photos/3184338/pexels-photo-3184338.jpeg'
  }
];

const mockTrendingTopics = [
  { name: 'Blockchain Journalism', count: 45, trend: '+12%' },
  { name: 'AI in Media', count: 38, trend: '+8%' },
  { name: 'Privacy Protection', count: 32, trend: '+15%' },
  { name: 'Decentralized Publishing', count: 28, trend: '+20%' },
  { name: 'Fact Verification', count: 24, trend: '+5%' }
];

const mockReadingHistory: Article[] = [
  {
    id: '4',
    title: 'The Economics of Anonymous Publishing',
    content: 'Full content...',
    excerpt: 'Anonymous publishing is creating new economic models for content creators.',
    author: 'Anonymous',
    author_anonymous: true,
    tags: ['economics', 'publishing', 'privacy'],
    published_at: '2025-01-07T15:00:00Z',
    likes: 89,
    image_url: 'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg'
  }
];

export default function RecommendationsPage() {
  const { user } = useStore();
  const [activeTab, setActiveTab] = useState('for-you');
  const [recommendedArticles, setRecommendedArticles] = useState<Article[]>([]);
  const [trendingTopics, setTrendingTopics] = useState(mockTrendingTopics);
  const [readingHistory, setReadingHistory] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        // For now, use mock data
        setRecommendedArticles(mockRecommendedArticles);
        setReadingHistory(mockReadingHistory);
        
        // TODO: Replace with actual API calls
        // if (user) {
        //   const recommendations = await articlesAPI.getRecommendations();
        //   setRecommendedArticles(recommendations);
        // }
      } catch (error) {
        console.error('Error loading recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    loadRecommendations();
  }, [user]);

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
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {recommendedArticles.map((article) => (
                      <ArticleCard key={article.id} article={article} />
                    ))}
                  </div>
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
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {recommendedArticles.slice(0, 4).map((article) => (
                      <ArticleCard key={article.id} article={article} />
                    ))}
                  </div>
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
                <span className="text-sm font-medium">24</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Reading Streak</span>
                <span className="text-sm font-medium">7 days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Favorite Topic</span>
                <Badge variant="secondary" className="text-xs">Blockchain</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}