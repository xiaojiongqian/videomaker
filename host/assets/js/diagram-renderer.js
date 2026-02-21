const MERMAID_SELECTOR = '.mermaid';
const MERMAID_MODULE_URL = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
let mermaidInstancePromise = null;

function isRenderableRoot(root) {
  return root instanceof Document || root instanceof Element;
}

async function loadMermaid() {
  if (!mermaidInstancePromise) {
    mermaidInstancePromise = import(MERMAID_MODULE_URL).then((module) => {
      const mermaid = module.default || module.mermaid || module;
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: 'neutral',
      });
      return mermaid;
    });
  }

  return mermaidInstancePromise;
}

export async function renderMermaidDiagrams(root = document) {
  const scope = isRenderableRoot(root) ? root : document;
  const nodes = [...scope.querySelectorAll(MERMAID_SELECTOR)].filter(
    (node) => node.dataset.mermaidRendered !== 'true'
  );

  if (!nodes.length) {
    return;
  }

  nodes.forEach((node) => {
    node.dataset.mermaidRendered = 'pending';
  });

  try {
    const mermaid = await loadMermaid();
    await mermaid.run({
      nodes,
      suppressErrors: true,
    });

    nodes.forEach((node) => {
      node.dataset.mermaidRendered = 'true';
    });
  } catch (error) {
    console.warn('Mermaid 渲染失败，已回退为源码展示。', error);
    nodes.forEach((node) => {
      node.dataset.mermaidRendered = 'fallback';
      node.classList.add('mermaid-fallback');
    });
  }
}
