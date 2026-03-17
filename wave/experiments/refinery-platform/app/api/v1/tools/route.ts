import { NextResponse } from 'next/server';
import { readdir, stat } from 'fs/promises';
import { join, basename } from 'path';
import { homedir } from 'os';

const TOOLS_DIRS = [
  join(homedir(), 'PROJECTS_all', 'PROJECT_elements', 'wave', 'tools'),
];

interface ToolEntry {
  name: string;
  path: string;
  type: 'directory' | 'file';
  description: string;
  modified: string;
  fileCount?: number;
}

export async function GET() {
  try {
    const tools: ToolEntry[] = [];

    for (const dir of TOOLS_DIRS) {
      try {
        const entries = await readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.name.startsWith('.') || entry.name === '__pycache__') continue;

          const fullPath = join(dir, entry.name);
          const s = await stat(fullPath).catch(() => null);
          if (!s) continue;

          if (entry.isDirectory()) {
            const files = await readdir(fullPath).catch(() => []);
            tools.push({
              name: entry.name,
              path: entry.name,
              type: 'directory',
              description: `${files.filter(f => f.endsWith('.py') || f.endsWith('.ts')).length} source files`,
              modified: s.mtime.toISOString(),
              fileCount: files.length,
            });
          } else if (entry.name.endsWith('.py') || entry.name.endsWith('.ts')) {
            tools.push({
              name: basename(entry.name, entry.name.endsWith('.py') ? '.py' : '.ts'),
              path: entry.name,
              type: 'file',
              description: `${(s.size / 1024).toFixed(1)}KB`,
              modified: s.mtime.toISOString(),
            });
          }
        }
      } catch { continue; }
    }

    tools.sort((a, b) => a.name.localeCompare(b.name));

    return NextResponse.json({
      success: true,
      data: { tools, total: tools.length },
    });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
