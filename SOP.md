# 网站内容管理 SOP（GitHub Pages）

用于管理站点文章上/下架，保持「集中管理 + 简单可维护」。

## 1) 入口文件

- 内容总索引：`host/data/content-index.json`
- 站点仅展示：`status = "published"` 的条目

## 2) 5 分钟流程

1. 准备内容：新增/更新 Markdown 与配图文件（路径可在仓库任意位置）。
2. 登记索引：在 `host/data/content-index.json` 新增或编辑条目。
3. 控制状态：
   - 草稿：`draft`（不展示）
   - 上架：`published`（前台可见）
   - 下架：`hidden`（不展示，但保留可恢复）
4. 提交发布：`git add` + `git commit` + `git push origin main`。
5. 验证上线：查看 GitHub Actions 的 `Deploy GitHub Pages` 是否成功，并访问线上页面。

## 3) 最小条目模板

```json
{
  "id": "your-unique-id",
  "title": "文章标题",
  "source": "../path/to/article.md",
  "status": "draft",
  "updatedAt": "2026-02-18"
}
```

## 4) 发布前检查清单

- `id` 唯一且稳定（已发布内容尽量不改）
- `source` 路径可访问，文内图片/相对链接可打开
- 标题、摘要、日期、封面字段已补齐（如有）
- 状态设置正确：要上线用 `published`，要下线用 `hidden`
- 推送后确认 Actions 成功，再抽检首页与详情页
