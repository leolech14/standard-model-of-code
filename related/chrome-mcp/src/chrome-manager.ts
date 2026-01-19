import puppeteer, { Browser, Page, Target } from 'puppeteer';
import { EventEmitter } from 'events';

export interface BrowserConfig {
  headless?: boolean;
  userDataDir?: string;
  windowSize?: {
    width: number;
    height: number;
  };
  devtools?: boolean;
  args?: string[];
}

export interface PageConfig {
  viewport?: {
    width: number;
    height: number;
    deviceScaleFactor?: number;
  };
  userAgent?: string;
  locale?: string;
  timezoneId?: string;
}

export class ChromeManager extends EventEmitter {
  private browser: Browser | null = null;
  private pages: Map<string, Page> = new Map();
  private defaultConfig: BrowserConfig = {
    headless: false,
    windowSize: { width: 1920, height: 1080 },
    devtools: false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding',
      '--disable-features=TranslateUI',
      '--disable-ipc-flooding-protection',
    ],
  };

  async launch(config: BrowserConfig = {}): Promise<string> {
    if (this.browser) {
      throw new Error('Chrome browser is already running');
    }

    const mergedConfig = { ...this.defaultConfig, ...config };

    // Add window size args if provided
    if (mergedConfig.windowSize) {
      mergedConfig.args!.push(
        `--window-size=${mergedConfig.windowSize.width},${mergedConfig.windowSize.height}`
      );
    }

    // Add user data dir if provided
    if (mergedConfig.userDataDir) {
      mergedConfig.args!.push(`--user-data-dir=${mergedConfig.userDataDir}`);
    }

    this.browser = await puppeteer.launch({
      headless: mergedConfig.headless,
      devtools: mergedConfig.devtools,
      args: mergedConfig.args,
      defaultViewport: mergedConfig.windowSize,
    });

    // Set up event listeners
    this.browser.on('targetcreated', this.handleTargetCreated.bind(this));
    this.browser.on('targetdestroyed', this.handleTargetDestroyed.bind(this));
    this.browser.on('targetchanged', this.handleTargetChanged.bind(this));

    this.emit('launched');

    return 'Browser launched successfully';
  }

  async close(): Promise<string> {
    if (!this.browser) {
      return 'Browser is not running';
    }

    await this.browser.close();
    this.browser = null;
    this.pages.clear();

    this.emit('closed');

    return 'Browser closed successfully';
  }

  async newTab(url?: string): Promise<string> {
    if (!this.browser) {
      throw new Error('Browser is not running');
    }

    const page = await this.browser.newPage();
    const pageId = this.generatePageId(page);

    // Set up page event listeners
    page.on('console', (msg) => {
      this.emit('console', { pageId, type: msg.type(), text: msg.text() });
    });

    page.on('pageerror', (error) => {
      this.emit('pageerror', { pageId, error: error.message });
    });

    page.on('request', (request) => {
      this.emit('request', {
        pageId,
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType(),
      });
    });

    page.on('response', (response) => {
      this.emit('response', {
        pageId,
        url: response.url(),
        status: response.status(),
        ok: response.ok(),
      });
    });

    this.pages.set(pageId, page);

    if (url) {
      await page.goto(url);
    }

    this.emit('newTab', { pageId, url });

    return pageId;
  }

  async getPage(pageId: string): Promise<Page> {
    const page = this.pages.get(pageId);
    if (!page) {
      throw new Error(`Page with ID ${pageId} not found`);
    }
    return page;
  }

  async getCurrentPage(): Promise<Page> {
    if (!this.browser) {
      throw new Error('Browser is not running');
    }

    const pages = await this.browser.pages();
    if (pages.length === 0) {
      throw new Error('No pages available');
    }

    // Return the active page
    const activeTarget = this.browser.targets().find(t => t.type() === 'page');
    if (activeTarget) {
      return await activeTarget.page() as Page;
    }

    return pages[0];
  }

  async getAllPages(): Promise<Page[]> {
    if (!this.browser) {
      throw new Error('Browser is not running');
    }

    return await this.browser.pages();
  }

  async closeTab(pageId: string): Promise<string> {
    const page = this.pages.get(pageId);
    if (!page) {
      throw new Error(`Page with ID ${pageId} not found`);
    }

    await page.close();
    this.pages.delete(pageId);

    this.emit('tabClosed', { pageId });

    return `Page ${pageId} closed`;
  }

  async configurePage(pageId: string, config: PageConfig): Promise<string> {
    const page = await this.getPage(pageId);

    if (config.viewport) {
      await page.setViewport(config.viewport);
    }

    if (config.userAgent) {
      await page.setUserAgent(config.userAgent);
    }

    if (config.locale) {
      await page.setExtraHTTPHeaders({ 'Accept-Language': config.locale });
    }

    if (config.timezoneId) {
      await page.emulateTimezone(config.timezoneId);
    }

    return `Page ${pageId} configured successfully`;
  }

  async takeScreenshot(
    pageId?: string,
    options: {
      format?: 'png' | 'jpeg';
      fullPage?: boolean;
      selector?: string;
      quality?: number;
    } = {}
  ): Promise<string> {
    const page = pageId
      ? await this.getPage(pageId)
      : await this.getCurrentPage();

    if (options.selector) {
      const element = await page.$(options.selector);
      if (!element) {
        throw new Error(`Element with selector ${options.selector} not found`);
      }
      return await element.screenshot({
        encoding: 'base64',
        type: options.format || 'png',
        quality: options.quality,
      }) as string;
    }

    return await page.screenshot({
      encoding: 'base64',
      type: options.format || 'png',
      fullPage: options.fullPage !== false,
      quality: options.quality,
    }) as string;
  }

  async executeScript(
    pageId: string,
    script: string,
    ...args: any[]
  ): Promise<any> {
    const page = await this.getPage(pageId);
    return await page.evaluate(script, ...args);
  }

  private generatePageId(page: Page): string {
    return `page_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async handleTargetCreated(target: Target) {
    if (target.type() === 'page') {
      const page = await target.page();
      if (page) {
        const pageId = this.generatePageId(page);
        this.pages.set(pageId, page);
        this.emit('pageCreated', { pageId, target });
      }
    }
  }

  private async handleTargetDestroyed(target: Target) {
    if (target.type() === 'page') {
      // Find and remove page
      for (const [pageId, page] of this.pages.entries()) {
        if (page.isClosed()) {
          this.pages.delete(pageId);
          this.emit('pageDestroyed', { pageId, target });
          break;
        }
      }
    }
  }

  private async handleTargetChanged(target: Target) {
    if (target.type() === 'page') {
      this.emit('pageChanged', { target });
    }
  }

  async cleanup(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.pages.clear();
    }
  }

  // Utility methods
  get isRunning(): boolean {
    return this.browser !== null && this.browser.isConnected();
  }

  get pageCount(): number {
    return this.pages.size;
  }

  async getPageList(): Promise<Array<{ id: string; url: string; title: string }>> {
    const pageList = [];
    for (const [pageId, page] of this.pages.entries()) {
      try {
        const url = page.url();
        const title = await page.title();
        pageList.push({ id: pageId, url, title });
      } catch (e) {
        // Page might be closed
        this.pages.delete(pageId);
      }
    }
    return pageList;
  }
}