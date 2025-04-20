'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { BookOpen, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useStore } from '@/lib/store';
import { authAPI } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const { setUser, setToken } = useStore();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(formData.email, formData.password);
      
      // Set user and token in store
      setUser(response.user);
      setToken(response.token);
      
      // Redirect to dashboard or home page
      router.push('/');
    } catch (error: any) {
      setError(error.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Demo login function for development
  const handleDemoLogin = (role: 'reader' | 'author' | 'administrator' | 'auditor') => {
    const demoUsers = {
      reader: {
        id: '1',
        email: 'reader@demo.com',
        name: 'Demo Reader',
        role: 'reader' as const,
        avatar: '',
      },
      author: {
        id: '2',
        email: 'author@demo.com',
        name: 'Demo Author',
        role: 'author' as const,
        avatar: '',
      },
      administrator: {
        id: '3',
        email: 'admin@demo.com',
        name: 'Demo Admin',
        role: 'administrator' as const,
        avatar: '',
      },
      auditor: {
        id: '4',
        email: 'auditor@demo.com',
        name: 'Demo Auditor',
        role: 'auditor' as const,
        avatar: '',
      }
    };

    setUser(demoUsers[role]);
    setToken('demo-token-' + role);
    router.push('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-purple-50 to-blue-50 dark:from-primary/10 dark:via-purple-950/20 dark:to-blue-950/20 p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold">FuseNews</span>
          </div>
          <p className="text-muted-foreground">
            Sign in to your decentralized news account
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Welcome back</CardTitle>
            <CardDescription>
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    disabled={loading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="text-center">
              <Link 
                href="/forgot-password" 
                className="text-sm text-primary hover:underline"
              >
                Forgot your password?
              </Link>
            </div>

            <Separator />

            {/* Demo Login Buttons */}
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground text-center">Demo Accounts</p>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('reader')}
                  disabled={loading}
                >
                  Reader
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('author')}
                  disabled={loading}
                >
                  Author
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('administrator')}
                  disabled={loading}
                >
                  Admin
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDemoLogin('auditor')}
                  disabled={loading}
                >
                  Auditor
                </Button>
              </div>
            </div>

            <div className="text-center text-sm">
              <span className="text-muted-foreground">Don't have an account? </span>
              <Link href="/register" className="text-primary hover:underline">
                Sign up
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Features */}
        <Card className="bg-muted/50">
          <CardContent className="p-4">
            <div className="text-center space-y-2">
              <h4 className="font-medium">Why FuseNews?</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Anonymous publishing with DID protection</li>
                <li>• AI-powered personalized recommendations</li>
                <li>• Blockchain-verified content authenticity</li>
                <li>• Community-driven content curation</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}