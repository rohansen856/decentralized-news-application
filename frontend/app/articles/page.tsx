'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArticleCard } from '@/components/article-card';
import { Search, Filter, SortAsc, Grid, List, Loader2 } from 'lucide-react';
import { Article } from '@/lib/store';
import { articlesAPI } from '@/lib/api';

const categories = [
  'blockchain', 'business', 'entertainment', 'health', 'journalism', 
  'lifestyle', 'politics', 'science', 'sports', 'technology'
];

const languages = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' }
];

const allTags = ['blockchain', 'journalism', 'technology', 'AI', 'machine learning', 'media', 'tech', 'identity', 'privacy', 'economics', 'publishing', 'cryptography', 'governance', 'moderation', 'community'];

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  
  const perPage = 12;

  // Initial load
  useEffect(() => {
    fetchArticles(1, true);
  }, []);

  // Filters change
  useEffect(() => {
    resetAndFetchArticles();
  }, [selectedCategory, selectedLanguage, sortBy, sortOrder]);

  // Search with debounce
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      resetAndFetchArticles();
    }, 500); // Debounce search

    return () => clearTimeout(delayedSearch);
  }, [searchQuery]);

  const resetAndFetchArticles = useCallback(async () => {
    setCurrentPage(1);
    setHasMore(true);
    await fetchArticles(1, true);
  }, [selectedCategory, selectedLanguage, sortBy, sortOrder, searchQuery]);

  const fetchArticles = async (page: number = 1, reset: boolean = false) => {
    if (reset) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      const params: any = {
        page,
        per_page: perPage,
        status: 'published',
        sort_by: sortBy,
        sort_order: sortOrder
      };

      if (selectedCategory) params.category = selectedCategory;
      if (selectedLanguage) params.language = selectedLanguage;
      if (searchQuery.trim()) {
        // Use search API for text search
        const searchResponse = await articlesAPI.search(searchQuery.trim(), params);
        const newArticles = searchResponse.articles || [];
        
        if (reset) {
          setArticles(newArticles);
        } else {
          setArticles(prev => [...prev, ...newArticles]);
        }
        
        setTotalCount(searchResponse.total || newArticles.length);
        setHasMore(newArticles.length === perPage);
      } else {
        // Use regular articles API
        const response = await articlesAPI.getAll(params);
        const newArticles = response || [];
        
        if (reset) {
          setArticles(newArticles);
        } else {
          setArticles(prev => [...prev, ...newArticles]);
        }
        
        setTotalCount(newArticles.length);
        setHasMore(newArticles.length === perPage);
      }

      if (!reset) {
        setCurrentPage(page);
      }
    } catch (error) {
      console.error('Error fetching articles:', error);
      if (reset) {
        setArticles([]);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      fetchArticles(currentPage + 1, false);
    }
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSelectedLanguage('');
    setSelectedTags([]);
    setSortBy('created_at');
    setSortOrder('desc');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">All Articles</h1>
        <p className="text-xl text-muted-foreground">
          Discover stories from our global community of writers
        </p>
      </div>

      {/* Filters and Search */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filters & Search</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search articles, authors, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Category and Language Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-3">Category</h4>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <h4 className="font-medium mb-3">Language</h4>
              <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                <SelectTrigger>
                  <SelectValue placeholder="All languages" />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((language) => (
                    <SelectItem key={language.code} value={language.code}>
                      {language.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Tags */}
          <div>
            <h4 className="font-medium mb-3">Filter by Tags</h4>
            <div className="flex flex-wrap gap-2">
              {allTags.map((tag) => (
                <Badge
                  key={tag}
                  variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Sort and View Options */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <SortAsc className="w-4 h-4" />
                <span className="text-sm font-medium">Sort by:</span>
              </div>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="created_at">Latest</SelectItem>
                  <SelectItem value="published_at">Published Date</SelectItem>
                  <SelectItem value="like_count">Most Liked</SelectItem>
                  <SelectItem value="view_count">Most Viewed</SelectItem>
                  <SelectItem value="title">Title (A-Z)</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortOrder} onValueChange={setSortOrder}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="desc">Descending</SelectItem>
                  <SelectItem value="asc">Ascending</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Active Filters */}
          {(searchQuery || selectedCategory || selectedLanguage || selectedTags.length > 0) && (
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="flex items-center flex-wrap gap-2">
                <span className="text-sm text-muted-foreground">Active filters:</span>
                {searchQuery && (
                  <Badge variant="secondary">
                    Search: "{searchQuery}"
                  </Badge>
                )}
                {selectedCategory && (
                  <Badge variant="secondary">
                    Category: {selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)}
                  </Badge>
                )}
                {selectedLanguage && (
                  <Badge variant="secondary">
                    Language: {languages.find(l => l.code === selectedLanguage)?.name}
                  </Badge>
                )}
                {selectedTags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    Tag: {tag}
                  </Badge>
                ))}
              </div>
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear all
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      <div className="mb-6">
        <p className="text-muted-foreground">
          {loading ? 'Loading...' : `${articles.length} of ${totalCount} articles`}
        </p>
      </div>

      {/* Loading State */}
      {loading && articles.length === 0 && (
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading articles...</p>
        </div>
      )}

      {/* Articles Grid/List */}
      {!loading && articles.length > 0 ? (
        <div className={viewMode === 'grid' 
          ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" 
          : "space-y-4"
        }>
          {articles.map((article) => (
            <ArticleCard 
              key={article.id} 
              article={article} 
              variant={viewMode === 'list' ? 'compact' : 'default'}
            />
          ))}
        </div>
      ) : !loading && articles.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-xl font-semibold mb-2">No articles found</h3>
            <p className="text-muted-foreground mb-6">
              Try adjusting your search query or filters to find what you're looking for.
            </p>
            <Button onClick={clearFilters}>Clear Filters</Button>
          </CardContent>
        </Card>
      ) : null}

      {/* Load More */}
      {articles.length > 0 && hasMore && (
        <div className="text-center mt-12">
          <Button 
            variant="outline" 
            size="lg" 
            onClick={handleLoadMore}
            disabled={loadingMore}
          >
            {loadingMore ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Loading...
              </>
            ) : (
              'Load More Articles'
            )}
          </Button>
        </div>
      )}

      {/* No More Articles */}
      {articles.length > 0 && !hasMore && (
        <div className="text-center mt-12">
          <p className="text-muted-foreground">No more articles to load</p>
        </div>
      )}
    </div>
  );
}