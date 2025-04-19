'use client';

import * as React from 'react';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { type ThemeProviderProps } from 'next-themes/dist/types';
import { useStore } from '@/lib/store';

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const { theme } = useStore();
  
  return (
    <NextThemesProvider 
      {...props} 
      defaultTheme={theme}
      forcedTheme={theme}
    >
      {children}
    </NextThemesProvider>
  );
}