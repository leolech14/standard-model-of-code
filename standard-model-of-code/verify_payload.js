const fs = require('fs');
const zlib = require('zlib');

// Read HTML
const html = fs.readFileSync('.collider/output_human-readable_standard-model-of-code_20260121_092355.html', 'utf-8');

// Extract payload
const match = html.match(/COMPRESSED_PAYLOAD\s*=\s*"([A-Za-z0-9+/=]+)"/);
if (!match) {
    console.log('Payload not found');
    process.exit(1);
}

const payload = match[1];
console.log('Payload length:', payload.length);

// Decode base64
const decoded = Buffer.from(payload, 'base64');
console.log('Decoded length:', decoded.length);

// Inflate
const inflated = zlib.gunzipSync(decoded);
console.log('Inflated length:', inflated.length);

// Parse JSON
console.log('Parsing JSON...');
const start = Date.now();
const data = JSON.parse(inflated.toString('utf-8'));
console.log('Parse time:', Date.now() - start, 'ms');
console.log('Nodes:', data.nodes?.length);
console.log('Links:', data.links?.length);
console.log('File boundaries:', data.file_boundaries?.length);
