'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RoleBasedGuard } from '@/components/role-based-guard';
import { 
  PenTool, 
  Eye, 
  Save, 
  Send, 
  Image as ImageIcon, 
  Tag, 
  Shield, 
  X,
  Plus,
  Loader2
} from 'lucide-react';
import { useStore } from '@/lib/store';
import { articlesAPI } from '@/lib/api';

const suggestedTags = [
  'blockchain', 'journalism', 'technology', 'AI', 'politics', 'economics',
  'privacy', 'security', 'media', 'society', 'environment', 'health',
  'science', 'culture', 'business', 'education', 'innovation'
];

export default function WritePage() {
  const router = useRouter();
  const { user } = useStore();
  const [activeTab, setActiveTab] = useState('write');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    title: '',
    excerpt: '',
    content: '',
    tags: [] as string[],
    imageUrl: '',
    publishAnonymously: false,
    isDraft: true
  });

  const [newTag, setNewTag] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setError('');
  };

  const handleSwitchChange = (name: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const addTag = (tag: string) => {
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
    setNewTag('');
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleAddCustomTag = () => {
    if (newTag.trim()) {
      addTag(newTag.trim().toLowerCase());
    }
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Title is required');
      return false;
    }
    if (!formData.content.trim()) {
      setError('Content is required');
      return false;
    }
    if (!formData.excerpt.trim()) {
      setError('Excerpt is required');
      return false;
    }
    if (formData.tags.length === 0) {
      setError('At least one tag is required');
      return false;
    }
    return true;
  };

  const handleSave = async (publish: boolean = false) => {
    if (!validateForm()) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const articleData = {
        title: formData.title,
        content: formData.content,
        summary: formData.excerpt,
        category: formData.tags[0] || 'general', // Use first tag as category or default to 'general'
        tags: formData.tags,
        anonymous_author: formData.publishAnonymously,
        language: 'en',
        status: publish ? 'published' : 'draft'
      };

      const data = await articlesAPI.create(articleData);
      router.push(`/articles/${data.id}`);
      
      setSuccess(publish ? 'Article published successfully!' : 'Draft saved successfully!');
      
      if (publish) {
        // setTimeout(() => {
        //   router.push('/articles');
        // }, 2000);
      }
    } catch (error: any) {
      setError(error.response?.data?.message || 'Failed to save article. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const wordCount = formData.content.split(/\s+/).filter(word => word.length > 0).length;
  const readingTime = Math.ceil(wordCount / 200);

  return (
    <RoleBasedGuard allowedRoles={['author', 'administrator']}>
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Write Article</h1>
          <p className="text-xl text-muted-foreground">
            Share your story with the world
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="write" className="flex items-center space-x-2">
              <PenTool className="w-4 h-4" />
              <span>Write</span>
            </TabsTrigger>
            <TabsTrigger value="preview" className="flex items-center space-x-2">
              <Eye className="w-4 h-4" />
              <span>Preview</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="write" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-6">
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {success && (
                  <Alert>
                    <AlertDescription>{success}</AlertDescription>
                  </Alert>
                )}

                <Card>
                  <CardHeader>
                    <CardTitle>Article Content</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">Title *</Label>
                      <Input
                        id="title"
                        name="title"
                        placeholder="Enter your article title..."
                        value={formData.title}
                        onChange={handleInputChange}
                        className="text-lg"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="excerpt">Excerpt *</Label>
                      <Textarea
                        id="excerpt"
                        name="excerpt"
                        placeholder="Write a brief summary of your article..."
                        value={formData.excerpt}
                        onChange={handleInputChange}
                        rows={3}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="content">Content *</Label>
                      <Textarea
                        id="content"
                        name="content"
                        placeholder="Write your article content here..."
                        value={formData.content}
                        onChange={handleInputChange}
                        rows={20}
                        className="font-mono"
                      />
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>{wordCount} words</span>
                        <span>~{readingTime} min read</span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="imageUrl">Featured Image URL</Label>
                      <div className="flex space-x-2">
                        <Input
                          id="imageUrl"
                          name="imageUrl"
                          placeholder="https://example.com/image.jpg"
                          value={formData.imageUrl}
                          onChange={handleInputChange}
                        />
                        <Button variant="outline" size="icon">
                          <ImageIcon className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Publishing Options */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="w-5 h-5" />
                      <span>Publishing Options</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Publish Anonymously</Label>
                        <p className="text-sm text-muted-foreground">
                          Use DID protection to hide your identity
                        </p>
                      </div>
                      <Switch
                        checked={formData.publishAnonymously}
                        onCheckedChange={(checked) => handleSwitchChange('publishAnonymously', checked)}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Tags */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Tag className="w-5 h-5" />
                      <span>Tags</span>
                    </CardTitle>
                    <CardDescription>
                      Add tags to help readers discover your article
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Selected Tags */}
                    {formData.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {formData.tags.map((tag) => (
                          <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
                            <span>{tag}</span>
                            <button
                              onClick={() => removeTag(tag)}
                              className="ml-1 hover:text-destructive"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* Add Custom Tag */}
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Add custom tag..."
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddCustomTag()}
                      />
                      <Button variant="outline" size="icon" onClick={handleAddCustomTag}>
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Suggested Tags */}
                    <div>
                      <Label className="text-sm">Suggested Tags</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {suggestedTags
                          .filter(tag => !formData.tags.includes(tag))
                          .slice(0, 10)
                          .map((tag) => (
                            <Badge
                              key={tag}
                              variant="outline"
                              className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                              onClick={() => addTag(tag)}
                            >
                              {tag}
                            </Badge>
                          ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Actions */}
                <Card>
                  <CardContent className="pt-6 space-y-3">
                    <Button
                      onClick={() => handleSave(true)}
                      disabled={loading}
                      className="w-full"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Publishing...
                        </>
                      ) : (
                        <>
                          <Send className="mr-2 h-4 w-4" />
                          Publish Article
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleSave(false)}
                      disabled={loading}
                      className="w-full"
                    >
                      <Save className="mr-2 h-4 w-4" />
                      Save as Draft
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="preview" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex flex-wrap gap-2 mb-4">
                  {formData.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
                <CardTitle className="text-3xl font-bold font-serif">
                  {formData.title || 'Article Title'}
                </CardTitle>
                <CardDescription className="text-lg">
                  {formData.excerpt || 'Article excerpt will appear here...'}
                </CardDescription>
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <span>By {formData.publishAnonymously ? 'Anonymous' : user?.username}</span>
                  <span>•</span>
                  <span>{wordCount} words</span>
                  <span>•</span>
                  <span>~{readingTime} min read</span>
                </div>
              </CardHeader>
              <CardContent>
                {formData.imageUrl && (
                  <div className="aspect-video relative overflow-hidden rounded-lg mb-6">
                    <img
                      src={formData.imageUrl}
                      alt="Featured"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div className="prose prose-lg dark:prose-invert max-w-none">
                  <div className="whitespace-pre-wrap font-serif text-lg leading-relaxed">
                    {formData.content || 'Your article content will appear here...'}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </RoleBasedGuard>
  );
}