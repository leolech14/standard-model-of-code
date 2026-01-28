import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import yaml from 'js-yaml';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: Request) {
    try {
        const inputConfig = await request.json();

        // 1. Transform UI config to Backend Parametric Schema
        const backendConfig = {
            pipeline: {
                query: inputConfig.query || "Implicit Socratic Audit (Dashboard Trigger)",
                max_files: inputConfig.maxFiles || 50
            },
            refinery: {
                // Map 1-5 to shallow/medium/deep
                context_depth: inputConfig.contextDepth <= 2 ? 'shallow' : (inputConfig.contextDepth <= 4 ? 'medium' : 'deep'),
                attention_mode: inputConfig.attentionMode || 'laminar',
                threshold_high: 0.6,
                threshold_low: 0.3
            }
        };

        const yamlStr = yaml.dump(backendConfig);
        const tempPath = path.join(process.cwd(), 'temp_refinery_config.yaml');
        await fs.writeFile(tempPath, yamlStr);

        // 2. Upload to GCS
        // We use the LOCAL gsutil because this dashboard runs on the user's machine (Agentic Phase)
        const gcsPath = 'gs://elements-archive-2026/config/refinery_config.yaml';
        console.log('[API] Uploading config to', gcsPath);
        await execAsync(`gsutil cp ${tempPath} ${gcsPath}`);

        // 3. Trigger Cloud Run Job
        console.log('[API] Triggering Cloud Run Job...');
        const command = `gcloud run jobs execute socratic-audit-job --region us-central1 --format="value(metadata.name)"`;
        const { stdout, stderr } = await execAsync(command);

        if (stderr && !stdout) {
            console.error('[API] gcloud error:', stderr);
            throw new Error(stderr);
        }

        const executionId = stdout.trim();
        console.log('[API] Job Started:', executionId);

        // Cleanup
        await fs.unlink(tempPath);

        return NextResponse.json({
            success: true,
            executionId: executionId,
            message: `Job started: ${executionId}`
        });

    } catch (error: any) {
        console.error('[API] Execution Failed:', error);
        return NextResponse.json({
            success: false,
            error: error.message
        }, { status: 500 });
    }
}
