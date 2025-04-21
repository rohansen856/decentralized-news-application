'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RoleBasedGuard } from '@/components/role-based-guard';
import { 
  Search, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  FileText,
  User,
  Clock
} from 'lucide-react';

// Mock auditor data
const mockPendingReviews = [
  {
    id: '1',
    title: 'Blockchain Technology in Modern Journalism',
    author: 'Anonymous',
    submittedDate: '2025-01-08T10:00:00Z',
    type: 'article',
    priority: 'high',
    reason: 'DID verification required'
  },
  {
    id: '2',
    title: 'The Future of Decentralized Media',
    author: 'John Doe',
    submittedDate: '2025-01-08T08:00:00Z',
    type: 'article',
    priority: 'medium',
    reason: 'Content verification'
  }
];

const mockFlaggedContent = [
  {
    id: '3',
    title: 'Controversial Political Statement',
    author: 'Anonymous',
    flaggedDate: '2025-01-07T15:00:00Z',
    reason: 'Misinformation reported',
    reportCount: 5,
    status: 'pending'
  },
  {
    id: '4',
    title: 'Unverified Claims About Technology',
    author: 'TechWriter',
    flaggedDate: '2025-01-07T12:00:00Z',
    reason: 'Source verification needed',
    reportCount: 3,
    status: 'under_review'
  }
];

const mockDIDVerifications = [
  {
    id: '5',
    author: 'Anonymous Author #1',
    articleTitle: 'Sensitive Political Expose',
    submittedDate: '2025-01-08T09:00:00Z',
    didHash: '0x1234...abcd',
    status: 'pending'
  },
  {
    id: '6',
    author: 'Anonymous Author #2',
    articleTitle: 'Corporate Whistleblower Report',
    submittedDate: '2025-01-07T16:00:00Z',
    didHash: '0x5678...efgh',
    status: 'verified'
  }
];

export default function AuditorPage() {
  const [activeTab, setActiveTab] = useState('reviews');
  const [pendingReviews, setPendingReviews] = useState(mockPendingReviews);
  const [flaggedContent, setFlaggedContent] = useState(mockFlaggedContent);
  const [didVerifications, setDIDVerifications] = useState(mockDIDVerifications);
  const [loading, setLoading] = useState(false);

  const handleReviewAction = (reviewId: string, action: 'approve' | 'reject' | 'request_changes') => {
    // TODO: Implement review actions
    console.log(`${action} review ${reviewId}`);
    setPendingReviews(prev => prev.filter(review => review.id !== reviewId));
  };

  const handleFlaggedContentAction = (contentId: string, action: 'approve' | 'remove' | 'escalate') => {
    // TODO: Implement flagged content actions
    console.log(`${action} flagged content ${contentId}`);
    setFlaggedContent(prev => 
      prev.map(content => 
        content.id === contentId 
          ? { ...content, status: action === 'approve' ? 'approved' : action === 'remove' ? 'removed' : 'escalated' }
          : content
      )
    );
  };

  const handleDIDVerification = (verificationId: string, action: 'verify' | 'reject') => {
    // TODO: Implement DID verification actions
    console.log(`${action} DID verification ${verificationId}`);
    setDIDVerifications(prev =>
      prev.map(verification =>
        verification.id === verificationId
          ? { ...verification, status: action === 'verify' ? 'verified' : 'rejected' }
          : verification
      )
    );
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'secondary';
      case 'under_review': return 'default';
      case 'approved': return 'default';
      case 'verified': return 'default';
      case 'rejected': return 'destructive';
      case 'removed': return 'destructive';
      default: return 'outline';
    }
  };

  return (
    <RoleBasedGuard allowedRoles={['auditor', 'administrator']}>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Auditor Dashboard</h1>
          <p className="text-xl text-muted-foreground">
            Review content, verify DID authenticity, and maintain platform integrity
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Reviews</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pendingReviews.length}</div>
              <p className="text-xs text-muted-foreground">Awaiting review</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Flagged Content</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{flaggedContent.length}</div>
              <p className="text-xs text-muted-foreground">Requires attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">DID Verifications</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{didVerifications.filter(d => d.status === 'pending').length}</div>
              <p className="text-xs text-muted-foreground">Pending verification</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-muted-foreground">Reviews completed</p>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="reviews">Content Reviews</TabsTrigger>
            <TabsTrigger value="flagged">Flagged Content</TabsTrigger>
            <TabsTrigger value="did">DID Verification</TabsTrigger>
          </TabsList>

          <TabsContent value="reviews" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Pending Content Reviews</CardTitle>
                <CardDescription>
                  Articles and content awaiting auditor review
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {pendingReviews.map((review) => (
                    <div key={review.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-medium mb-1">{review.title}</h4>
                          <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
                            <User className="w-3 h-3" />
                            <span>by {review.author}</span>
                            <span>•</span>
                            <Clock className="w-3 h-3" />
                            <span>{new Date(review.submittedDate).toLocaleDateString()}</span>
                          </div>
                          <p className="text-sm text-muted-foreground">{review.reason}</p>
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <Badge variant={getPriorityColor(review.priority)}>
                            {review.priority} priority
                          </Badge>
                          <Badge variant="outline">
                            {review.type}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="w-3 h-3 mr-1" />
                          Review
                        </Button>
                        <Button 
                          size="sm" 
                          variant="default"
                          onClick={() => handleReviewAction(review.id, 'approve')}
                        >
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Approve
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleReviewAction(review.id, 'request_changes')}
                        >
                          <FileText className="w-3 h-3 mr-1" />
                          Request Changes
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => handleReviewAction(review.id, 'reject')}
                        >
                          <XCircle className="w-3 h-3 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {pendingReviews.length === 0 && (
                    <div className="text-center py-8">
                      <CheckCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                      <h3 className="text-lg font-semibold mb-2">All caught up!</h3>
                      <p className="text-muted-foreground">No pending reviews at the moment.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="flagged" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Flagged Content</CardTitle>
                <CardDescription>
                  Content reported by the community for review
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {flaggedContent.map((content) => (
                    <div key={content.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-medium mb-1">{content.title}</h4>
                          <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
                            <User className="w-3 h-3" />
                            <span>by {content.author}</span>
                            <span>•</span>
                            <AlertTriangle className="w-3 h-3" />
                            <span>{content.reportCount} reports</span>
                            <span>•</span>
                            <Clock className="w-3 h-3" />
                            <span>{new Date(content.flaggedDate).toLocaleDateString()}</span>
                          </div>
                          <p className="text-sm text-muted-foreground">{content.reason}</p>
                        </div>
                        <Badge variant={getStatusColor(content.status)}>
                          {content.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="w-3 h-3 mr-1" />
                          Review Content
                        </Button>
                        <Button 
                          size="sm" 
                          variant="default"
                          onClick={() => handleFlaggedContentAction(content.id, 'approve')}
                          disabled={content.status !== 'pending'}
                        >
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Approve
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => handleFlaggedContentAction(content.id, 'remove')}
                          disabled={content.status !== 'pending'}
                        >
                          <XCircle className="w-3 h-3 mr-1" />
                          Remove
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleFlaggedContentAction(content.id, 'escalate')}
                          disabled={content.status !== 'pending'}
                        >
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Escalate
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="did" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>DID Verification Queue</CardTitle>
                <CardDescription>
                  Verify decentralized identity authenticity for anonymous publications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {didVerifications.map((verification) => (
                    <div key={verification.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-medium mb-1">{verification.articleTitle}</h4>
                          <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
                            <User className="w-3 h-3" />
                            <span>{verification.author}</span>
                            <span>•</span>
                            <Clock className="w-3 h-3" />
                            <span>{new Date(verification.submittedDate).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center space-x-2 text-sm">
                            <Shield className="w-3 h-3" />
                            <code className="text-xs bg-muted px-2 py-1 rounded">
                              {verification.didHash}
                            </code>
                          </div>
                        </div>
                        <Badge variant={getStatusColor(verification.status)}>
                          {verification.status}
                        </Badge>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Search className="w-3 h-3 mr-1" />
                          Verify DID
                        </Button>
                        <Button 
                          size="sm" 
                          variant="default"
                          onClick={() => handleDIDVerification(verification.id, 'verify')}
                          disabled={verification.status !== 'pending'}
                        >
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Verify
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => handleDIDVerification(verification.id, 'reject')}
                          disabled={verification.status !== 'pending'}
                        >
                          <XCircle className="w-3 h-3 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </RoleBasedGuard>
  );
}