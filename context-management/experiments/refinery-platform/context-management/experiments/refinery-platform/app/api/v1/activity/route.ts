import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

/**
 * GET /api/v1/activity
 *
 * Get recent activity across all projects
 * Returns timeline of processing events, searches, updates
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const hours = parseInt(searchParams.get('hours') || '24');
    const limit = parseInt(searchParams.get('limit') || '50');

    // Load activity from various sources
    const activity = await loadRecentActivity(hours);

    // Sort by timestamp desc, limit
    const sorted = activity
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit);

    return NextResponse.json({
      success: true,
      data: {
        items: sorted,
        total: activity.length,
        hours,
        limit
      },
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

interface ActivityEvent {
  id: string;
  timestamp: string;
  action: string;
  project_id: string;
  details: Record<string, any>;
  category: 'processing' | 'search' | 'update' | 'error' | 'system';
}

async function loadRecentActivity(hours: number): Promise<ActivityEvent[]> {
  const activity: ActivityEvent[] = [];
  const cutoffTime = Date.now() - (hours * 60 * 60 * 1000);

  // For MVP: Generate from filesystem watcher logs, chunk metadata, etc.
  // Future: Read from activity log database

  const elementsPath = process.env.ELEMENTS_PATH || '/Users/lech/PROJECTS_all/PROJECT_elements';

  // 1. Check filesystem watcher log
  try {
    const watcherLog = path.join(elementsPath, '.agent/intelligence/filesystem_watcher.log');
    const log = await fs.readFile(watcherLog, 'utf-8');
    const lines = log.split('\n').slice(-100); // Last 100 lines

    for (const line of lines) {
      if (!line.trim()) continue;

      // Parse log line (format: timestamp - message)
      const match = line.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - (.+)/);
      if (match) {
        const [_, timestampStr, message] = match;
        const timestamp = new Date(timestampStr).toISOString();

        if (new Date(timestamp).getTime() > cutoffTime) {
          activity.push({
            id: `watcher_${activity.length}`,
            timestamp,
            action: message.includes('triggered') ? 'processing_triggered' : 'file_change_detected',
            project_id: 'elements',
            details: { message },
            category: 'processing'
          });
        }
      }
    }
  } catch (e) {
    // Log doesn't exist or can't read
  }

  // 2. Check chunk metadata for recent updates
  try {
    const chunksDir = path.join(elementsPath, '.agent/intelligence/chunks');
    const metadataPath = path.join(chunksDir, 'metadata.json');
    const metadata = JSON.parse(await fs.readFile(metadataPath, 'utf-8'));

    if (metadata.last_generated) {
      const timestamp = metadata.last_generated;
      if (new Date(timestamp).getTime() > cutoffTime) {
        activity.push({
          id: `chunks_${activity.length}`,
          timestamp,
          action: 'chunks_updated',
          project_id: 'elements',
          details: {
            total_chunks: metadata.total_chunks || 0,
            total_tokens: metadata.total_tokens || 0
          },
          category: 'update'
        });
      }
    }
  } catch (e) {
    // Metadata doesn't exist
  }

  // 3. Synthetic events for demo (remove when real logs exist)
  if (activity.length === 0) {
    const now = new Date();
    activity.push(
      {
        id: 'demo_1',
        timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
        action: 'project_registered',
        project_id: 'elements',
        details: { name: 'PROJECT_elements' },
        category: 'system'
      },
      {
        id: 'demo_2',
        timestamp: new Date(now.getTime() - 1 * 60 * 60 * 1000).toISOString(),
        action: 'chunks_processed',
        project_id: 'elements',
        details: { chunks_created: 2673, tokens: 539000 },
        category: 'processing'
      },
      {
        id: 'demo_3',
        timestamp: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
        action: 'search_query',
        project_id: 'elements',
        details: { query: 'authentication logic', results: 12 },
        category: 'search'
      }
    );
  }

  return activity;
}
