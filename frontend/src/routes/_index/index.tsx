import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { ActiveTabContext } from '../_index';
import * as React from 'react';

import { useSetAtom } from 'jotai';
import { fromPageAtom } from '@/components/PageBreadcrumb';
import { useCurrency } from '@/hooks/useCurrency';

export const Route = createFileRoute('/_index/')({
  component: DashboardWrapper,
});

function DashboardWrapper() {
  return <DashboardPage />;
}

function DashboardPage() {
  const setFrom = useSetAtom(fromPageAtom);

  React.useEffect(() => {
    setFrom(undefined);
  }, [setFrom]);

  const activeTabContext = React.useContext(ActiveTabContext);

  if (!activeTabContext) {
    throw new Error(
      'DashboardPage must be used within an ActiveTabContext Provider',
    );
  }

  return (
    <div className="h-full flex-1 flex-col space-y-8 p-8 md:flex">
      <header className="flex items-center justify-between">
        <h1 className="text-3xl font-bold"> Dashboard </h1>
      </header>
    </div>
  );
}
