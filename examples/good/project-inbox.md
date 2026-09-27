<!-- 原文摘录；仅收紧简单列表空行。来源 sources/project-inbox.md。证明 SEM-001 至 SEM-007、PRE-003、PRE-005；并非全文完美认证。片段之间省略项目。 -->

## Develop

### 01. AI Usage / Quota Hub

AI Usage / Quota Hub 不是另一个 token 或余额 Dashboard，而是为多 AI 平台并存后的**任务调度问题**提供决策层。Codex、OpenCode、OpenRouter、DeepSeek、Muse 等同时存在时，真正困难的并不是知道每个平台用了多少，而是判断当前哪个模型有足够额度、何时 reset、成本和能力是否匹配，以及一个具体任务是否值得交给它。产品因此更接近 **AI Compute Router for Humans**：综合额度、模型状态、价格、上下文长度、近期失败率和任务类型，最终回答“这个任务现在应该交给谁，以及为什么”。

- **V1：** 只做观察与推荐，不自动替用户调用模型。数据模型覆盖 `Provider / Model / RemainingQuota / ResetAt / Cost / Context / Availability / RecentFailure / CapabilityTag`，再使用 Task Profiler 区分 coding、debugging、repo-wide、research、vision、long-context 等任务。
- **下一阶段：** 发展 `Task-to-Model Policy Engine`。例如 small edit 优先 cheap/fast，repo-wide refactor 优先 long-context + stable quota，final review 使用 strongest model；之后再接 Codex / OpenCode，让 Agent 在任务开始前调用 `/route-task` 获取模型与预算建议。
- **关键限制：** 各个平台并不都会正式暴露 quota，因此所有数据必须区分 `official / inferred / scraped / manually configured`。产品不能把推算值包装成精确额度，也不能假设所有 provider 都能统一读取。

### 03. Huawei Health → AI Bridge

Huawei Health → AI Bridge 的定位不是“再做一个健康 AI”，而是建立 **Personal Health Data Gateway**。Huawei Watch / Huawei Health 中已经积累了大量真实数据，但这些数据目前很难直接进入 ChatGPT、Claude、Codex、OpenCode 或 MCP，因此用户仍然需要截图、导 CSV 或人工转述。这个项目首先解决的是连接、标准化和 provenance，让健康数据成为任何上层 AI 都可以安全读取的个人数据层，而不是一开始就做健康判断或医疗功能。

核心数据链较长，保留纵向表示：

```
Huawei Health / Health Connect / TCX / GPX / FIT
                     ↓
                 Connector
                     ↓
                 Normalizer
                     ↓
           Personal Health Store
                     ↓
                 Query API
                     ↓
             MCP / ChatGPT App
```

- **V1：** 优先支持 Huawei Health export、Health Connect、TCX / GPX / FIT，并统一为 `sleep / heart_rate / resting_hr / steps / calories / workout / distance / pace / SpO₂ / weight` 等 schema；同时记录每条数据究竟来自 Huawei、Health Connect 还是手工输入。
- **关键难点：** 真正困难的是 Huawei 数据获取、Android 权限、地区差异、重复数据去重和不同平台之间的睡眠 / 运动 schema 映射，而不是 LLM 本身。
- **后续：** 在基础数据层稳定后再接 Intervals.icu、Strava、Garmin、Apple Health，并逐步发展成 Universal Personal Health Context Layer。Huawei 应该是第一个 connector，而不是第一版就同时支持所有设备生态。
    

---

### 04. Photographer Preference Memory

现有 Lightroom、Aftershoot 等产品已经能够完成失焦、闭眼、重复帧等技术选片，因此这里没有必要重新开发“AI Culling”。真正值得保留的问题是：**为什么同一组照片里，你最终会选择 A 而不是 B。** Photographer Preference Memory 应学习个人长期审美，而不是判断一张照片是否符合通用摄影标准；人物角度、视线、姿态、构图、空间关系、背景、光线方向、色彩和技术质量都可以参与判断，但技术质量只是其中一个维度。

核心数据关系较短，直接横向表达：

```
Photo + Selection Event + Context → Personal Preference Signal
```

- **数据：** 五星 / 四星 / 淘汰、同一连拍中的最终选择、最终发布、是否进入作品集、是否二次精修都可以成为偏好信号，其中最重要的监督形式优先使用 `A vs B → chose A`，而不是要求用户给大量照片填写绝对评分。
- **V1：** 不训练自己的视觉大模型，先用现成 multimodal embedding 加轻量 personalized ranking layer。输出使用 `Strong Match / Maybe / Technical Reject` 等可解释分类，并说明影响选择的主要因素，避免制造 `87/100` 一类没有真实意义的精确分数。
- **长期方向：** 逐渐形成 `Personal Aesthetic Profile`，再从选片扩展到人物最佳角度、光线、妆容和拍摄前判断，并最终和人脸、神态、服装、光线等审美研究体系产生联系。任何版本都不自动删除 RAW。

### 08. Personal GitHub Radar

Personal GitHub Radar 解决的是“热门项目很多，但真正和当前工作相关的很少”。它不应该复制 GitHub Trending，而是根据个人 Stars、已有 repositories、最近 commits、长期兴趣和手工规则建立动态兴趣模型，判断一个新项目到底值不值得花时间，以及它和现有项目是否存在实际结合关系。输出的重点不是 summary，而是行动判断。

行动状态固定为四级，而不是继续嵌套 bullet：

1. `WATCH` — 值得持续关注。
2. `TRY` — 现在值得安装测试。
3. `INTEGRATE` — 与现有项目存在直接结合价值。
4. `IGNORE` — 热门，但和当前工作无关。
    

- **V1：** 只接 GitHub API，使用 Stars、Following、repo metadata、release / commit activity 等信息，每天筛选 Top 10，周末进一步留下真正值得继续看的 3 个。
- **评分逻辑：** 不能主要依赖 Star，而应综合 `relevance × maintenance × maturity × novelty × integration potential`；后续再加入 semantic graph，解释一个 repository 与现有项目之间具体存在什么关系。
- **当前优先级：** 较低。每日兴趣简报已经承担部分 discovery，而 AI Stack Change Impact 又会负责判断某个变化是否真正影响现有工作流；只有 GitHub discovery 后续仍明显过载时，才值得把 Radar 独立开发。

## Adopted

这一组方向已经有成熟工具覆盖主要需求，因此不再进入开发池。采用原则不是寻找功能最多的平台，而是在不增加大量长期维护系统的前提下，用最少的新工具补齐真实缺口；如果未来现成方案确实无法覆盖关键需求，再重新评估是否开发。

|#|能力|当前采用方式|使用边界|
|---|---|---|---|
|09|Cross-Agent Memory|使用 `shared-agent-memory` 等现成 MCP / memory 方案|保存稳定事实，不保存实时项目状态|
|10|Research Evidence Stack|`Elicit / Scite → Zotero → Obsidian`|Zotero 是 canonical bibliography，最终知识回到 Obsidian|
|11|Conversation Capsule / Handoff|使用现成 Agent handoff / capsule 工具|负责跨 Agent 会话交接，不重做通用 exporter|
|12|Agent Environment Manager|使用 `agentctl`、doctor 等现成工具|管 MCP、skills、rules、配置 drift 和环境检查|
|13|Bug Capture → AI|使用 Jam 等成熟产品|一次性交付 screen、console、network 和 user actions|

推荐的长期结构保持为：

```
.workspace/
├── README.md
├── release-policy.yaml
├── artifact-manifest.yaml
├── verification.yaml
├── impact/
└── reports/
    └── releases/
```
