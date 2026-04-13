const INDEX_URL = "./data/content-index.json";
const DEFAULT_CHANNEL = "ai";

const TYPE_LABELS = {
  article: "文章",
  "video-note": "视频总结",
  "audio-note": "音频总结",
};

let indexCache;

function normalizeItem(item) {
  const topics = Array.isArray(item.topic) ? item.topic : [];
  const date = item.date || item.updatedAt || "";
  const sequence = Number.parseInt(String(item.sequence || ""), 10);

  return {
    ...item,
    channel: item.channel || DEFAULT_CHANNEL,
    language: item.language || "zh-CN",
    topic: topics,
    type: item.type || "article",
    typeLabel: item.typeLabel || "",
    status: item.status || "draft",
    date,
    sequence: Number.isFinite(sequence) ? sequence : null,
    summary: item.summary || "",
    seriesTitle: item.seriesTitle || "",
    chapterId: item.chapterId || "",
    updatedAt: item.updatedAt || date,
    searchableText: [
      item.title || "",
      item.summary || "",
      topics.join(" "),
      item.type || "",
      item.typeLabel || "",
      item.seriesTitle || "",
      item.chapterId || "",
    ]
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

function sortNovel(items) {
  return [...items].sort((a, b) => {
    const aSeries = String(a.typeLabel || a.seriesTitle || a.type || "");
    const bSeries = String(b.typeLabel || b.seriesTitle || b.type || "");
    const seriesCompare = aSeries.localeCompare(bSeries, "zh-CN");
    if (seriesCompare !== 0) {
      return seriesCompare;
    }

    const aSequence = Number.isFinite(a.sequence) ? a.sequence : Number.MAX_SAFE_INTEGER;
    const bSequence = Number.isFinite(b.sequence) ? b.sequence : Number.MAX_SAFE_INTEGER;

    if (aSequence !== bSequence) {
      return aSequence - bSequence;
    }

    return String(a.title || "").localeCompare(String(b.title || ""), "zh-CN");
  });
}

export function sortContentItems(items, channel = "") {
  if (channel === "novel") {
    return sortNovel(items);
  }

  return sortByRecent(items);
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

export async function listAllPublishedContent() {
  const list = await loadContentIndex();
  return list.filter((item) => item.status === "published");
}

export function filterContentByChannel(items, channel = "") {
  if (!channel) {
    return [...items];
  }

  return items.filter((item) => item.channel === channel);
}

export async function listPublishedContent(channel = "") {
  const list = await listAllPublishedContent();
  return sortContentItems(filterContentByChannel(list, channel), channel);
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
