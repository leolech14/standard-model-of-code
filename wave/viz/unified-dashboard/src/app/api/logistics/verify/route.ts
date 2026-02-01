import { NextResponse } from 'next/server';
import { getManifest } from '@/lib/data-loader';

export async function GET() {
    const manifest = await getManifest();
    if (!manifest) {
        return NextResponse.json({ error: 'Manifest not found or integrity check failed' }, { status: 404 });
    }
    return NextResponse.json({
        manifest,
        verified: true,
        timestamp: new Date().toISOString()
    });
}
