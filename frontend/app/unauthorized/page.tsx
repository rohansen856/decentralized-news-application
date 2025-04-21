'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, ArrowLeft, Home } from 'lucide-react';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-purple-50 to-blue-50 dark:from-primary/10 dark:via-purple-950/20 dark:to-blue-950/20 p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader className="pb-4">
          <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-destructive" />
          </div>
          <CardTitle className="text-2xl">Access Denied</CardTitle>
          <CardDescription className="text-base">
            You don't have permission to access this page
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              This page requires specific user permissions that your current account doesn't have.
            </p>
            <p className="text-sm text-muted-foreground">
              If you believe this is an error, please contact an administrator.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button variant="outline" asChild>
              <Link href="/" className="flex items-center space-x-2">
                <Home className="w-4 h-4" />
                <span>Go Home</span>
              </Link>
            </Button>
            <Button asChild>
              <Link href="/profile" className="flex items-center space-x-2">
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Profile</span>
              </Link>
            </Button>
          </div>

          <div className="pt-4 border-t">
            <h4 className="font-medium mb-2">Need different access?</h4>
            <p className="text-sm text-muted-foreground mb-3">
              Contact support to request role changes or additional permissions.
            </p>
            <Button variant="outline" size="sm">
              Contact Support
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}