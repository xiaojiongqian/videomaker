# 学习 Claude Code 开发经验：构建优秀 Agent 的实战借鉴

如果你正在做 Agent 产品，这篇来自 Claude Code 团队的一线复盘很值得看。

它最有价值的观点不是“要不要多加工具”，而是：**工具设计必须<strong style="color:#C2410C;">跟着模型能力变化一起迭代</strong>**。同一个设计，在模型能力升级后，可能从“<strong style="color:#C2410C;">必要</strong>”变成“<strong style="color:#C2410C;">束缚</strong>”。

![Claude Code 经验图 1](https://img.learnblockchain.cn/2026/02/28/10744939_image.jpg)

## 这篇文章最值得拿走的 6 个结论

1. **Agent 的核心不是工具数量，而是 <strong style="color:#C2410C;">action space 的质量</strong>。**
工具越多不一定越好，每多一个选择都会增加模型决策负担。

2. **工具要“<strong style="color:#C2410C;">贴合模型能力</strong>”，不是贴合工程师想象。**
判断标准很简单：看模型真实输出，持续实验，而不是靠先验假设。

3. **<strong style="color:#C2410C;">结构化交互</strong>比“格式约定”更稳定。**
让模型按 Markdown 模板输出问题，常常会跑偏；把提问能力做成独立工具（如 AskUserQuestion）更可靠。

4. **模型能力升级后，要<strong style="color:#C2410C;">主动淘汰旧约束</strong>。**
早期用 TodoWrite 保持任务轨道；后期改成 Task Tool，重点转向多 Agent 协同与依赖管理。

5. **让模型<strong style="color:#C2410C;">自己构建上下文</strong>，通常比“喂上下文”更可扩展。**
从 RAG 预置上下文，走向 Grep 搜索代码、递归读取 Skills，体现的是“探索式上下文构建”。

6. **<strong style="color:#C2410C;">Progressive Disclosure（渐进式披露）</strong>是高性价比扩展手段。**
不增加新工具，也能通过分层文档/子 Agent 扩展能力，避免上下文膨胀和工具膨胀。

## 三个关键演进案例

### 1) AskUserQuestion：从“输出格式约束”到“工具化提问”

团队做了三次尝试：

- 在 ExitPlanTool 里附带问题数组：实现简单，但计划和提问耦合后容易冲突。
- 约束模型输出固定 Markdown：通用但不稳定，容易漏项或变形。
- <strong style="color:#C2410C;">独立 AskUserQuestion 工具</strong>：可随时调用，计划模式下重点触发，用户通过弹窗回答，<strong style="color:#C2410C;">链路更稳定</strong>。

这背后的方法论是：不要只要求模型“说对”，要为模型提供“<strong style="color:#C2410C;">稳定做对</strong>”的交互结构。

![Claude Code 经验图 2](https://img.learnblockchain.cn/2026/02/28/29607404_image.jpg)

### 2) TodoWrite → Task Tool：从“单体执行”到“协同执行”

早期 TodoWrite 的目标是防止模型跑偏，甚至每 5 轮插提醒。

但<strong style="color:#C2410C;">模型能力增强后</strong>，这些提醒反而<strong style="color:#C2410C;">限制了模型动态调整任务</strong>。尤其引入 subagents 后，单一 Todo List <strong style="color:#C2410C;">难以协同</strong>。

于是演进到 Task Tool：

- 支持<strong style="color:#C2410C;">任务依赖</strong>
- 支持<strong style="color:#C2410C;">跨子 Agent 同步进度</strong>
- 支持<strong style="color:#C2410C;">任务修改与删除</strong>

启发是：你为旧模型设计的“<strong style="color:#C2410C;">护栏</strong>”，可能会成为新模型的“<strong style="color:#C2410C;">天花板</strong>”。

![Claude Code 经验图 3](https://img.learnblockchain.cn/2026/02/28/34593394_image.jpg)

### 3) 从 RAG 到搜索 + Skills：让 Agent 学会“自己找答案”

文章里一个非常实用的变化是：从“系统预先给上下文”，逐步转向“<strong style="color:#C2410C;">模型主动构建上下文</strong>”。

路径大致是：

- <strong style="color:#C2410C;">RAG</strong>：快，但依赖索引与环境，且上下文是被动注入。
- <strong style="color:#C2410C;">Grep 搜索代码库</strong>：让模型自己定位相关文件。
- <strong style="color:#C2410C;">Skills 递归读取</strong>：形成分层探索，逐步收敛到最相关信息。

这其实是把“<strong style="color:#C2410C;">检索能力</strong>”从系统能力，逐步迁移成<strong style="color:#C2410C;">模型可操作能力</strong>。

![Claude Code 经验图 4](https://img.learnblockchain.cn/2026/02/28/42710217_image.jpg)

## 对 Agent 产品的直接借鉴（可落地）

可以把下面这份清单当作评审模板：

- 新增一个工具前，先问：能否用 <strong style="color:#C2410C;">progressive disclosure</strong> 解决？
- 每个工具都要验证：模型是否“<strong style="color:#C2410C;">愿意且会正确调用</strong>”？
- 每个季度复盘一次：哪些工具已从“<strong style="color:#C2410C;">增益</strong>”变成“<strong style="color:#C2410C;">约束</strong>”？
- 对复杂任务优先设计“<strong style="color:#C2410C;">协同结构</strong>”（任务依赖、状态共享），而不是只加提醒。
- 上下文策略优先级：让模型先“<strong style="color:#C2410C;">找</strong>”，系统再“<strong style="color:#C2410C;">补</strong>”。

## 一句话总结

优秀 Agent 不是“工具堆出来”的，而是通过<strong style="color:#C2410C;">持续观察模型行为</strong>、不断<strong style="color:#C2410C;">重构 action space</strong>迭代出来的。

---

参考链接：

- 原帖（X）：https://x.com/trq212/status/2027463795355095314
- Prompt Caching（文中提及）：https://x.com/trq212/status/2024574133011673516
- Task Tool（文中提及）：https://x.com/trq212/status/2014480496013803643
