import { ChromeManager } from '../chrome-manager.js';

export class BrowserTools {
  constructor(private chromeManager: ChromeManager) {}

  async launch(args: {
    headless?: boolean;
    userDataDir?: string;
    windowSize?: { width: number; height: number };
  }) {
    const result = await this.chromeManager.launch(args);
    return {
      content: [
        {
          type: 'text',
          text: result,
        },
      ],
    };
  }

  async close(args: any) {
    const result = await this.chromeManager.close();
    return {
      content: [
        {
          type: 'text',
          text: result,
        },
      ],
    };
  }

  async newTab(args: { url?: string; active?: boolean }) {
    const pageId = await this.chromeManager.newTab(args.url);
    return {
      content: [
        {
          type: 'text',
          text: `New tab created with ID: ${pageId}`,
        },
      ],
    };
  }

  async listTabs() {
    const pages = await this.chromeManager.getPageList();
    return {
      content: [
        {
          type: 'text',
          text: `Open tabs:\n\n${pages
            .map(p => `- ${p.id}: ${p.title} (${p.url})`)
            .join('\n')}`,
        },
      ],
    };
  }

  async getVersion() {
    const page = await this.chromeManager.getCurrentPage();
    const version = await page.evaluate(() => navigator.userAgent);
    return {
      content: [
        {
          type: 'text',
          text: `Browser: ${version}`,
        },
      ],
    };
  }

  async clearCache() {
    const page = await this.chromeManager.getCurrentPage();
    await page.evaluate(() => {
      // Clear various caches
      if ('caches' in window) {
        caches.keys().then(names => {
          names.forEach(name => caches.delete(name));
        });
      }
      localStorage.clear();
      sessionStorage.clear();
    });

    return {
      content: [
        {
          type: 'text',
          text: 'Cache cleared',
        },
      ],
    };
  }
}