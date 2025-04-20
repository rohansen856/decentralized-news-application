'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArticleCard } from '@/components/article-card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Sparkles, BookOpen, Users, Shield, Zap } from 'lucide-react';
import { useStore, Article } from '@/lib/store';
import { articlesAPI } from '@/lib/api';
import Link from 'next/link';

// Mock data - replace with actual API calls
const mockFeaturedArticles: Article[] = [
  {
    id: '1',
    title: 'The Future of Decentralized Journalism: How Blockchain is Revolutionizing News',
    content: 'Full article content here...',
    excerpt: 'Exploring how blockchain technology is transforming the journalism industry by providing transparency, decentralization, and new monetization models.',
    author: 'Sarah Chen',
    author_anonymous: false,
    tags: ['blockchain', 'journalism', 'technology'],
    published_at: '2025-01-08T10:00:00Z',
    likes: 127,
    image_url: 'https://images.pexels.com/photos/518543/pexels-photo-518543.jpeg'
  },
  {
    id: '2',
    title: 'AI-Powered News Curation: The Next Generation of Personalized Media',
    content: 'Full article content here...',
    excerpt: 'How artificial intelligence is reshaping how we discover and consume news, creating personalized experiences for every reader.',
    author: 'Anonymous',
    author_anonymous: true,
    tags: ['AI', 'machine learning', 'media'],
    published_at: '2025-01-08T08:00:00Z',
    likes: 89,
    image_url: 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg'
  }
];

const mockTrendingArticles: Article[] = [
  {
    id: '3',
    title: 'Breaking: Major Tech Companies Adopt Decentralized Identity Standards',
    content: 'Full article content here...',
    excerpt: 'In a landmark decision, five major technology companies announced their adoption of decentralized identity standards.',
    author: 'Mike Johnson',
    author_anonymous: false,
    tags: ['tech', 'identity', 'privacy'],
    published_at: '2025-01-08T12:00:00Z',
    likes: 245,
    image_url: 'https://images.pexels.com/photos/3184287/pexels-photo-3184287.jpeg'
  },
  {
    id: '4',
    title: 'The Economics of Anonymous Publishing: A New Revenue Model',
    content: 'Full article content here...',
    excerpt: 'Anonymous publishing is creating new economic models for content creators while protecting their identity.',
    author: 'Anonymous',
    author_anonymous: true,
    tags: ['economics', 'publishing', 'privacy'],
    published_at: '2025-01-08T09:00:00Z',
    likes: 156,
    image_url: 'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg'
  }
];

const mockRecommendedArticles: Article[] = [
  {
    id: '5',
    title: 'Understanding Zero-Knowledge Proofs in Journalism',
    content: 'Full article content here...',
    excerpt: 'A deep dive into how zero-knowledge proofs can revolutionize source protection and fact verification.',
    author: 'Dr. Alice Wang',
    author_anonymous: false,
    tags: ['cryptography', 'journalism', 'privacy'],
    published_at: '2025-01-08T07:00:00Z',
    likes: 92,
    image_url: 'https://images.pexels.com/photos/5380664/pexels-photo-5380664.jpeg'
  }
];

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('trending');
  const [featuredArticles, setFeaturedArticles] = useState<Article[]>([]);
  const [trendingArticles, setTrendingArticles] = useState<Article[]>([]);
  const [recommendedArticles, setRecommendedArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useStore();

  useEffect(() => {
    const loadArticles = async () => {
      try {
        // For now, use mock data
        setFeaturedArticles(mockFeaturedArticles);
        setTrendingArticles(mockTrendingArticles);
        setRecommendedArticles(mockRecommendedArticles);
        
        // TODO: Replace with actual API calls
        // const [trending, recommended] = await Promise.all([
        //   articlesAPI.getTrending(),
        //   user ? articlesAPI.getRecommendations() : Promise.resolve([])
        // ]);
        // setTrendingArticles(trending);
        // setRecommendedArticles(recommended);
      } catch (error) {
        console.error('Error loading articles:', error);
      } finally {
        setLoading(false);
      }
    };

    loadArticles();
  }, [user]);

  const features = [
    {
      icon: Shield,
      title: 'Anonymous Publishing',
      description: 'Protect your identity while sharing important stories with DID technology.'
    },
    {
      icon: Sparkles,
      title: 'AI Recommendations',
      description: 'Personalized news feed powered by advanced machine learning algorithms.'
    },
    {
      icon: Users,
      title: 'Community Driven',
      description: 'Reader-curated content with transparent voting and ranking systems.'
    },
    {
      icon: Zap,
      title: 'Real-time Updates',
      description: 'Get instant notifications for breaking news and trending stories.'
    }
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary/10 via-purple-50 to-blue-50 dark:from-primary/5 dark:via-purple-950/20 dark:to-blue-950/20 py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            The Future of News is Decentralized
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Experience journalism without boundaries. Read, write, and discover news on a platform 
            powered by blockchain technology and AI-driven personalization.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/articles">Explore Articles</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/write">Start Writing</Link>
            </Button>
          </div>
          
          <div className="flex flex-wrap justify-center gap-4 mt-12">
            <Badge variant="secondary" className="text-sm px-4 py-2">
              <BookOpen className="w-4 h-4 mr-2" />
              10,000+ Articles
            </Badge>
            <Badge variant="secondary" className="text-sm px-4 py-2">
              <Users className="w-4 h-4 mr-2" />
              5,000+ Writers
            </Badge>
            <Badge variant="secondary" className="text-sm px-4 py-2">
              <Shield className="w-4 h-4 mr-2" />
              100% Anonymous Options
            </Badge>
          </div>
        </div>
      </section>

      {/* Featured Articles */}
      <section className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">Featured Stories</h2>
          <Button variant="outline" asChild>
            <Link href="/articles">View All</Link>
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {featuredArticles.map((article) => (
            <ArticleCard 
              key={article.id} 
              article={article} 
              variant="featured" 
            />
          ))}
        </div>
      </section>

      {/* Trending & Recommended */}
      <section className="container mx-auto px-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex items-center justify-between mb-8">
            <TabsList className="grid w-auto grid-cols-2">
              <TabsTrigger value="trending" className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4" />
                <span>Trending</span>
              </TabsTrigger>
              <TabsTrigger value="recommended" className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>For You</span>
              </TabsTrigger>
            </TabsList>
            <Button variant="outline" asChild>
              <Link href={activeTab === 'trending' ? '/articles?sort=trending' : '/recommendations'}>
                View All
              </Link>
            </Button>
          </div>

          <TabsContent value="trending" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trendingArticles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="recommended" className="space-y-6">
            {user ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendedArticles.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
            ) : (
              <Card className="text-center py-12">
                <CardContent>
                  <Sparkles className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-xl font-semibold mb-2">Get Personalized Recommendations</h3>
                  <p className="text-muted-foreground mb-6">
                    Sign in to see articles tailored to your interests and reading history.
                  </p>
                  <Button asChild>
                    <Link href="/login">Sign In</Link>
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </section>

      {/* Features Section */}
      <section className="bg-muted/50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose FuseNews?</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Experience the next generation of journalism with cutting-edge technology 
              and community-driven content curation.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="text-center p-6 hover:shadow-lg transition-shadow">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 text-center py-16">
        <Card className="p-12 bg-gradient-to-r from-primary/5 to-purple-50 dark:from-primary/10 dark:to-purple-950/20 border-0">
          <CardHeader>
            <CardTitle className="text-3xl mb-4">Ready to Join the Revolution?</CardTitle>
            <CardDescription className="text-lg max-w-2xl mx-auto">
              Whether you're a reader seeking truth or a writer with stories to tell, 
              FuseNews provides the platform for decentralized, transparent journalism.
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link href="/register">Get Started</Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}