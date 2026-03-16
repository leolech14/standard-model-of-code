import { NextResponse } from 'next/server';
import { readFile, readdir } from 'fs/promises';
import { join } from 'path';
import { homedir } from 'os';

const DEVJOURNAL_DIR = join(homedir(), '.devjournal');
const DAYS_DIR = join(DEVJOURNAL_DIR, 'days');

interface DailyDigest {
  date: string;
  generated_at: string;
  total_events: number;
  events_by_source: Record<string, number>;
  events_by_kind: Record<string, number>;
  events_by_project: Record<string, number>;
  timeline: Array<{
    hour: number;
    label: string;
    total: number;
    by_source: Record<string, number>;
  }>;
  projects_active: string[];
  milestones: Array<Record<string, unknown>>;
  velocity: Record<string, number>;
  highlights: Array<Record<string, unknown>>;
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const date = searchParams.get('date');

    // If specific date requested, return that day's digest
    if (date) {
      const filePath = join(DAYS_DIR, `${date}.json`);
      try {
        const content = await readFile(filePath, 'utf-8');
        const digest: DailyDigest = JSON.parse(content);
        return NextResponse.json({ success: true, data: digest });
      } catch {
        return NextResponse.json(
          { success: false, error: `No journal data for ${date}` },
          { status: 404 }
        );
      }
    }

    // No date param: return latest day's full digest (for SemanticPage nodes)
    // plus available days list for navigation
    let files: string[] = [];
    try {
      files = await readdir(DAYS_DIR);
    } catch {
      return NextResponse.json({
        success: true,
        data: { days: [], total_days: 0, total_events: 0, velocity: {}, timeline: [], highlights: [], milestones: [], events_by_project: {}, events_by_source: {}, projects_active: [] },
      });
    }

    const jsonFiles = files
      .filter((f) => f.endsWith('.json'))
      .sort()
      .reverse(); // Most recent first

    // Load latest day's full digest
    let latestDigest: DailyDigest | null = null;
    if (jsonFiles.length > 0) {
      try {
        const content = await readFile(join(DAYS_DIR, jsonFiles[0]), 'utf-8');
        latestDigest = JSON.parse(content);
      } catch { /* empty */ }
    }

    // Build day summaries for navigation
    const days = [];
    for (const file of jsonFiles.slice(0, 30)) {
      try {
        const content = await readFile(join(DAYS_DIR, file), 'utf-8');
        const digest: DailyDigest = JSON.parse(content);
        days.push({
          date: digest.date,
          total_events: digest.total_events,
          events_by_source: digest.events_by_source,
          projects_active: digest.projects_active,
          velocity: digest.velocity,
          milestones_count: digest.milestones.length,
        });
      } catch {
        continue;
      }
    }

    // Merge: latest day's data at top level (for node fieldPath extraction)
    // plus days array for navigation
    return NextResponse.json({
      success: true,
      data: {
        // Latest day's fields (nodes extract from here via fieldPath)
        ...(latestDigest ?? {}),
        // Navigation
        days,
        total_days: jsonFiles.length,
        journal_dir: DEVJOURNAL_DIR,
      },
    });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: String(err) },
      { status: 500 }
    );
  }
}
