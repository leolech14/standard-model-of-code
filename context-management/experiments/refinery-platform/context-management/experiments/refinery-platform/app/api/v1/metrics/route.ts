import { NextResponse } from 'next/server';

/**
 * GET /api/v1/metrics
 *
 * Platform-wide metrics across all tenants
 */
export async function GET() {
  try {
    // For MVP: Hardcoded metrics for Elements
    // Future: Aggregate across all projects from database

    const metrics = {
      total_projects: 1,  // Elements (for now)
      total_chunks: 2673,
      total_tokens: 539000,
      active_tenants: 1,
      storage_bytes: 15000000,  // ~15MB
      last_24h: {
        queries: 0,  // TODO: Track from activity log
        processing_jobs: 0,
        chunks_created: 0,
        chunks_updated: 0,
        errors: 0
      },
      platform: {
        level: 'L7',
        target: 'L8',
        type: 'Independent Spinoff',
        origin: 'PROJECT_elements',
        version: 'v1.0.0',
        uptime_hours: Math.floor((Date.now() - new Date('2026-01-28T16:00:00Z').getTime()) / 3600000)
      }
    };

    return NextResponse.json({
      success: true,
      data: metrics,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
