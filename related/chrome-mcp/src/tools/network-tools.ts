import { ChromeManager } from '../chrome-manager.js';

export class NetworkTools {
  private requestLog: any[] = [];

  constructor(private chromeManager: ChromeManager) {
    this.setupRequestLogging();
  }

  private setupRequestLogging() {
    this.chromeManager.on('request', (data) => {
      this.requestLog.push({
        ...data,
        timestamp: Date.now(),
        type: 'request',
      });

      // Keep only last 1000 requests
      if (this.requestLog.length > 1000) {
        this.requestLog = this.requestLog.slice(-1000);
      }
    });

    this.chromeManager.on('response', (data) => {
      const requestIndex = this.requestLog.findIndex(
        r => r.pageId === data.pageId && r.url === data.url && r.type === 'request'
      );

      if (requestIndex !== -1) {
        this.requestLog[requestIndex] = {
          ...this.requestLog[requestIndex],
          status: data.status,
          ok: data.ok,
          responseTimestamp: data.timestamp,
          type: 'completed',
        };
      } else {
        this.requestLog.push({
          ...data,
          timestamp: Date.now(),
          type: 'response',
        });
      }
    });
  }

  async getRequests(args: { limit?: number; filter?: any }) {
    let requests = [...this.requestLog];

    // Apply filters
    if (args.filter) {
      if (args.filter.url) {
        const urlRegex = new RegExp(args.filter.url);
        requests = requests.filter(r => urlRegex.test(r.url));
      }
      if (args.filter.method) {
        requests = requests.filter(r => r.method === args.filter.method);
      }
      if (args.filter.status) {
        requests = requests.filter(r => r.status === args.filter.status);
      }
    }

    // Sort by timestamp (newest first)
    requests.sort((a, b) => b.timestamp - a.timestamp);

    // Limit results
    if (args.limit) {
      requests = requests.slice(0, args.limit);
    }

    const output = requests.map(r => {
      const duration = r.responseTimestamp
        ? `${r.responseTimestamp - r.timestamp}ms`
        : 'pending';

      return `[${r.status || 'PENDING'}] ${r.method || 'GET'} ${r.url} (${duration})`;
    }).join('\n');

    return {
      content: [
        {
          type: 'text',
          text: `Network Requests (${requests.length}):\n\n${output}`,
        },
      ],
    };
  }

  async blockRequests(args: { patterns: string[] }) {
    const page = await this.chromeManager.getCurrentPage();

    await page.setRequestInterception(true);
    page.on('request', (request) => {
      const url = request.url();
      const shouldBlock = args.patterns.some(pattern => {
        const regex = new RegExp(pattern.replace(/\*/g, '.*'));
        return regex.test(url);
      });

      if (shouldBlock) {
        request.abort();
      } else {
        request.continue();
      }
    });

    return {
      content: [
        {
          type: 'text',
          text: `Blocking requests matching: ${args.patterns.join(', ')}`,
        },
      ],
    };
  }

  async clearLogs() {
    this.requestLog = [];
    return {
      content: [
        {
          type: 'text',
          text: 'Network logs cleared',
        },
      ],
    };
  }

  async getNetworkConditions() {
    const page = await this.chromeManager.getCurrentPage();

    const conditions = await page.evaluate(() => {
      const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;

      return {
        online: navigator.onLine,
        effectiveType: connection?.effectiveType || 'unknown',
        downlink: connection?.downlink || 'unknown',
        rtt: connection?.rtt || 'unknown',
      };
    });

    return {
      content: [
        {
          type: 'text',
          text: `Network Conditions:\n\n${JSON.stringify(conditions, null, 2)}`,
        },
      ],
    };
  }
}