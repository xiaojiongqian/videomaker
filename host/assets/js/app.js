import {
  getFilterOptions,
  getTypeLabel,
  listPublishedContent,
  queryContent,
} from './content-service.js';
import { renderMarkdownDocument } from './markdown-renderer.js';

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

function renderCard(item) {
  const href = `./post.html?id=${encodeURIComponent(item.id)}`;
  const topics = item.topic.length ? item.topic.join(' / ') : '未分类';

  return `
    <article class="card">
      <span class="pill">${escapeHtml(getTypeLabel(item.type))}</span>
      <h3><a href="${href}">${escapeHtml(item.title)}</a></h3>
      <p>${escapeHtml(item.summary || '暂无摘要')}</p>
      <p class="muted">${escapeHtml(formatDate(item.date || item.updatedAt))} · ${escapeHtml(topics)}</p>
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

async function initIndexPage() {
  const contentListEl = document.getElementById('contentList');
  const resultMetaEl = document.getElementById('resultMeta');

  const keywordInput = document.getElementById('keyword');
  const typeSelect = document.getElementById('type');
  const topicSelect = document.getElementById('topic');
  const yearSelect = document.getElementById('year');

  try {
    const published = await listPublishedContent();

    if (!published.length) {
      renderEmptyState(contentListEl, '请先在 content-index.json 中将内容状态设为 published。');
      resultMetaEl.textContent = '已发布内容 0 篇';
      return;
    }

    const filters = getFilterOptions(published);
    updateSelectOptions(typeSelect, filters.types, getTypeLabel);
    updateSelectOptions(topicSelect, filters.topics);
    updateSelectOptions(yearSelect, filters.years);

    const applyFilters = () => {
      const filtered = queryContent(published, {
        keyword: keywordInput.value,
        type: typeSelect.value,
        topic: topicSelect.value,
        year: yearSelect.value,
      });

      if (!filtered.length) {
        renderEmptyState(contentListEl, '没有匹配结果，请尝试调整筛选条件。');
      } else {
        contentListEl.innerHTML = filtered.map(renderCard).join('');
      }

      resultMetaEl.textContent = `共 ${filtered.length} 篇内容（已发布总数 ${published.length}）`;
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

  if (!tocItems.length) {
    tocList.innerHTML = '<li class="muted">暂无目录</li>';
    return;
  }

  tocList.innerHTML = tocItems
    .map((item) => {
      return `<li data-level="${item.level}"><a href="#${escapeHtml(item.id)}">${escapeHtml(item.text)}</a></li>`;
    })
    .join('');
}

function renderPostNavigation(items, currentIndex) {
  const navEl = document.getElementById('postNav');
  const links = [];

  if (currentIndex > 0) {
    const prev = items[currentIndex - 1];
    links.push(
      `<a class="chip" href="./post.html?id=${encodeURIComponent(prev.id)}">← ${escapeHtml(prev.title)}</a>`
    );
  }

  if (currentIndex < items.length - 1) {
    const next = items[currentIndex + 1];
    links.push(
      `<a class="chip" href="./post.html?id=${encodeURIComponent(next.id)}">${escapeHtml(next.title)} →</a>`
    );
  }

  navEl.innerHTML = links.length ? links.join('') : '<span class="muted">没有更多内容</span>';
}

async function initPostPage() {
  const postTitleEl = document.getElementById('post-title');
  const postMetaEl = document.getElementById('postMeta');
  const postSummaryEl = document.getElementById('postSummary');
  const postContentEl = document.getElementById('postContent');

  try {
    const published = await listPublishedContent();
    if (!published.length) {
      postTitleEl.textContent = '暂无可阅读内容';
      postMetaEl.textContent = '请先发布内容。';
      postContentEl.innerHTML = '<div class="note">content-index.json 中没有 published 内容。</div>';
      renderToc([]);
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const requestedId = params.get('id');
    const currentIndex = requestedId ? published.findIndex((item) => item.id === requestedId) : 0;

    if (requestedId && currentIndex < 0) {
      postTitleEl.textContent = '内容不存在或未发布';
      postMetaEl.textContent = `未找到 id=${requestedId}`;
      postContentEl.innerHTML =
        '<div class="note">请返回首页重新选择内容，或确认 id 对应内容状态为 published。</div>';
      renderToc([]);
      return;
    }

    const item = published[currentIndex < 0 ? 0 : currentIndex];
    const topics = item.topic.length ? item.topic.join(' / ') : '未分类';

    document.title = `${item.title} - AI时代`;

    postTitleEl.textContent = item.title;
    postMetaEl.textContent = `${getTypeLabel(item.type)} · ${formatDate(item.date || item.updatedAt)} · ${topics}`;
    postSummaryEl.textContent = item.summary || '';

    const { html, toc } = await renderMarkdownDocument(item.source);
    postContentEl.innerHTML = html;
    renderToc(toc);
    renderPostNavigation(published, currentIndex < 0 ? 0 : currentIndex);
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
