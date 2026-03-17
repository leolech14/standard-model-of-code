import { NextResponse } from 'next/server';
import { PARAMETERS, DOMAINS, getParamsByDomain } from '@/lib/engine/parameters';
import { BEAUTY_CONSTRAINTS } from '@/lib/engine/beauty';

export async function GET() {
  return NextResponse.json({
    success: true,
    data: {
      parameters: PARAMETERS,
      domains: DOMAINS,
      paramsByDomain: Object.fromEntries(
        DOMAINS.map(d => [d, getParamsByDomain(d)])
      ),
      beautyConstraints: BEAUTY_CONSTRAINTS.map(c => ({
        id: c.id,
        description: c.description,
      })),
      total: PARAMETERS.length,
    },
  });
}
