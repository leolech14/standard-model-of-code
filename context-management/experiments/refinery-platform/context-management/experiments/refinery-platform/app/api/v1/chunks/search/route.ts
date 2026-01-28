import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

/**
 * POST /api/v1/chunks/search
 *
 * Search chunks across all projects or specific project
 * Returns ranked results by relevance
 */
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { query, project_id, limit = 20 } = body;

    if (!query || query.trim() === '') {
      return NextResponse.json({
        success: false,
        error: 'Query is required',
        timestamp: new Date().toISOString()
      }, { status: 400 });
    }

    // Load chunks
    const chunks = project_id
      ? await loadProjectChunks(project_id)
      : await loadAllChunks();

    // Simple text search (TODO: upgrade to semantic/embedding search)
    const queryLower = query.toLowerCase();
    const results = chunks
      .filter(chunk =>
        chunk.content.toLowerCase().includes(queryLower) ||
        chunk.file.toLowerCase().includes(queryLower)
      )
      .map(chunk => {
        // Calculate simple relevance score
        const contentMatches = (chunk.content.toLowerCase().match(new RegExp(queryLower, 'g')) || []).length;
        const fileMatches = chunk.file.toLowerCase().includes(queryLower) ? 10 : 0;
        const score = contentMatches + fileMatches;

        // Extract highlights
        const highlights = extractHighlights(chunk.content, query, 3);

        return {
          chunk,
          score,
          highlights
        };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    return NextResponse.json({
      success: true,
      data: {
        results,
        total_matches: results.length,
        query,
        project_id: project_id || 'all'
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
  const projectPaths: Record<string, string> = {
    'elements': process.env.ELEMENTS_PATH || '/Users/lech/PROJECTS_all/PROJECT_elements',
  };

  const projectPath = projectPaths[projectId];
  if (!projectPath) return [];

  const chunksDir = path.join(projectPath, '.agent/intelligence/chunks');

  try {
    const files = await fs.readdir(chunksDir);
    const chunkFiles = files.filter(f => f.endsWith('_chunks.json'));

    const allChunks = [];
    for (const file of chunkFiles) {
      const content = await fs.readFile(path.join(chunksDir, file), 'utf-8');
      const data = JSON.parse(content);
      const chunks = Array.isArray(data) ? data : (data.chunks || []);

      allChunks.push(...chunks.map((c: any) => ({
        ...c,
        project_id: projectId,
        chunk_id: c.chunk_id || `${projectId}_${c.file}_${allChunks.length}`
      })));
    }

    return allChunks;
  } catch {
    return [];
  }
}

async function loadAllChunks() {
  // For now just load Elements
  // Future: Load all registered projects
  return loadProjectChunks('elements');
}

function extractHighlights(content: string, query: string, maxHighlights: number): string[] {
  const highlights: string[] = [];
  const queryLower = query.toLowerCase();
  const contentLower = content.toLowerCase();

  let pos = 0;
  while (highlights.length < maxHighlights && pos < content.length) {
    const index = contentLower.indexOf(queryLower, pos);
    if (index === -1) break;

    // Extract context around match (50 chars before, 100 after)
    const start = Math.max(0, index - 50);
    const end = Math.min(content.length, index + query.length + 100);
    let highlight = content.substring(start, end);

    // Add ellipsis
    if (start > 0) highlight = '...' + highlight;
    if (end < content.length) highlight = highlight + '...';

    highlights.push(highlight);
    pos = index + query.length;
  }

  return highlights;
}
