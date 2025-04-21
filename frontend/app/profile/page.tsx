'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArticleCard } from '@/components/article-card';
import { 
  User, 
  Settings, 
  BookOpen, 
  Heart, 
  Bookmark, 
  Shield, 
  Eye,
  Edit,
  Save,
  Loader2,
  Camera
} from 'lucide-react';
import { useStore, Article } from '@/lib/store';
import { authAPI, articlesAPI } from '@/lib/api';

// Mock user articles
const mockUserArticles: Article[] = [
  {
    id: '1',
    title: 'The Future of Decentralized Journalism',
    content: 'Full content...',
    excerpt: 'Exploring how blockchain technology is transforming journalism...',
    author: 'Demo Author',
    author_anonymous: false,
    tags: ['blockchain', 'journalism'],
    published_at: '2025-01-08T10:00:00Z',
    likes: 127,
    image_url: 'https://images.pexels.com/photos/518543/pexels-photo-518543.jpeg'
  }
];

const mockBookmarkedArticles: Article[] = [
  {
    id: '2',
    title: 'AI-Powered News Curation',
    content: 'Full content...',
    excerpt: 'How AI is reshaping news discovery...',
    author: 'Anonymous',
    author_anonymous: true,
    tags: ['AI', 'media'],
    published_at: '2025-01-08T08:00:00Z',
    likes: 89,
    image_url: 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg'
  }
];

export default function ProfilePage() {
  const { user, setUser } = useStore();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    bio: '',
    avatar: user?.avatar || '',
    didProtected: user?.did_protected || false,
    emailNotifications: true,
    publicProfile: true
  });

  const [userArticles, setUserArticles] = useState<Article[]>([]);
  const [bookmarkedArticles, setBookmarkedArticles] = useState<Article[]>([]);
  const [stats, setStats] = useState({
    articlesPublished: 0,
    totalLikes: 0,
    totalViews: 0,
    followers: 0
  });

  useEffect(() => {
    // Load user data and articles
    setUserArticles(mockUserArticles);
    setBookmarkedArticles(mockBookmarkedArticles);
    setStats({
      articlesPublished: 12,
      totalLikes: 1250,
      totalViews: 15600,
      followers: 89
    });
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setProfileData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setError('');
  };

  const handleSwitchChange = (name: string, checked: boolean) => {
    setProfileData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // TODO: Replace with actual API call
      // const updatedUser = await authAPI.updateProfile(profileData);
      // setUser(updatedUser);
      
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
    } catch (error: any) {
      setError(error.response?.data?.message || 'Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
        <p className="text-muted-foreground">Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Profile</h1>
        <p className="text-xl text-muted-foreground">
          Manage your account and content
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile" className="flex items-center space-x-2">
            <User className="w-4 h-4" />
            <span>Profile</span>
          </TabsTrigger>
          <TabsTrigger value="articles" className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4" />
            <span>My Articles</span>
          </TabsTrigger>
          <TabsTrigger value="bookmarks" className="flex items-center space-x-2">
            <Bookmark className="w-4 h-4" />
            <span>Bookmarks</span>
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Profile Info */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Profile Information</CardTitle>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditing(!isEditing)}
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      {isEditing ? 'Cancel' : 'Edit'}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
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

                  {/* Avatar */}
                  <div className="flex items-center space-x-4">
                    <Avatar className="w-20 h-20">
                      <AvatarImage src={profileData.avatar} />
                      <AvatarFallback className="text-2xl">
                        {profileData.name.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    {isEditing && (
                      <Button variant="outline" size="sm">
                        <Camera className="w-4 h-4 mr-2" />
                        Change Photo
                      </Button>
                    )}
                  </div>

                  {/* Form Fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Name</Label>
                      <Input
                        id="name"
                        name="name"
                        value={profileData.name}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={profileData.email}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="bio">Bio</Label>
                    <Textarea
                      id="bio"
                      name="bio"
                      placeholder="Tell us about yourself..."
                      value={profileData.bio}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      rows={4}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Role</Label>
                      <p className="text-sm text-muted-foreground capitalize">
                        {user.role}
                      </p>
                    </div>
                    <Badge variant="secondary" className="capitalize">
                      {user.role}
                    </Badge>
                  </div>

                  {isEditing && (
                    <div className="flex space-x-2">
                      <Button onClick={handleSaveProfile} disabled={loading}>
                        {loading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className="mr-2 h-4 w-4" />
                            Save Changes
                          </>
                        )}
                      </Button>
                      <Button variant="outline" onClick={() => setIsEditing(false)}>
                        Cancel
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Stats */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Articles Published</span>
                    <span className="font-semibold">{stats.articlesPublished}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Total Likes</span>
                    <span className="font-semibold">{stats.totalLikes}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Total Views</span>
                    <span className="font-semibold">{stats.totalViews.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Followers</span>
                    <span className="font-semibold">{stats.followers}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="w-5 h-5" />
                    <span>Privacy</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>DID Protected</Label>
                      <p className="text-sm text-muted-foreground">
                        Enhanced privacy protection
                      </p>
                    </div>
                    <Badge variant={profileData.didProtected ? "default" : "secondary"}>
                      {profileData.didProtected ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="articles" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>My Articles</CardTitle>
              <CardDescription>
                Articles you've published on the platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              {userArticles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {userArticles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-semibold mb-2">No articles yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Start writing to see your articles here
                  </p>
                  <Button>Write Your First Article</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bookmarks" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Bookmarked Articles</CardTitle>
              <CardDescription>
                Articles you've saved for later reading
              </CardDescription>
            </CardHeader>
            <CardContent>
              {bookmarkedArticles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {bookmarkedArticles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Bookmark className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-semibold mb-2">No bookmarks yet</h3>
                  <p className="text-muted-foreground">
                    Bookmark articles to save them for later
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Privacy Settings</CardTitle>
                <CardDescription>
                  Control your privacy and data protection
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>DID Protection</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable enhanced privacy protection
                    </p>
                  </div>
                  <Switch
                    checked={profileData.didProtected}
                    onCheckedChange={(checked) => handleSwitchChange('didProtected', checked)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Public Profile</Label>
                    <p className="text-sm text-muted-foreground">
                      Make your profile visible to others
                    </p>
                  </div>
                  <Switch
                    checked={profileData.publicProfile}
                    onCheckedChange={(checked) => handleSwitchChange('publicProfile', checked)}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Notification Settings</CardTitle>
                <CardDescription>
                  Manage your notification preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive updates via email
                    </p>
                  </div>
                  <Switch
                    checked={profileData.emailNotifications}
                    onCheckedChange={(checked) => handleSwitchChange('emailNotifications', checked)}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}