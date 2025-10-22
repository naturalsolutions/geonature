import { Pipe, PipeTransform } from '@angular/core';
import { Renderer, marked } from 'marked';
import * as DOMPurifyModule from 'dompurify';
const DOMPurify = (DOMPurifyModule as any).default;

const linkRenderer = new Renderer();
(linkRenderer as any).link = (
  href: string | null,
  title: string | null,
  text: string
) => {
  const safeHref = href ?? '';
  const titleAttr = title ? ` title="${title}"` : '';
  return `<a href="${safeHref}" target="_blank" rel="noopener"${titleAttr}>${text}</a>`;
};

@Pipe({ name: 'markdown' })
export class MarkdownPipe implements PipeTransform {
  transform(md: string | null | undefined): string {
    if (!md) return '';
    const html = marked.parse(md, { breaks: true, renderer: linkRenderer }) as string;
    return DOMPurify.sanitize(html, {
      USE_PROFILES: { html: true },
      ADD_ATTR: ['target', 'rel'],
    });
  }
}
