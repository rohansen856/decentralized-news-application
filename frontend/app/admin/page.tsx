'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RoleBasedGuard } from '@/components/role-based-guard';
import { 
  Users, 
  FileText, 
  TrendingUp, 
  Shield, 
  AlertTriangle,
  Eye,
  Ban,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { analyticsAPI } from '@/lib/api';


export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalArticles: 0,
    pendingReviews: 0,
    flaggedContent: 0,
    activeUsers: 0,
    newUsersToday: 0,
    articlesThisWeek: 0
  });
  const [recentUsers, setRecentUsers] = useState<any[]>([]);
  const [flaggedContent, setFlaggedContent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const [adminStatsResponse, recentUsersResponse, flaggedContentResponse] = await Promise.all([
        analyticsAPI.getAdminStats(),
        analyticsAPI.getRecentUsers(),
        analyticsAPI.getFlaggedContent()
      ]);

      setStats(adminStatsResponse.stats || {
        totalUsers: 0,
        totalArticles: 0,
        pendingReviews: 0,
        flaggedContent: 0,
        activeUsers: 0,
        newUsersToday: 0,
        articlesThisWeek: 0
      });
      setRecentUsers(recentUsersResponse.users || []);
      setFlaggedContent(flaggedContentResponse.content || []);
    } catch (error) {
      console.error('Error loading admin data:', error);
      setError('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = (userId: string, action: 'approve' | 'ban' | 'delete') => {
    // TODO: Implement user management actions
    console.log(`${action} user ${userId}`);
  };

  const handleContentAction = (contentId: string, action: 'approve' | 'remove') => {
    // TODO: Implement content moderation actions
    console.log(`${action} content ${contentId}`);
  };

  return (
    <RoleBasedGuard allowedRoles={['administrator']}>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Admin Dashboard</h1>
          <p className="text-xl text-muted-foreground">
            Manage users, content, and platform analytics
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="content">Content</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {loading && (
              <div className="text-center py-8">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Loading admin dashboard...</p>
              </div>
            )}
            
            {error && (
              <div className="text-center py-8">
                <p className="text-red-500 mb-4">{error}</p>
                <Button onClick={loadAdminData}>Try Again</Button>
              </div>
            )}

            {!loading && !error && (
              <>
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalUsers.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    +{stats.newUsersToday} today
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalArticles.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Published content
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.pendingReviews}</div>
                  <p className="text-xs text-muted-foreground">
                    Awaiting moderation
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Flagged Content</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{stats.flaggedContent}</div>
                  <p className="text-xs text-muted-foreground">
                    Requires attention
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Users</CardTitle>
                  <CardDescription>Latest user registrations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentUsers.map((user) => (
                      <div key={user.id} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{user.name}</p>
                          <p className="text-sm text-muted-foreground">{user.email}</p>
                        </div>
                        <div className="text-right">
                          <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                            {user.status}
                          </Badge>
                          <p className="text-xs text-muted-foreground mt-1">{user.joinDate}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Flagged Content</CardTitle>
                  <CardDescription>Content requiring review</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {flaggedContent.map((content) => (
                      <div key={content.id} className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium line-clamp-1">{content.title}</p>
                            <p className="text-sm text-muted-foreground">by {content.author}</p>
                          </div>
                          <Badge variant="destructive" className="text-xs">
                            {content.reason}
                          </Badge>
                        </div>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline" onClick={() => handleContentAction(content.id, 'approve')}>
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Approve
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => handleContentAction(content.id, 'remove')}>
                            <XCircle className="w-3 h-3 mr-1" />
                            Remove
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
                </div>

                {/* Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Users</CardTitle>
                      <CardDescription>Latest user registrations</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {recentUsers.length > 0 ? recentUsers.map((user) => (
                          <div key={user.id} className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{user.name}</p>
                              <p className="text-sm text-muted-foreground">{user.email}</p>
                            </div>
                            <div className="text-right">
                              <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                                {user.status}
                              </Badge>
                              <p className="text-xs text-muted-foreground mt-1">{user.joinDate}</p>
                            </div>
                          </div>
                        )) : (
                          <p className="text-center py-4 text-muted-foreground">No recent users</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Flagged Content</CardTitle>
                      <CardDescription>Content requiring review</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {flaggedContent.length > 0 ? flaggedContent.map((content) => (
                          <div key={content.id} className="space-y-2">
                            <div className="flex items-start justify-between">
                              <div>
                                <p className="font-medium line-clamp-1">{content.title}</p>
                                <p className="text-sm text-muted-foreground">by {content.author}</p>
                              </div>
                              <Badge variant="destructive" className="text-xs">
                                {content.reason}
                              </Badge>
                            </div>
                            <div className="flex space-x-2">
                              <Button size="sm" variant="outline" onClick={() => handleContentAction(content.id, 'approve')}>
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Approve
                              </Button>
                              <Button size="sm" variant="destructive" onClick={() => handleContentAction(content.id, 'remove')}>
                                <XCircle className="w-3 h-3 mr-1" />
                                Remove
                              </Button>
                            </div>
                          </div>
                        )) : (
                          <p className="text-center py-4 text-muted-foreground">No flagged content</p>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}
          </TabsContent>

          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>User Management</CardTitle>
                <CardDescription>Manage platform users and their permissions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <p className="font-medium">{user.name}</p>
                        <p className="text-sm text-muted-foreground">{user.email}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs capitalize">
                            {user.role}
                          </Badge>
                          <Badge variant={user.status === 'active' ? 'default' : 'secondary'} className="text-xs">
                            {user.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="w-3 h-3 mr-1" />
                          View
                        </Button>
                        <Button size="sm" variant="outline">
                          <Shield className="w-3 h-3 mr-1" />
                          Edit
                        </Button>
                        <Button size="sm" variant="destructive">
                          <Ban className="w-3 h-3 mr-1" />
                          Ban
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="content" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Content Moderation</CardTitle>
                <CardDescription>Review and moderate platform content</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {flaggedContent.map((content) => (
                    <div key={content.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-medium">{content.title}</h4>
                          <p className="text-sm text-muted-foreground">by {content.author}</p>
                          <p className="text-xs text-muted-foreground mt-1">Flagged on {content.date}</p>
                        </div>
                        <Badge variant="destructive">
                          {content.reason}
                        </Badge>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="w-3 h-3 mr-1" />
                          Review
                        </Button>
                        <Button size="sm" variant="default" onClick={() => handleContentAction(content.id, 'approve')}>
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Approve
                        </Button>
                        <Button size="sm" variant="destructive" onClick={() => handleContentAction(content.id, 'remove')}>
                          <XCircle className="w-3 h-3 mr-1" />
                          Remove
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Platform Analytics</CardTitle>
                <CardDescription>Detailed insights and metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Active Users (24h)</p>
                    <p className="text-2xl font-bold">{stats.activeUsers}</p>
                    <p className="text-xs text-green-600">+12% from yesterday</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Articles Published (7d)</p>
                    <p className="text-2xl font-bold">{stats.articlesThisWeek}</p>
                    <p className="text-xs text-green-600">This week</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium">User Engagement</p>
                    <p className="text-2xl font-bold">87%</p>
                    <p className="text-xs text-green-600">+3% from last month</p>
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