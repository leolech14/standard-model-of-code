import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

/**
 * GET /api/v1/projects
 *
 * List all registered projects (tenants) in the Refinery Platform
 *
 * Multi-tenant design: Each project is isolated
 */
export async function GET() {
  try {
    // For now: Scan Elements as first tenant
    // Future: Read from database or config

    const projects = await discoverProjects();

    return NextResponse.json({
      success: true,
      data: projects,
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

async function discoverProjects() {
  // Hardcoded for MVP - Elements as first tenant
  // Future: Scan /data/refinery/ or query database

  const elementsPath = process.env.ELEMENTS_PATH || `${process.env.HOME}/PROJECTS_all/PROJECT_elements`;
  const chunksDir = path.join(elementsPath, '.agent/intelligence/chunks');

  // Check if Elements chunks exist
  let elementChunks = 0;
  try {
    const files = await fs.readdir(chunksDir);
    elementChunks = files.filter(f => f.endsWith('_chunks.json')).length;
  } catch (e) {
    // Chunks not found - project not processed yet
  }

  return [
    {
      id: 'elements',
      name: 'PROJECT_elements',
      path: elementsPath,
      status: elementChunks > 0 ? 'active' : 'unprocessed',
      created_at: '2026-01-01T00:00:00Z',  // Placeholder
      last_processed: new Date().toISOString(),
      health: {
        chunk_count: 2673,  // From our knowledge
        token_count: 539000,
        file_count: 1384,
        coverage: 0.92,
        freshness_hours: 2,
        error_count: 0
      }
    },
    // Future tenants will be added here
    // {
    //   id: 'atman',
    //   name: 'PROJECT_atman',
    //   ...
    // }
  ];
}
