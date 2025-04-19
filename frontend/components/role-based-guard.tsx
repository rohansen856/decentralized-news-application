'use client';

import { useStore, UserRole } from '@/lib/store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface RoleBasedGuardProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
  redirectTo?: string;
  fallback?: React.ReactNode;
}

export function RoleBasedGuard({ 
  children, 
  allowedRoles, 
  redirectTo = '/login',
  fallback 
}: RoleBasedGuardProps) {
  const { user } = useStore();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push(redirectTo);
      return;
    }

    if (!allowedRoles.includes(user.role)) {
      router.push('/unauthorized');
      return;
    }
  }, [user, allowedRoles, redirectTo, router]);

  if (!user) {
    return fallback || <div>Loading...</div>;
  }

  if (!allowedRoles.includes(user.role)) {
    return fallback || <div>Unauthorized</div>;
  }

  return <>{children}</>;
}