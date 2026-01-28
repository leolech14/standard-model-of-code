import { NextResponse } from 'next/server';
import { getColliderGraph } from '@/lib/data-loader';

export async function GET() {
    const graph = await getColliderGraph();
    if (!graph) {
        return NextResponse.json({ error: 'Failed to load graph data' }, { status: 500 });
    }
    return NextResponse.json(graph);
}
