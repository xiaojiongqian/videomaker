const INDEX_URL = "./data/content-index.json";

const TYPE_LABELS = {
  article: "文章",
  "video-note": "视频总结",
  "audio-note": "音频总结",
};

let indexCache;

function normalizeItem(item) {
  const topics = Array.isArray(item.topic) ? item.topic : [];
  const date = item.date || item.updatedAt || "";

  return {
    ...item,
    topic: topics,
    type: item.type || "article",
    status: item.status || "draft",
    date,
    summary: item.summary || "",
    updatedAt: item.updatedAt || date,
    searchableText: [item.title || "", item.summary || "", topics.join(" "), item.type || ""]
      .join(" ")
      .toLowerCase(),
  };
}

function getSortTimestamp(item) {
  const value = item.date || item.updatedAt;
  const ts = Date.parse(value);
  return Number.isNaN(ts) ? 0 : ts;
}

function sortByRecent(items) {
  return [...items].sort((a, b) => getSortTimestamp(b) - getSortTimestamp(a));
}

export async function loadContentIndex() {
  if (indexCache) {
    return indexCache;
  }

  const response = await fetch(INDEX_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`无法加载内容索引：${response.status}`);
  }

  const json = await response.json();
  indexCache = Array.isArray(json) ? json.map(normalizeItem) : [];
  return indexCache;
}

export async function listPublishedContent() {
  const list = await loadContentIndex();
  return sortByRecent(list.filter((item) => item.status === "published"));
}

export function getTypeLabel(type) {
  return TYPE_LABELS[type] || type || "未分类";
}

export function getYear(item) {
  const value = item.date || item.updatedAt || "";
  return value.slice(0, 4);
}

export function getFilterOptions(items) {
  const types = new Set();
  const topics = new Set();
  const years = new Set();

  items.forEach((item) => {
    if (item.type) {
      types.add(item.type);
    }

    item.topic.forEach((topic) => topics.add(topic));

    const year = getYear(item);
    if (year) {
      years.add(year);
    }
  });

  return {
    types: [...types],
    topics: [...topics],
    years: [...years].sort((a, b) => b.localeCompare(a)),
  };
}

export function queryContent(items, filters) {
  const keyword = (filters.keyword || "").trim().toLowerCase();
  const type = filters.type || "";
  const topic = filters.topic || "";
  const year = filters.year || "";

  return items.filter((item) => {
    if (type && item.type !== type) {
      return false;
    }

    if (topic && !item.topic.includes(topic)) {
      return false;
    }

    if (year && getYear(item) !== year) {
      return false;
    }

    if (keyword && !item.searchableText.includes(keyword)) {
      return false;
    }

    return true;
  });
}
