import { ChromeManager } from '../chrome-manager.js';

export class ElementTools {
  constructor(private chromeManager: ChromeManager) {}

  async click(args: {
    selector: string;
    waitForSelector?: boolean;
    timeout?: number;
  }) {
    const page = await this.chromeManager.getCurrentPage();

    if (args.waitForSelector !== false) {
      await page.waitForSelector(args.selector, {
        timeout: args.timeout || 5000,
      });
    }

    await page.click(args.selector);

    return {
      content: [
        {
          type: 'text',
          text: `Clicked element: ${args.selector}`,
        },
      ],
    };
  }

  async type(args: {
    selector: string;
    text: string;
    clear?: boolean;
    delay?: number;
  }) {
    const page = await this.chromeManager.getCurrentPage();

    await page.waitForSelector(args.selector);

    if (args.clear !== false) {
      await page.click(args.selector, { clickCount: 3 });
    }

    await page.type(args.selector, args.text, {
      delay: args.delay || 10,
    });

    return {
      content: [
        {
          type: 'text',
          text: `Typed "${args.text}" into ${args.selector}`,
        },
      ],
    };
  }

  async select(args: { selector: string; value: string }) {
    const page = await this.chromeManager.getCurrentPage();

    await page.waitForSelector(args.selector);
    await page.select(args.selector, args.value);

    return {
      content: [
        {
          type: 'text',
          text: `Selected value "${args.value}" in ${args.selector}`,
        },
      ],
    };
  }

  async hover(args: { selector: string }) {
    const page = await this.chromeManager.getCurrentPage();

    await page.waitForSelector(args.selector);
    await page.hover(args.selector);

    return {
      content: [
        {
          type: 'text',
          text: `Hovered over element: ${args.selector}`,
        },
      ],
    };
  }

  async scroll(args: { selector?: string; x?: number; y?: number }) {
    const page = await this.chromeManager.getCurrentPage();

    if (args.selector) {
      await page.waitForSelector(args.selector);
      await page.evaluate((sel) => {
        const element = document.querySelector(sel);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, args.selector);
    } else {
      await page.evaluate((x, y) => {
        window.scrollBy(x || 0, y || 0);
      }, args.x || 0, args.y || 0);
    }

    return {
      content: [
        {
          type: 'text',
          text: `Scrolled ${args.selector ? `to ${args.selector}` : `by (${args.x || 0}, ${args.y || 0})`}`,
        },
      ],
    };
  }

  async waitForElement(args: { selector: string; timeout?: number }) {
    const page = await this.chromeManager.getCurrentPage();

    const element = await page.waitForSelector(args.selector, {
      timeout: args.timeout || 30000,
    });

    const exists = !!element;

    return {
      content: [
        {
          type: 'text',
          text: `Element ${args.selector} ${exists ? 'found' : 'not found'}`,
        },
      ],
    };
  }

  async getElementInfo(args: { selector: string }) {
    const page = await this.chromeManager.getCurrentPage();

    const info = await page.evaluate((selector) => {
      const element = document.querySelector(selector);
      if (!element) return null;

      const rect = element.getBoundingClientRect();
      const computed = window.getComputedStyle(element);

      return {
        tagName: element.tagName,
        id: element.id,
        className: element.className,
        textContent: element.textContent?.substring(0, 100),
        innerHTML: element.innerHTML.substring(0, 200),
        position: {
          x: rect.left,
          y: rect.top,
          width: rect.width,
          height: rect.height,
        },
        visible: computed.display !== 'none' && computed.visibility !== 'hidden',
        zindex: computed.zIndex,
        attributes: Array.from(element.attributes).map(attr => ({
          name: attr.name,
          value: attr.value,
        })),
      };
    }, args.selector);

    return {
      content: [
        {
          type: 'text',
          text: info ? JSON.stringify(info, null, 2) : 'Element not found',
        },
      ],
    };
  }
}