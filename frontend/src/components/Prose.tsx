/**
 * Minimal inline markup renderer.
 *
 * Content authors get `**bold**`, `*italic*`, `` `code` ``, and `[text](url)`. Nothing here ever
 * produces raw HTML — no `dangerouslySetInnerHTML` anywhere in the app — so untrusted-looking
 * content cannot become script.
 */

import { Fragment, type ReactNode } from 'react';

const TOKEN = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)\s]+\))/g;

function isSafeUrl(url: string): boolean {
  return /^(https?:\/\/|\/|#|mailto:)/i.test(url);
}

export function inlineFormat(text: string): ReactNode[] {
  const parts = text.split(TOKEN).filter((part) => part !== '');
  return parts.map((part, index) => {
    const key = `${index}-${part.slice(0, 8)}`;
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={key}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={key}>{part.slice(1, -1)}</code>;
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }
    const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(part);
    if (link?.[1] && link[2]) {
      const [, label, url] = link;
      if (!isSafeUrl(url)) return <Fragment key={key}>{label}</Fragment>;
      const external = /^https?:\/\//i.test(url);
      return (
        <a
          key={key}
          href={url}
          {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
        >
          {label}
        </a>
      );
    }
    return <Fragment key={key}>{part}</Fragment>;
  });
}

export function Paragraph({ children }: { children: string }) {
  return <p>{inlineFormat(children)}</p>;
}

export function Prose({ body, className }: { body: readonly string[]; className?: string }) {
  return (
    <div className={className}>
      {body.map((block, index) => {
        const key = `${index}-${block.slice(0, 16)}`;
        if (block.startsWith('- ')) {
          const items = block
            .split('\n')
            .map((line) => line.replace(/^-\s*/, '').trim())
            .filter(Boolean);
          return (
            <ul key={key}>
              {items.map((item, i) => (
                <li key={`${i}-${item.slice(0, 12)}`}>{inlineFormat(item)}</li>
              ))}
            </ul>
          );
        }
        if (/^\d+\.\s/.test(block)) {
          const items = block
            .split('\n')
            .map((line) => line.replace(/^\d+\.\s*/, '').trim())
            .filter(Boolean);
          return (
            <ol key={key}>
              {items.map((item, i) => (
                <li key={`${i}-${item.slice(0, 12)}`}>{inlineFormat(item)}</li>
              ))}
            </ol>
          );
        }
        if (block.startsWith('### ')) {
          return <h4 key={key}>{inlineFormat(block.slice(4))}</h4>;
        }
        return <p key={key}>{inlineFormat(block)}</p>;
      })}
    </div>
  );
}
