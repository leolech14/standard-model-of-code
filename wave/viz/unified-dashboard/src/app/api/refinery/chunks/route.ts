import { NextResponse } from 'next/server';
import { getRefineryChunks } from '@/lib/data-loader';

export async function GET() {
    const chunks = await getRefineryChunks();
    return NextResponse.json({
        chunks,
        total_count: chunks.length,
        timestamp: new Date().toISOString()
    });
}
