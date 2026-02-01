import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execAsync = promisify(exec);

// Dynamically resolve repo root (unified-dashboard is at wave/viz/unified-dashboard)
const REPO_ROOT = path.resolve(process.cwd(), '../../..');

// Prefer repo venv python, fallback to system python3
function getPythonPath(): string {
    const venvPython = path.join(REPO_ROOT, '.tools_venv', 'bin', 'python');
    if (fs.existsSync(venvPython)) {
        return venvPython;
    }
    return 'python3';
}

function truncate(str: string, maxLen: number = 500): string {
    if (str.length <= maxLen) return str;
    return str.substring(0, maxLen) + '... [truncated]';
}

export async function GET() {
    try {
        const pythonPath = getPythonPath();
        const scriptPath = path.join(REPO_ROOT, 'wave', 'tools', 'ops', 'health_check.py');

        // Verify script exists
        if (!fs.existsSync(scriptPath)) {
            return NextResponse.json(
                {
                    timestamp: new Date().toISOString(),
                    overall_status: 'ERROR',
                    error: `Health check script not found: ${scriptPath}`,
                    services: {}
                },
                { status: 500 }
            );
        }

        // Run health check script with Doppler for env vars
        const { stdout, stderr } = await execAsync(
            `doppler run -- ${pythonPath} ${scriptPath} --json`,
            {
                timeout: 15000,
                cwd: REPO_ROOT
            }
        );

        if (stderr && !stdout) {
            return NextResponse.json(
                {
                    timestamp: new Date().toISOString(),
                    overall_status: 'ERROR',
                    error: 'Health check failed',
                    stderr: truncate(stderr),
                    services: {}
                },
                { status: 500 }
            );
        }

        const healthData = JSON.parse(stdout);
        return NextResponse.json(healthData);

    } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        const errorStderr = (error as { stderr?: string })?.stderr;

        return NextResponse.json(
            {
                timestamp: new Date().toISOString(),
                overall_status: 'ERROR',
                error: truncate(errorMessage),
                stderr: errorStderr ? truncate(errorStderr) : undefined,
                services: {}
            },
            { status: 500 }
        );
    }
}
