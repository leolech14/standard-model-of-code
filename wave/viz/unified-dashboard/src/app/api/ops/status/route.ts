import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const PROJECT_ROOT = '/Users/lech/PROJECTS_all/PROJECT_elements';

export async function GET() {
    try {
        // Run health check script with Doppler for env vars
        const { stdout, stderr } = await execAsync(
            `doppler run -- python3 ${PROJECT_ROOT}/wave/tools/ops/health_check.py --json`,
            { timeout: 10000 }
        );

        if (stderr && !stdout) {
            return NextResponse.json(
                { error: 'Health check failed', details: stderr },
                { status: 500 }
            );
        }

        const healthData = JSON.parse(stdout);
        return NextResponse.json(healthData);

    } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return NextResponse.json(
            {
                timestamp: new Date().toISOString(),
                overall_status: 'ERROR',
                error: errorMessage,
                services: {}
            },
            { status: 500 }
        );
    }
}
