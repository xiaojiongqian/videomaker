import {
  filterContentByChannel,
  getFilterOptions,
  getTypeLabel,
  listAllPublishedContent,
  listPublishedContent,
  queryContent,
  sortContentItems,
} from './content-service.js';
import { renderMermaidDiagrams } from './diagram-renderer.js';
import { renderMarkdownDocument } from './markdown-renderer.js';

const DEFAULT_CHANNEL = 'ai';

const CHANNEL_CONFIGS = {
  ai: {
    label: 'AI时代',
    description: '支持筛选与检索的 AI 内容卡片列表。',
    indexHeading: 'AI时代',
    indexIntro: '支持按关键词、类型、主题与年份筛选已发布内容。',
    keywordPlaceholder: '输入标题、摘要或标签',
    typeFilterLabel: '类型',
    yearFilterVisible: true,
    resultUnit: '篇',
    emptyListText: 'AI时代频道暂无已发布内容。',
    emptyFilterText: '没有匹配结果，请尝试调整筛选条件。',
    footerLabel: 'AI时代',
  },
  novel: {
    label: '小说',
    description: '支持筛选与检索的小说章节列表。',
    indexHeading: '小说',
    indexIntro: '支持按关键词、系列与主题筛选已发布章节。',
    keywordPlaceholder: '输入章节标题、摘要或标签',
    typeFilterLabel: '系列',
    yearFilterVisible: false,
    resultUnit: '章',
    emptyListText: '小说频道暂无已发布章节。',
    emptyFilterText: '没有匹配章节，请尝试调整筛选条件。',
    footerLabel: '小说',
  },
};

function escapeHtml(value) {
  return String(value || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function formatDate(value) {
  const ts = Date.parse(value || '');
  if (Number.isNaN(ts)) {
    return value || '日期未知';
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(ts);
}

function getChannelConfig(channel) {
  return CHANNEL_CONFIGS[channel] || CHANNEL_CONFIGS[DEFAULT_CHANNEL];
}

function getRequestedChannel() {
  const params = new URLSearchParams(window.location.search);
  const requested = (params.get('channel') || '').trim();
  return requested && CHANNEL_CONFIGS[requested] ? requested : DEFAULT_CHANNEL;
}

function getChannelHref(channel) {
  if (channel === DEFAULT_CHANNEL) {
    return './index.html';
  }

  return `./index.html?channel=${encodeURIComponent(channel)}`;
}

function setMetaContent(selector, value) {
  const element = document.querySelector(selector);
  if (element) {
    element.setAttribute('content', value);
  }
}

function setPageMetadata(title, description, ogType) {
  document.title = title;
  setMetaContent('meta[name="description"]', description);
  setMetaContent('meta[property="og:title"]', title);
  setMetaContent('meta[property="og:description"]', description);

  if (ogType) {
    setMetaContent('meta[property="og:type"]', ogType);
  }
}

function applySiteChrome(channel, pageKind, item = null) {
  const config = getChannelConfig(channel);
  document.body.dataset.channel = channel;

  const brandEl = document.getElementById('siteBrand');
  if (brandEl) {
    brandEl.textContent = config.label;
    brandEl.href = getChannelHref(channel);
  }

  const footerEl = document.getElementById('siteFooterText');
  if (footerEl) {
    footerEl.textContent = `作者：Vik Qian · 版权所有 © 2026 ${config.footerLabel}`;
  }

  const navLinks = [
    ['navAi', 'ai', CHANNEL_CONFIGS.ai.label],
    ['navNovel', 'novel', CHANNEL_CONFIGS.novel.label],
  ];

  navLinks.forEach(([elementId, navChannel, label]) => {
    const link = document.getElementById(elementId);
    if (!link) {
      return;
    }

    link.textContent = label;
    link.href = getChannelHref(navChannel);
    if (navChannel === channel) {
      link.setAttribute('aria-current', 'page');
    } else {
      link.removeAttribute('aria-current');
    }
  });

  if (pageKind === 'index') {
    setPageMetadata(config.label, config.description, 'website');
    return;
  }

  if (item) {
    setPageMetadata(`${item.title} - ${config.label}`, item.summary || config.description, 'article');
    return;
  }

  setPageMetadata(`详情页 - ${config.label}`, `${config.label}内容详情页。`, 'article');
}

function getItemTypeLabel(item) {
  return item.typeLabel || getTypeLabel(item.type);
}

function buildTypeLabelMap(items) {
  const map = new Map();

  items.forEach((item) => {
    if (!item.type) {
      return;
    }

    map.set(item.type, getItemTypeLabel(item));
  });

  return map;
}

function getItemListMeta(item) {
  if (item.channel === 'novel') {
    const parts = [];
    if (Number.isFinite(item.sequence)) {
      parts.push(`第${item.sequence}章`);
    }

    if (item.topic.length) {
      parts.push(item.topic.join(' / '));
    }

    return parts.join(' · ') || '小说章节';
  }

  const topics = item.topic.length ? item.topic.join(' / ') : '未分类';
  return `${formatDate(item.date || item.updatedAt)} · ${topics}`;
}

function getPostMetaText(item) {
  if (item.channel === 'novel') {
    const parts = ['小说'];
    const typeLabel = getItemTypeLabel(item);

    if (typeLabel) {
      parts.push(typeLabel);
    }

    if (Number.isFinite(item.sequence)) {
      parts.push(`第${item.sequence}章`);
    }

    return parts.join(' · ');
  }

  const topics = item.topic.length ? item.topic.join(' / ') : '未分类';
  return `${getItemTypeLabel(item)} · ${formatDate(item.date || item.updatedAt)} · ${topics}`;
}

function getPostHref(item) {
  const page = typeof item.page === 'string' ? item.page.trim() : '';
  if (page) {
    return page;
  }
  return `./post.html?id=${encodeURIComponent(item.id)}`;
}

function renderCard(item) {
  const href = getPostHref(item);

  return `
    <article class="card">
      <span class="pill">${escapeHtml(getItemTypeLabel(item))}</span>
      <h3><a href="${href}">${escapeHtml(item.title)}</a></h3>
      <p>${escapeHtml(item.summary || '暂无摘要')}</p>
      <p class="muted">${escapeHtml(getItemListMeta(item))}</p>
    </article>
  `;
}

function renderEmptyState(container, text) {
  container.innerHTML = `
    <article class="card empty-state">
      <h3>暂无内容</h3>
      <p class="muted">${escapeHtml(text)}</p>
    </article>
  `;
}

function updateSelectOptions(selectEl, values, formatter = (value) => value) {
  selectEl.querySelectorAll('option[data-dynamic="true"]').forEach((option) => option.remove());

  values.forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = formatter(value);
    option.dataset.dynamic = 'true';
    selectEl.append(option);
  });
}

function applyIndexPageLabels(channel) {
  const config = getChannelConfig(channel);
  const headingEl = document.getElementById('all-title');
  const introEl = document.getElementById('channelDescription');
  const keywordInput = document.getElementById('keyword');
  const typeLabelEl = document.querySelector('label[for="type"]');
  const yearFieldEl = document.querySelector('[data-filter-field="year"]');

  if (headingEl) {
    headingEl.textContent = config.indexHeading;
  }

  if (introEl) {
    introEl.textContent = config.indexIntro;
  }

  if (keywordInput) {
    keywordInput.placeholder = config.keywordPlaceholder;
  }

  if (typeLabelEl) {
    typeLabelEl.textContent = config.typeFilterLabel;
  }

  if (yearFieldEl) {
    yearFieldEl.hidden = !config.yearFilterVisible;
  }
}

async function initIndexPage() {
  const contentListEl = document.getElementById('contentList');
  const resultMetaEl = document.getElementById('resultMeta');
  const channel = getRequestedChannel();
  const config = getChannelConfig(channel);
  const keywordInput = document.getElementById('keyword');
  const typeSelect = document.getElementById('type');
  const topicSelect = document.getElementById('topic');
  const yearSelect = document.getElementById('year');

  applySiteChrome(channel, 'index');
  applyIndexPageLabels(channel);

  try {
    const published = await listPublishedContent(channel);

    if (!published.length) {
      renderEmptyState(contentListEl, config.emptyListText);
      resultMetaEl.textContent = `已发布 0 ${config.resultUnit}`;
      return;
    }

    const filters = getFilterOptions(published);
    const typeLabels = buildTypeLabelMap(published);
    updateSelectOptions(typeSelect, filters.types, (value) => typeLabels.get(value) || getTypeLabel(value));
    updateSelectOptions(topicSelect, filters.topics);
    updateSelectOptions(yearSelect, filters.years);

    if (!config.yearFilterVisible) {
      yearSelect.value = '';
    }

    const applyFilters = () => {
      const filtered = queryContent(published, {
        keyword: keywordInput.value,
        type: typeSelect.value,
        topic: topicSelect.value,
        year: config.yearFilterVisible ? yearSelect.value : '',
      });

      if (!filtered.length) {
        renderEmptyState(contentListEl, config.emptyFilterText);
      } else {
        contentListEl.innerHTML = filtered.map(renderCard).join('');
      }

      resultMetaEl.textContent = `共 ${filtered.length} ${config.resultUnit}（已发布总数 ${published.length} ${config.resultUnit}）`;
    };

    [keywordInput, typeSelect, topicSelect, yearSelect].forEach((element) => {
      element.addEventListener('input', applyFilters);
      element.addEventListener('change', applyFilters);
    });

    applyFilters();
  } catch (error) {
    console.error(error);
    renderEmptyState(contentListEl, '加载失败，请稍后重试。');
    resultMetaEl.textContent = '内容加载失败';
  }
}

function renderToc(tocItems) {
  const tocList = document.getElementById('tocList');
  const topLevelItems = tocItems.filter((item) => item.level === 2);

  if (!topLevelItems.length) {
    tocList.innerHTML = '<li class="muted">暂无目录</li>';
    return;
  }

  tocList.innerHTML = topLevelItems
    .map((item) => {
      return `<li data-level="${item.level}"><a href="#${escapeHtml(item.id)}">${escapeHtml(item.text)}</a></li>`;
    })
    .join('');
}

function initTocActiveState() {
  const tocList = document.getElementById('tocList');
  if (!tocList) {
    return;
  }

  const links = [...tocList.querySelectorAll('a[href^="#"]')];
  if (!links.length) {
    return;
  }

  const records = links
    .map((link) => {
      let targetId = (link.getAttribute('href') || '').replace('#', '');
      try {
        targetId = decodeURIComponent(targetId);
      } catch {
        // Keep original anchor id when decoding fails.
      }
      return {
        link,
        item: link.closest('li'),
        target: document.getElementById(targetId),
      };
    })
    .filter((record) => record.target);

  if (!records.length) {
    return;
  }

  const clearActive = () => {
    records.forEach((record) => {
      record.link.classList.remove('is-active');
      record.item?.classList.remove('is-active');
    });
  };

  const setActiveById = (id) => {
    clearActive();
    const active = records.find((record) => record.target.id === id);
    if (!active) {
      return;
    }
    active.link.classList.add('is-active');
    active.item?.classList.add('is-active');
  };

  setActiveById(records[0].target.id);

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

      if (visible.length) {
        setActiveById(visible[0].target.id);
        return;
      }

      const passed = records
        .map((record) => record.target)
        .filter((target) => target.getBoundingClientRect().top <= 140);

      if (passed.length) {
        setActiveById(passed[passed.length - 1].id);
      }
    },
    {
      rootMargin: '-20% 0px -60% 0px',
      threshold: [0, 1],
    }
  );

  records.forEach((record) => observer.observe(record.target));
}

const TOC_WIDTH_STORAGE_KEY = 'content-site.toc.width';

function initTocResizer() {
  const layout = document.querySelector('.post-layout');
  const tocEl = document.querySelector('.toc');
  const resizerEl = document.getElementById('tocResizer');
  if (!layout || !tocEl || !resizerEl) {
    return;
  }

  const desktopMedia = window.matchMedia('(min-width: 1024px)');
  const clampWidth = (value) => Math.max(220, Math.min(420, Math.round(value)));
  const readStoredWidth = () => {
    try {
      return Number.parseInt(localStorage.getItem(TOC_WIDTH_STORAGE_KEY) || '', 10);
    } catch {
      return Number.NaN;
    }
  };
  const writeStoredWidth = (value) => {
    try {
      localStorage.setItem(TOC_WIDTH_STORAGE_KEY, String(value));
    } catch {
      // Ignore storage failures and keep runtime behavior.
    }
  };
  const applyWidth = (value) => {
    const next = clampWidth(value);
    layout.style.setProperty('--toc-width', `${next}px`);
    return next;
  };

  const applyStoredWidth = () => {
    if (!desktopMedia.matches) {
      layout.style.removeProperty('--toc-width');
      return;
    }
    const stored = readStoredWidth();
    if (Number.isFinite(stored)) {
      applyWidth(stored);
    }
  };

  applyStoredWidth();
  desktopMedia.addEventListener('change', applyStoredWidth);

  let dragging = false;
  let activePointerId = null;
  let startX = 0;
  let startWidth = 0;

  const stopDragging = () => {
    dragging = false;
    activePointerId = null;
    resizerEl.classList.remove('is-dragging');
  };

  resizerEl.addEventListener('pointerdown', (event) => {
    if (!desktopMedia.matches) {
      return;
    }
    dragging = true;
    activePointerId = event.pointerId;
    startX = event.clientX;
    startWidth = tocEl.getBoundingClientRect().width;
    resizerEl.classList.add('is-dragging');
    resizerEl.setPointerCapture(event.pointerId);
    event.preventDefault();
  });

  resizerEl.addEventListener('pointermove', (event) => {
    if (!dragging || event.pointerId !== activePointerId) {
      return;
    }
    const width = applyWidth(startWidth + (event.clientX - startX));
    writeStoredWidth(width);
  });

  resizerEl.addEventListener('pointerup', (event) => {
    if (event.pointerId !== activePointerId) {
      return;
    }
    stopDragging();
  });

  resizerEl.addEventListener('pointercancel', stopDragging);
  resizerEl.addEventListener('lostpointercapture', stopDragging);

  resizerEl.addEventListener('keydown', (event) => {
    if (!desktopMedia.matches) {
      return;
    }
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') {
      return;
    }
    event.preventDefault();
    const delta = event.key === 'ArrowRight' ? 16 : -16;
    const width = applyWidth(tocEl.getBoundingClientRect().width + delta);
    writeStoredWidth(width);
  });
}

function renderPostNavigation(items, currentIndex) {
  const navEl = document.getElementById('postNav');
  const links = [];

  if (currentIndex > 0) {
    const prev = items[currentIndex - 1];
    links.push(
      `<a class="chip" href="${escapeHtml(getPostHref(prev))}">← ${escapeHtml(prev.title)}</a>`
    );
  }

  if (currentIndex < items.length - 1) {
    const next = items[currentIndex + 1];
    links.push(
      `<a class="chip" href="${escapeHtml(getPostHref(next))}">${escapeHtml(next.title)} →</a>`
    );
  }

  navEl.innerHTML = links.length ? links.join('') : '<span class="muted">没有更多内容</span>';
}

async function initPostPage() {
  const postTitleEl = document.getElementById('post-title');
  const postMetaEl = document.getElementById('postMeta');
  const postSummaryEl = document.getElementById('postSummary');
  const postContentEl = document.getElementById('postContent');
  const requestedChannel = getRequestedChannel();
  applySiteChrome(requestedChannel, 'post');
  initTocResizer();

  try {
    const published = await listAllPublishedContent();
    if (!published.length) {
      postTitleEl.textContent = '暂无可阅读内容';
      postMetaEl.textContent = '请先发布内容。';
      postContentEl.innerHTML = '<div class="note">content-index.json 中没有 published 内容。</div>';
      renderToc([]);
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const requestedId = params.get('id');
    const requestedItem = requestedId ? published.find((item) => item.id === requestedId) : null;

    if (requestedId && !requestedItem) {
      postTitleEl.textContent = '内容不存在或未发布';
      postMetaEl.textContent = `未找到 id=${requestedId}`;
      postContentEl.innerHTML =
        '<div class="note">请返回首页重新选择内容，或确认 id 对应内容状态为 published。</div>';
      renderToc([]);
      return;
    }

    const channel = requestedItem?.channel || requestedChannel;
    const channelItems = sortContentItems(filterContentByChannel(published, channel), channel);
    if (!channelItems.length) {
      postTitleEl.textContent = '暂无可阅读内容';
      postMetaEl.textContent = `${getChannelConfig(channel).label}频道暂无已发布内容。`;
      postContentEl.innerHTML = '<div class="note">当前频道没有可阅读内容。</div>';
      renderToc([]);
      return;
    }

    const currentIndex = requestedItem
      ? channelItems.findIndex((item) => item.id === requestedItem.id)
      : 0;
    const item = requestedItem || channelItems[0];
    applySiteChrome(item.channel, 'post', item);

    postTitleEl.textContent = item.title;
    postMetaEl.textContent = getPostMetaText(item);
    postSummaryEl.textContent = item.summary || '';

    const { html, toc } = await renderMarkdownDocument(item.source);
    postContentEl.innerHTML = html;
    await renderMermaidDiagrams(postContentEl);
    renderToc(toc);
    initTocActiveState();
    renderPostNavigation(channelItems, currentIndex < 0 ? 0 : currentIndex);
  } catch (error) {
    console.error(error);
    postTitleEl.textContent = '加载失败';
    postMetaEl.textContent = '无法读取详情内容';
    postContentEl.innerHTML = `<div class="note">${escapeHtml(error.message)}</div>`;
    renderToc([]);
  }
}

function bootstrap() {
  const page = document.body.dataset.page;

  if (page === 'index') {
    initIndexPage();
  }

  if (page === 'post') {
    initPostPage();
  }
}

bootstrap();
