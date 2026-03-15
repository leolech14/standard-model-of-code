'use client';

import { useState } from 'react';
import { SemanticPage } from '@/lib/nodes/SemanticPage';
import { OpportunityList } from './OpportunityList';

export default function TradingPage() {
  const [filters, setFilters] = useState<Record<string, string>>({});

  return (
    <SemanticPage
      domain="trading"
      customViews={{ OpportunityList }}
      filterState={filters}
      onFilterChange={(k, v) => setFilters((prev) => ({ ...prev, [k]: v }))}
    />
  );
}
