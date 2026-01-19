import { ChromeManager } from '../chrome-manager.js';
import { marked } from 'marked';

export class PageTools {
  constructor(private chromeManager: ChromeManager) {}

  async navigate(args: { url: string; waitUntil?: string; timeout?: number }) {
    const page = await this.chromeManager.getCurrentPage();

    await page.goto(args.url, {
      waitUntil: args.waitUntil as any || 'load',
      timeout: args.timeout || 30000,
    });

    const title = await page.title();
    const url = page.url();

    return {
      content: [
        {
          type: 'text',
          text: `Navigated to: ${title}\nURL: ${url}`,
        },
      ],
    };
  }

  async screenshot(args: {
    format?: 'png' | 'jpeg';
    fullPage?: boolean;
    selector?: string;
    quality?: number;
  }) {
    const base64Image = await this.chromeManager.takeScreenshot(
      undefined,
      args
    );

    return {
      content: [
        {
          type: 'image',
          data: base64Image,
          mimeType: `image/${args.format || 'png'}`,
        },
      ],
    };
  }

  async getContent(args: {
    format?: 'html' | 'text' | 'markdown';
    selector?: string;
  }) {
    const page = await this.chromeManager.getCurrentPage();

    let content: string;
    const format = args.format || 'text';

    if (args.selector) {
      const element = await page.$(args.selector);
      if (!element) {
        throw new Error(`Element with selector ${args.selector} not found`);
      }
      content = await page.evaluate(
        (el, fmt) => {
          if (fmt === 'html') return el.outerHTML;
          if (fmt === 'text') return el.textContent || '';
          return el.innerHTML;
        },
        element,
        format
      );
    } else {
      switch (format) {
        case 'html':
          content = await page.content();
          break;
        case 'text':
          content = await page.evaluate(() => document.body.innerText);
          break;
        case 'markdown':
          const html = await page.content();
          content = await this.htmlToMarkdown(html);
          break;
      }
    }

    // Truncate if too long
    if (content.length > 100000) {
      content = content.substring(0, 100000) + '\n\n... [Content truncated]';
    }

    return {
      content: [
        {
          type: 'text',
          text: content,
        },
      ],
    };
  }

  async execute(args: {
    script: string;
    args?: string[];
    waitForResult?: boolean;
  }) {
    const page = await this.chromeManager.getCurrentPage();

    try {
      const result = await page.evaluate(
        new Function('args', args.script),
        args.args || []
      );

      return {
        content: [
          {
            type: 'text',
            text: typeof result === 'object'
              ? JSON.stringify(result, null, 2)
              : String(result),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error executing script: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async analyze(args: {
    includePerformance?: boolean;
    includeAccessibility?: boolean;
    includeSEO?: boolean;
  }) {
    const page = await this.chromeManager.getCurrentPage();
    const metrics: any = {};

    // Basic metrics
    metrics.title = await page.title();
    metrics.url = page.url();
    metrics.viewport = await page.evaluate(() => ({
      width: window.innerWidth,
      height: window.innerHeight,
    }));

    // Performance metrics
    if (args.includePerformance !== false) {
      const perfMetrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByType('paint')[0]?.startTime,
          firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime,
        };
      });
      metrics.performance = perfMetrics;
    }

    // SEO metrics
    if (args.includeSEO !== false) {
      const seoMetrics = await page.evaluate(() => {
        const getMeta = (name: string) => {
          const meta = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
          return meta?.getAttribute('content');
        };

        return {
          title: document.title?.length || 0,
          description: getMeta('description')?.length || 0,
          h1: document.querySelectorAll('h1').length,
          h2: document.querySelectorAll('h2').length,
          h3: document.querySelectorAll('h3').length,
          images: {
            total: document.querySelectorAll('img').length,
            withAlt: document.querySelectorAll('img[alt]').length,
          },
          links: {
            internal: document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]').length,
            external: document.querySelectorAll('a[href^="http"]:not([href^="' + window.location.origin + '"])').length,
          },
          hasCanonical: !!document.querySelector('link[rel="canonical"]'),
        };
      });
      metrics.seo = seoMetrics;
    }

    // Accessibility metrics
    if (args.includeAccessibility !== false) {
      const a11yMetrics = await page.evaluate(() => {
        return {
          imagesWithoutAlt: document.querySelectorAll('img:not([alt])').length,
          inputsWithoutLabel: document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])').length,
          linksWithoutText: document.querySelectorAll('a:empty').length,
          headingsWithoutContent: document.querySelectorAll('h1,h2,h3,h4,h5,h6').length,
        };
      });
      metrics.accessibility = a11yMetrics;
    }

    return {
      content: [
        {
          type: 'text',
          text: `Page Analysis:\n\n${JSON.stringify(metrics, null, 2)}`,
        },
      ],
    };
  }

  async getLinks(args: { selector?: string; externalOnly?: boolean }) {
    const page = await this.chromeManager.getCurrentPage();

    const links = await page.evaluate((sel, external) => {
      const container = sel ? document.querySelector(sel) : document.body;
      if (!container) return [];

      const links = Array.from(container.querySelectorAll('a[href]'));
      return links.map(link => ({
        text: link.textContent?.trim() || '',
        href: link.getAttribute('href'),
        title: link.getAttribute('title'),
        target: link.getAttribute('target'),
      }));
    }, args.selector || '', args.externalOnly || false);

    // Filter external links if requested
    if (args.externalOnly) {
      const pageUrl = new URL(page.url());
      return {
        content: [
          {
            type: 'text',
            text: `External Links:\n\n${links
              .filter(link => {
                try {
                  const linkUrl = new URL(link.href!);
                  return linkUrl.origin !== pageUrl.origin;
                } catch {
                  return true; // Invalid URLs are treated as external
                }
              })
              .map(link => `- ${link.text}: ${link.href}`)
              .join('\n')}`,
          },
        ],
      };
    }

    return {
      content: [
        {
          type: 'text',
          text: `Links found:\n\n${links
            .map(link => `- ${link.text}: ${link.href}`)
            .join('\n')}`,
        },
      ],
    };
  }

  async getForms(args: { includeInputs?: boolean }) {
    const page = await this.chromeManager.getCurrentPage();

    const forms = await page.evaluate((includeInputs) => {
      return Array.from(document.querySelectorAll('form')).map(form => ({
        id: form.id,
        action: form.action,
        method: form.method,
        inputs: includeInputs ? Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({
          name: input.getAttribute('name'),
          type: input.getAttribute('type') || input.tagName.toLowerCase(),
          id: input.id,
          required: input.hasAttribute('required'),
          placeholder: input.getAttribute('placeholder'),
        })) : [],
      }));
    }, args.includeInputs !== false);

    return {
      content: [
        {
          type: 'text',
          text: `Forms found:\n\n${JSON.stringify(forms, null, 2)}`,
        },
      ],
    };
  }

  private async htmlToMarkdown(html: string): Promise<string> {
    // Simple HTML to Markdown conversion
    // In a real implementation, you might use a proper library
    return html
      .replace(/<h([1-6])>(.*?)<\/h[1-6]>/gi, (_, level, text) =>
        `${'#'.repeat(parseInt(level))} ${text}\n\n`)
      .replace(/<strong>(.*?)<\/strong>/gi, '**$1**')
      .replace(/<em>(.*?)<\/em>/gi, '*$1*')
      .replace(/<a href="(.*?)".*?>(.*?)<\/a>/gi, '[$2]($1)')
      .replace(/<p>(.*?)<\/p>/gi, '$1\n\n')
      .replace(/<br>/gi, '\n')
      .replace(/<[^>]*>/g, '');
  }
}