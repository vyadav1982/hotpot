import React from 'react';
import { Link } from '@tanstack/react-router';
import { Copy } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useToast } from '@/hooks/use-toast';
import { atom, useAtom } from 'jotai';

interface BreadcrumbItem {
  label: string;
  to: string;
}

interface ReusableBreadcrumbProps {
  items?: BreadcrumbItem[];
  currentPage: string;
  className?: string;
  canCopy?: boolean;
}

export const fromPageAtom = atom<string | undefined>(undefined);

export default function ReusableBreadcrumb({
  items,
  currentPage,
  className = 'mb-6',
  canCopy = true,
}: ReusableBreadcrumbProps) {
  const { toast } = useToast();
  const [fromPage] = useAtom(fromPageAtom);

  const handleCopy = () => {
    if (canCopy) {
      navigator.clipboard.writeText(currentPage);
      toast({
        title: 'Copied',
        description: 'Page ID copied to clipboard',
      });
    }
  };

  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link to={'/'}>{'Home'}</Link>
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        {fromPage && fromPage !== currentPage ? (
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to={`/${fromPage.toLowerCase()}/`}>{fromPage}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
        ) : (
          items?.map((item, index) => (
            <React.Fragment key={item.to}>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link to={item.to}>{item.label}</Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              {index < items.length - 1 && <BreadcrumbSeparator />}
            </React.Fragment>
          ))
        )}
        {items?.length && <BreadcrumbSeparator />}
        <BreadcrumbItem>
          {canCopy ? (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="link"
                    className="h-auto p-0 text-sm font-normal"
                    onClick={handleCopy}
                  >
                    <BreadcrumbPage>{currentPage}</BreadcrumbPage>
                    <Copy className="ml-2 h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Copy</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          ) : (
            <BreadcrumbPage>{currentPage}</BreadcrumbPage>
          )}
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  );
}
