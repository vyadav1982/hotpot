// src/components/TopBar.tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

interface TopBarProps {
  leftContent?: React.ReactNode;
  centerContent?: React.ReactNode;
  rightContent?: React.ReactNode;
  className?: string;
}

export function TopBar({
  rightContent,
  leftContent,
  centerContent,
  className,
}: TopBarProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between border-b pb-4',
        className,
      )}
    >
      <div className="flex items-center">{leftContent}</div>
      <div className="flex items-center">{centerContent}</div>
      <div className="flex items-center">{rightContent}</div>
    </div>
  );
}
