import fs from 'fs';
import path from 'path';

const PROJECT_ROOT = '/Users/lech/PROJECTS_all/PROJECT_elements';
const COLLIDER_OUTPUT = path.join(PROJECT_ROOT, 'particle', '.collider', 'unified_analysis.json');
const REFINERY_DIR = path.join(PROJECT_ROOT, '.agent', 'intelligence', 'chunks');

export async function getColliderGraph() {
    try {
        const data = fs.readFileSync(COLLIDER_OUTPUT, 'utf8');
        const parsed = JSON.parse(data);

        // Filter edges that reference missing nodes (external dependencies)
        if (parsed.nodes && parsed.edges) {
            const nodeIds = new Set(parsed.nodes.map((n: any) => n.id));
            parsed.edges = parsed.edges.filter((e: any) =>
                nodeIds.has(e.source) && nodeIds.has(e.target)
            );
        }

        return parsed;
    } catch (error) {
        console.error('Error loading Collider graph:', error);
        return null;
    }
}

export async function getRefineryChunks() {
    try {
        const files = ['agent_chunks.json', 'core_chunks.json', 'aci_chunks.json'];
        let allChunks: any[] = [];

        for (const file of files) {
            const filePath = path.join(REFINERY_DIR, file);
            if (fs.existsSync(filePath)) {
                const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                if (data.chunks) {
                    allChunks = allChunks.concat(data.chunks);
                } else if (Array.isArray(data)) {
                    allChunks = allChunks.concat(data);
                }
            }
        }
        return allChunks;
    } catch (error) {
        console.error('Error loading Refinery chunks:', error);
        return [];
    }
}

export async function getManifest() {
    try {
        const data = fs.readFileSync(COLLIDER_OUTPUT, 'utf8');
        const parsed = JSON.parse(data);
        return parsed.manifest || null;
    } catch (error) {
        return null;
    }
}
