import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

/**
 * GET /api/v1/projects/:id/chunks
 *
 * Get chunks for a specific project (tenant)
 * Supports pagination
 */
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const perPage = parseInt(searchParams.get('per_page') || '50');

    const { id } = await params;
    const projectId = id;

    // Load chunks for this project
    const chunks = await loadProjectChunks(projectId);

    // Paginate
    const start = (page - 1) * perPage;
    const end = start + perPage;
    const paginatedChunks = chunks.slice(start, end);

    return NextResponse.json({
      success: true,
      data: {
        items: paginatedChunks,
        total: chunks.length,
        page,
        per_page: perPage,
        has_more: end < chunks.length
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

async function loadProjectChunks(projectId: string) {
  // Map project ID to actual data location
  const projectPaths: Record<string, string> = {
    'elements': process.env.ELEMENTS_PATH || `${process.env.HOME}/PROJECTS_all/PROJECT_elements`,
    // Future: 'atman', 'sentinel', etc.
  };

  const projectPath = projectPaths[projectId];
  if (!projectPath) {
    throw new Error(`Unknown project: ${projectId}`);
  }

  // Load chunk files
  const chunksDir = path.join(projectPath, '.agent/intelligence/chunks');

  try {
    const files = await fs.readdir(chunksDir);
    const chunkFiles = files.filter(f => f.endsWith('_chunks.json'));

    // Load all chunk files
    const allChunks = [];
    for (const file of chunkFiles) {
      const filePath = path.join(chunksDir, file);
      const content = await fs.readFile(filePath, 'utf-8');
      const data = JSON.parse(content);

      // Normalize format (data might be array or object with chunks key)
      const chunks = Array.isArray(data) ? data : (data.chunks || []);

      // Add project_id to each chunk
      allChunks.push(...chunks.map((c: any) => ({
        ...c,
        project_id: projectId,
        chunk_id: c.chunk_id || `${projectId}_${c.file}_${allChunks.length}`
      })));
    }

    return allChunks;
  } catch (error) {
    console.error(`Failed to load chunks for ${projectId}:`, error);
    return [];
  }
}
