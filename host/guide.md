# AI时代 发布站点设计文档（GitHub Pages）

## 1. 项目目标

构建一个**轻量化、纯前端、可长期维护**的内容发布站点，部署在 GitHub Pages，集中展示当前工程中可公开发表的内容，并通过清晰结构与高质量视觉设计提升阅读与浏览体验。

### 1.1 核心目标
- 内容统一发布：文章、视频总结、音频总结统一入口。
- 组织有机：按主题、系列、时间多维组织，而不是只按文件夹。
- 视觉友好：现代、克制、可读性强，兼顾移动端。
- 零后端依赖：完全静态资源，适配 GitHub Pages 免费托管。

### 1.2 非目标
- 不做账号系统/评论系统/在线编辑后台。
- 不做复杂服务端检索（仅前端本地索引搜索）。

---

## 2. 当前工程内容盘点与发布范围

## 2.1 建议纳入发布的内容（白名单）
1. 文章：`articals/**.md`
2. 视频文档：`video/**/doc/*_sum.md`
3. 音频文档：`audio/**/doc/*_sum.md`
4. 配图资源：与上述 Markdown 紧邻的 `images/` 目录

## 2.2 默认不直接展示的内容（灰名单）
- `*.srt`（可作为“下载附件”而非正文内容）
- `scripts/**`（内部脚本，除非单独写成教程）
- 中间产物 `*.json` / `*.sh`（可按需作为附录链接）

---

## 3. 信息架构（IA）

采用“主题 + 类型 + 时间”三维组织。

- 首页 `/`
  - Hero（站点定位）
  - 最新发布（按时间倒序）
  - 内容列表（含筛选/搜索）
  - 主题入口（AI 编程、习惯成长、Vibe Coding 等）
  - 精选长文
- 详情页 `/post/:slug`
  - Markdown 渲染正文
  - 目录（TOC）
  - 上一篇/下一篇
  - 关联内容推荐

说明：为保证 KISS/SOLID/DRY，当前版本只保留“首页 + 详情页”两页结构。

---

## 4. 内容模型设计

采用“**一个索引文件集中管理**”的极简方案：所有可发布内容统一登记在 `host/data/content-index.json`。

### 4.1 最小字段（建议）

每篇内容至少包含以下字段：

```json
{
  "id": "ai-coding-evolution",
  "title": "AI 编程的三个阶段",
  "source": "articals/coding-evolution/ai-coding-evolution.md",
  "status": "published",
  "updatedAt": "2026-02-17"
}
```

字段说明：
- `id`：唯一标识，同时可作为页面 `slug`。
- `title`：展示标题。
- `source`：仓库内 Markdown 路径（前端按需加载渲染）。
- `status`：上/下架状态（见下文）。
- `updatedAt`：最近更新时间（用于排序和管理）。

### 4.2 状态机制（保持简单）

只使用 3 个状态：
- `draft`：草稿，不展示。
- `published`：已上架，前台可见。
- `hidden`：已下架但保留，不展示。

前端展示规则：
- 首页列表模块与搜索模块**仅展示 `published`**。

日常操作：
- 上架：将 `status` 改为 `published`。
- 下架：将 `status` 改为 `hidden`（不删文件，方便恢复）。

说明：
- 目前不启用 `archived`，避免管理复杂化；后续若内容规模扩大再引入。

### 4.3 可选扩展字段（需要时再加）

为了支持更丰富的浏览体验，可按需增加：
- `type`：`article` / `video-note` / `audio-note`
- `topic`：主题标签数组
- `date`：内容发布日期（YYYY-MM-DD）
- `summary`：列表摘要
- `cover`：封面图片路径

---

## 5. 前端技术方案（纯前端、轻量）

## 5.1 技术选型
- HTML + CSS + 原生 ES Modules（无重型框架）
- Markdown 渲染：`marked`（浏览器端）
- 安全净化：`DOMPurify`
- 搜索：前端本地索引（可选 `Fuse.js`，也可先做原生 includes）

## 5.2 目录建议（host）

```text
host/
  index.html
  post.html
  assets/
    css/
      base.css
      theme.css
      components.css
    js/
      app.js
      content-service.js
      markdown-renderer.js
    vendor/
      marked.esm.js
      purify.es.mjs
  data/
    content-index.json
  guide.md
```

## 5.3 运行与部署原则
- 本地预览可用任意静态服务器。
- 线上仅发布 `host/` 目录静态文件。
- 不依赖 Node 服务端，不依赖数据库。

### 5.4 行业最佳实践架构（本项目采用）

采用“**Markdown 单一内容源 + 前端统一渲染**”的常规最佳实践：

1. 内容源：直接引用仓库中的 Markdown 和 images，不手工复制/维护第二份 HTML。
2. 内容管理：用 `host/data/content-index.json` 集中管理上/下架与顺序。
3. 渲染流程：`fetch markdown -> parser 渲染 -> DOMPurify 安全净化 -> TOC/锚点增强 -> 挂载页面`。
4. 样式控制：通过统一 CSS（排版、间距、代码块、图片）保证视觉一致性。
5. 安全边界：Markdown 渲染后必须做白名单净化，禁止不受控 HTML 注入。

这套架构的定位是：**先用最小复杂度实现高可维护性**，后续按需升级能力。

### 5.5 可控渲染规则（CSS 之外）

为保证 HTML 渲染可控性，约束分为三层：
- 渲染层（结构）：通过 `marked` 的 renderer 统一定义标题、链接、图片、代码块等输出结构。
- 安全层（边界）：使用 `DOMPurify` 统一做标签/属性白名单过滤。
- 样式层（视觉）：通过 `base.css/theme.css/components.css` 统一阅读体验。

结论：CSS 只负责“好不好看”；渲染器决定“长什么样”；净化策略决定“安不安全”。

### 5.6 后续升级路径（保持同一内容源）

当站点规模或 SEO 要求提升时，可升级为“**构建时预渲染 HTML**”：
- 仍以 Markdown 为唯一内容源（不人工维护两份内容）。
- 在 GitHub Actions 中自动生成静态 HTML 再发布。
- 适用于更高的首屏速度、抓取稳定性和大规模内容场景。

---

## 6. 视觉与交互设计规范

## 6.1 视觉关键词
- 现代、清爽、内容优先
- 留白充足、层级分明、低噪声
- 以阅读体验为核心而非炫技

## 6.2 设计令牌（建议）
- 主色：`#4F46E5`（Indigo）
- 强调色：`#06B6D4`（Cyan）
- 背景：`#F8FAFC` / 深色 `#0B1120`
- 正文色：`#0F172A` / 深色 `#E2E8F0`
- 字体：中文 `PingFang SC` / `Noto Sans SC`，英文 `Inter`
- 阅读宽度：正文容器 `72ch`，保障长文舒适度

## 6.3 组件风格
- 卡片：轻阴影 + 圆角（12px）+ hover 微动效
- 导航：顶部吸附，滚动后半透明毛玻璃
- 详情页：左侧目录（桌面）/ 顶部折叠目录（移动端）
- 图片：统一圆角与比例策略，支持点击放大

## 6.4 响应式断点
- Mobile: `<768px`
- Tablet: `768px~1023px`
- Desktop: `>=1024px`

---

## 7. 可用性、性能与 SEO

## 7.1 可访问性（A11y）
- 语义化标签（`main` / `article` / `nav`）
- 键盘可达与焦点样式
- 对比度符合 WCAG AA
- 图片必须包含 alt

## 7.2 性能预算
- 首屏关键资源（CSS+JS）目标 `<200KB`（gzip）
- 图片优先 WebP/AVIF，超大图延迟加载
- 正文页按需加载 Markdown 与图片

## 7.3 SEO（静态站可做）
- 每页唯一 `title` 与 `description`
- Open Graph / Twitter Card 元信息
- `sitemap.xml` 与 `robots.txt`
- 结构化数据（Article，后续可加）

---

## 8. GitHub Pages 部署方案

推荐使用 **GitHub Actions + Pages**：

1. 仓库 Settings → Pages → Source 选择 “GitHub Actions”
2. 工作流先构建 `_site/`，再将 `_site/` 作为发布产物
3. 推送到主分支后自动部署

工作流要点：
- 使用 `scripts/prepare_pages_bundle.py` 生成 `_site/`（部署产物）
- 在构建阶段自动同步 Markdown/图片到 `_site/content/`，并重写索引中的 `source/cover`
- 上传 `_site/` 目录为 Pages artifact，再执行部署

> 若仓库为 `username.github.io`：站点根路径为 `/`
> 若仓库为普通项目仓库：站点根路径通常为 `/<repo-name>/`（例如 `/videomaker/`）

---

## 9. 实施里程碑（含状态与补充要求）

### M1（1-2 天）
- 状态：已完成（2026-02-18）
- 输入：
  - 本设计文档（信息架构、视觉规范）
  - 白名单内容路径约定（`articals/`、`video/**/doc/`、`audio/**/doc/`）
- 工作：
  - 固化 IA 与页面路由（首页/详情页）
  - 搭建基础页面骨架与公共布局（导航、页脚、主容器）
  - 建立视觉主题变量与基础排版样式
- 输出：
  - 页面骨架文件：`host/index.html`、`host/post.html`
  - 样式基础文件：`host/assets/css/base.css`、`host/assets/css/theme.css`、`host/assets/css/components.css`
- 验证（阶段验收）：
  - 首页与详情页本地可访问，无 404、无明显布局错乱
  - 在 `<768px` 移动端宽度下可正常浏览（无横向滚动）
  - 首页与详情页具备可用的占位结构（非空白页）

### M2（1-2 天）
- 状态：已完成（2026-02-18）
- 输入：
  - M1 的页面骨架与样式
  - 待发布 Markdown 与图片资源
- 工作：
  - 建立并接入 `host/data/content-index.json`（集中管理内容状态）
  - 完成首页内容加载、筛选、搜索与详情路由联动
  - 打通 Markdown 渲染链路（parser + sanitize + TOC）
- 输出：
  - 可维护的内容索引文件（至少含 `id/title/source/status/updatedAt`）
  - 内容服务与渲染逻辑：`app.js`、`content-service.js`、`markdown-renderer.js`
  - 首页列表模块与详情页数据联动可用
- 验证（阶段验收）：
  - 首页列表仅展示 `status=published` 的内容
  - 支持按主题/类型/时间（或等价字段）浏览
  - 抽检至少 3 篇内容：Markdown 正常渲染，图片与相对链接可用
  - 详情页目录（TOC）可用，页面无阻断级脚本错误
- 实施状态补充：
  - 首页已落地：最新发布 + 全量列表 + 关键词/类型/主题/年份筛选
  - 详情页已落地：`post.html?id=<content-id>`、Markdown 渲染、TOC、上一篇/下一篇
  - 渲染链路已落地：`marked` -> `DOMPurify` -> 相对链接/图片重写 -> 标题锚点与 TOC
  - 数据源已落地：`host/data/content-index.json` 集中维护
- 已完成验证：
  - 本地可访问：`/host/index.html`、`/host/post.html` 返回 200
  - 首页数据联动可用：内容卡片渲染与筛选条件响应正常
  - 详情页渲染可用：抽检多篇文档，Markdown/图片/目录正常
  - 移动端（375px）无横向滚动：首页与详情页均通过

### M3（1 天）
- 状态：已完成（2026-02-18）
- 输入：
  - M2 完整功能站点
  - GitHub 仓库与 Pages 配置权限
- 工作：
  - 响应式与细节动效打磨
  - 完成 SEO/A11y/性能优化
  - 配置 GitHub Actions 并发布至 GitHub Pages
- 输出：
  - 线上可访问站点 URL（Pages）
  - 自动化发布流程（推送后自动部署）
  - 最终验收报告（可用性 + 性能分数）
- 验证（阶段验收）：
  - 站点可在 GitHub Pages 正常访问，移动端可用
  - Lighthouse（移动端）建议目标：
    - Performance ≥ 90
    - Accessibility ≥ 95
    - Best Practices ≥ 95
    - SEO ≥ 95
  - 首页/详情全链路可用（浏览、搜索、打开正文）
- 补充要求（来自当前实现）：
  - 已实现“内容同步”方案：构建时将引用内容同步到 `_site/content/`
  - 部署工作流使用 `_site/` 作为唯一发布目录，避免 `host/` 外部依赖
- 实施状态补充：
  - 已新增部署工作流：`.github/workflows/pages.yml`
  - 已新增打包脚本：`scripts/prepare_pages_bundle.py`
  - 已完成 SEO/A11y 基础增强：OG/Twitter meta、skip link、focus-visible、robots/sitemap 生成
- 已完成验证：
  - 本地页面验证通过：首页/详情页 200、移动端无横向滚动
  - 功能验证通过：首页筛选与详情页 Markdown/TOC/上一篇下一篇可用
  - 构建验证通过：`prepare_pages_bundle.py` 可产出可部署 `_site/`，含 `content/` 与重写后的索引
  - Lighthouse（本地）：
    - 首页：Performance 93 / Accessibility 100 / Best Practices 96 / SEO 100
    - 详情页：Performance 78 / Accessibility 100 / Best Practices 96 / SEO 100（性能受客户端动态渲染导致的 CLS 影响）
