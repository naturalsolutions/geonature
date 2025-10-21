import { Pipe, PipeTransform } from '@angular/core';
import { marked } from 'marked';
import * as DOMPurifyModule from 'dompurify';
const DOMPurify = (DOMPurifyModule as any).default;

@Pipe({ name: 'markdown' })
export class MarkdownPipe implements PipeTransform {
  transform(md: string | null | undefined): string {
    if (!md) return '';
    const html = marked.parse(md, { breaks: true }) as string;
    return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
  }
}
