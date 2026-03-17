import { NextResponse } from 'next/server';
import { readdir, stat, readFile } from 'fs/promises';
import { join, basename, extname } from 'path';
import { homedir } from 'os';

const ELEMENTS_ROOT = join(homedir(), 'PROJECTS_all', 'PROJECT_elements');

interface DocEntry {
  id: string;
  title: string;
  path: string;
  relativePath: string;
  type: 'html' | 'markdown';
  category: string;
  size: number;
  modified: string;
}

const SCAN_LOCATIONS: { dir: string; category: string }[] = [
  { dir: 'docs/specs', category: 'Architecture Specs' },
  { dir: 'docs/reader', category: 'Documentation Portal' },
  { dir: 'docs', category: 'Reports' },
  { dir: '.collider', category: 'Collider Analysis' },
  { dir: '.reh', category: 'Evolution History' },
  { dir: 'particle/docs/research', category: 'Research' },
  { dir: '.ecoroot/exploration-maps', category: 'Exploration Maps' },
];

async function scanDir(
  baseDir: string,
  category: string
): Promise<DocEntry[]> {
  const entries: DocEntry[] = [];
  const dir = join(ELEMENTS_ROOT, baseDir);

  try {
    const files = await readdir(dir);
    for (const file of files) {
      const ext = extname(file).toLowerCase();
      if (!['.html', '.md'].includes(ext)) continue;
      if (file.startsWith('.') || file === 'README.md') continue;

      const fullPath = join(dir, file);
      try {
        const s = await stat(fullPath);
        if (!s.isFile() || s.size < 100) continue;

        // Extract title from first line of markdown or <title> of HTML
        let title = basename(file, ext)
          .replace(/[-_]/g, ' ')
          .replace(/^\d{8}\s*/, '');

        if (ext === '.md') {
          try {
            const content = await readFile(fullPath, 'utf-8');
            const h1 = content.match(/^#\s+(.+)$/m);
            if (h1) title = h1[1];
          } catch { /* use filename */ }
        } else if (ext === '.html') {
          try {
            const content = await readFile(fullPath, 'utf-8');
            const titleTag = content.match(/<title>([^<]+)<\/title>/i);
            if (titleTag) title = titleTag[1];
          } catch { /* use filename */ }
        }

        entries.push({
          id: `${baseDir}/${file}`,
          title,
          path: fullPath,
          relativePath: `${baseDir}/${file}`,
          type: ext === '.html' ? 'html' : 'markdown',
          category,
          size: s.size,
          modified: s.mtime.toISOString(),
        });
      } catch { continue; }
    }
  } catch { /* dir doesn't exist */ }

  return entries;
}

export async function GET() {
  try {
    const allDocs: DocEntry[] = [];
    for (const loc of SCAN_LOCATIONS) {
      const entries = await scanDir(loc.dir, loc.category);
      allDocs.push(...entries);
    }

    // Sort by modified date (newest first)
    allDocs.sort((a, b) => b.modified.localeCompare(a.modified));

    // Group by category
    const byCategory: Record<string, DocEntry[]> = {};
    for (const doc of allDocs) {
      if (!byCategory[doc.category]) byCategory[doc.category] = [];
      byCategory[doc.category].push(doc);
    }

    return NextResponse.json({
      success: true,
      data: {
        total: allDocs.length,
        categories: byCategory,
        docs: allDocs,
      },
    });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: String(err) },
      { status: 500 }
    );
  }
}
