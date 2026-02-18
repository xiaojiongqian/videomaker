import { marked } from "../vendor/marked.esm.js";
import DOMPurify from "../vendor/purify.es.mjs";

marked.setOptions({
  gfm: true,
  breaks: false,
  mangle: false,
  headerIds: false,
});

function isExternalReference(value) {
  return /^(?:[a-z][a-z0-9+.-]*:|#|\/\/)/i.test(value);
}

function rewriteRelativeUrls(root, sourceUrl) {
  root.querySelectorAll("img[src], a[href]").forEach((element) => {
    const attr = element.tagName === "IMG" ? "src" : "href";
    const value = element.getAttribute(attr) || "";

    let resolved = value;
    if (value && !isExternalReference(value)) {
      resolved = new URL(value, sourceUrl).toString();
      element.setAttribute(attr, resolved);
    }

    if (element.tagName === "IMG") {
      element.setAttribute("loading", "lazy");
      element.setAttribute("decoding", "async");
    } else if (element.tagName === "A") {
      try {
        const url = new URL(resolved, sourceUrl);
        const isHttp = url.protocol === "http:" || url.protocol === "https:";
        const sameOrigin = url.origin === window.location.origin;
        if (isHttp && !sameOrigin) {
          element.setAttribute("target", "_blank");
          element.setAttribute("rel", "noopener noreferrer");
        }
      } catch {
        // Ignore malformed links and keep the sanitized output.
      }
    }
  });
}

function slugifyHeading(text) {
  const normalized = text
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");

  return normalized || "section";
}

function assignHeadingIds(root) {
  const idCounter = new Map();
  const toc = [];

  root.querySelectorAll("h2, h3").forEach((heading) => {
    const text = heading.textContent ? heading.textContent.trim() : "";
    const baseId = slugifyHeading(text);
    const count = idCounter.get(baseId) || 0;
    const nextCount = count + 1;
    idCounter.set(baseId, nextCount);

    const finalId = nextCount === 1 ? baseId : `${baseId}-${nextCount}`;
    heading.id = finalId;

    toc.push({
      id: finalId,
      text,
      level: heading.tagName === "H2" ? 2 : 3,
    });
  });

  return toc;
}

export async function renderMarkdownDocument(sourcePath) {
  const sourceUrl = new URL(sourcePath, window.location.href);
  const response = await fetch(sourceUrl, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`无法读取文档：${response.status}`);
  }

  const markdown = await response.text();
  const rendered = marked.parse(markdown);
  const safeHtml = DOMPurify.sanitize(rendered, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ["script", "style", "iframe", "object", "embed"],
  });

  const template = document.createElement("template");
  template.innerHTML = safeHtml;

  const wrapper = document.createElement("div");
  wrapper.append(template.content);

  rewriteRelativeUrls(wrapper, sourceUrl);
  const toc = assignHeadingIds(wrapper);

  return {
    html: wrapper.innerHTML,
    toc,
  };
}
