'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Heart, 
  Gift, 
  Coins, 
  TrendingUp, 
  Users, 
  Calendar,
  ExternalLink,
  Award
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface DonationStatsProps {
  userId?: string
  type: 'author' | 'donor'
  className?: string
}

interface AuthorStats {
  author_id: string
  total_received: number
  total_donations: number
  total_nfts: number
  average_donation: number
  top_articles: Array<{
    id: string
    title: string
    donation_count: number
    total_received: number
  }>
  recent_donations: Array<{
    id: string
    amount: number
    donor_id?: string
    transaction_hash: string
    created_at: string
    metadata: {
      message?: string
      anonymous?: boolean
    }
  }>
}

interface DonorStats {
  donor_id: string
  total_given: number
  total_donations: number
  total_nfts_owned: number
  favorite_authors: Array<{
    id: string
    username: string
    donation_count: number
    total_donated: number
  }>
  recent_donations: Array<{
    id: string
    amount: number
    author_id: string
    article_id: string
    transaction_hash: string
    created_at: string
    metadata: {
      article_title?: string
      message?: string
    }
  }>
}

export function DonationStats({ userId, type, className }: DonationStatsProps) {
  const [stats, setStats] = useState<AuthorStats | DonorStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      if (!userId) return

      try {
        setLoading(true)
        const response = await fetch(`/api/v1/donations/stats/${type}/${userId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })

        if (!response.ok) {
          throw new Error('Failed to fetch donation stats')
        }

        const data = await response.json()
        setStats(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [userId, type])

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="animate-pulse">
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-8 bg-muted rounded w-1/2"></div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center h-32">
          <p className="text-muted-foreground">
            {error || 'No donation data available'}
          </p>
        </CardContent>
      </Card>
    )
  }

  const isAuthor = type === 'author'
  const authorStats = stats as AuthorStats
  const donorStats = stats as DonorStats

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {isAuthor ? 'Total Received' : 'Total Given'}
            </CardTitle>
            <Coins className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(isAuthor ? authorStats.total_received : donorStats.total_given).toFixed(4)} ETH
            </div>
            <p className="text-xs text-muted-foreground">
              From {isAuthor ? authorStats.total_donations : donorStats.total_donations} donations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Donations</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isAuthor ? authorStats.total_donations : donorStats.total_donations}
            </div>
            <p className="text-xs text-muted-foreground">
              {isAuthor ? 'Received' : 'Made'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">FTK NFTs</CardTitle>
            <Gift className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isAuthor ? authorStats.total_nfts : donorStats.total_nfts_owned}
            </div>
            <p className="text-xs text-muted-foreground">
              {isAuthor ? 'Generated' : 'Owned'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {isAuthor ? 'Average Donation' : 'Favorite Authors'}
            </CardTitle>
            {isAuthor ? (
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <Users className="h-4 w-4 text-muted-foreground" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isAuthor 
                ? `${authorStats.average_donation.toFixed(4)} ETH`
                : donorStats.favorite_authors.length
              }
            </div>
            <p className="text-xs text-muted-foreground">
              {isAuthor ? 'Per donation' : 'Authors supported'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats */}
      <Tabs defaultValue={isAuthor ? "articles" : "authors"} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value={isAuthor ? "articles" : "authors"}>
            {isAuthor ? 'Top Articles' : 'Favorite Authors'}
          </TabsTrigger>
          <TabsTrigger value="recent">Recent Activity</TabsTrigger>
        </TabsList>

        <TabsContent value={isAuthor ? "articles" : "authors"} className="space-y-4">
          {isAuthor ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Top Performing Articles
                </CardTitle>
                <CardDescription>
                  Your articles ranked by total donations received
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {authorStats.top_articles.length > 0 ? (
                  authorStats.top_articles.map((article, index) => (
                    <div key={article.id} className="flex items-center justify-between p-3 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <Badge variant="secondary" className="w-6 h-6 rounded-full p-0 flex items-center justify-center">
                          {index + 1}
                        </Badge>
                        <div>
                          <p className="font-medium text-sm">{article.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {article.donation_count} donations
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{article.total_received.toFixed(4)} ETH</p>
                        <Button variant="ghost" size="sm" className="h-auto p-1">
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No donations received yet
                  </p>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Authors You Support
                </CardTitle>
                <CardDescription>
                  Authors ranked by your total donations to them
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {donorStats.favorite_authors.length > 0 ? (
                  donorStats.favorite_authors.map((author, index) => (
                    <div key={author.id} className="flex items-center justify-between p-3 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-8 h-8">
                          <AvatarFallback>
                            {author.username.slice(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-sm">{author.username}</p>
                          <p className="text-xs text-muted-foreground">
                            {author.donation_count} donations
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{author.total_donated.toFixed(4)} ETH</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    No donations made yet
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="recent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                {isAuthor ? 'Latest donations received' : 'Your recent donations'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {(isAuthor ? authorStats.recent_donations : donorStats.recent_donations).length > 0 ? (
                (isAuthor ? authorStats.recent_donations : donorStats.recent_donations).map((donation) => (
                  <div key={donation.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Heart className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">
                          {donation.amount.toFixed(4)} ETH
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(donation.created_at), { addSuffix: true })}
                        </p>
                        {donation.metadata.message && (
                          <p className="text-xs text-muted-foreground italic mt-1">
                            "{donation.metadata.message}"
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <Button variant="ghost" size="sm" className="h-auto p-1">
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center text-muted-foreground py-8">
                  No recent activity
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}