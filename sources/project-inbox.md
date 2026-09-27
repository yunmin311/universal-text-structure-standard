
| #   | 方向                                   | 状态                           | 当前判断                                            |
| --- | ------------------------------------ | ---------------------------- | ----------------------------------------------- |
| 01  | AI Usage / Quota Hub                 | **Develop**                  | 高价值开发候选；解决多模型额度、可用性与任务调度                        |
| 02  | Project Context Bridge               | **Develop**                  | 高价值基础设施；统一项目当前状态                                |
| 03  | Huawei Health → AI Bridge            | **Develop**                  | 明确生态缺口；解决 Huawei Health → AI 数据连接               |
| 04  | Photographer Preference Memory       | **Develop**                  | 保留；学习个人摄影审美，不重复开发技术选片                           |
| 05  | Evidence-first Portfolio Compiler    | **Develop**                  | 高优先级；建立 Evidence → Claim → Narrative            |
| 06  | Graduate Application Evidence Matrix | **Develop**                  | 保留；建立在 Personal Evidence Graph 之上               |
| 07  | Obsidian Course Copilot              | **Develop / Lower Priority** | 已有成熟 workflow，未来重点是标准执行与验证                      |
| 08  | Personal GitHub Radar                | **Develop / Lower Priority** | 需求成立，但 discovery 已被每日简报部分覆盖                     |
| 09  | Cross-Agent Memory                   | **Adopted**                  | 使用成熟 MCP / memory 方案，不重复开发                      |
| 10  | Research Evidence Stack              | **Adopted**                  | Elicit / Scite → Zotero → Obsidian              |
| 11  | Conversation Capsule / Handoff       | **Adopted**                  | 使用现成跨 Agent handoff 工具                          |
| 12  | Agent Environment Manager            | **Adopted**                  | 使用现成配置治理和 doctor 工具                             |
| 13  | Bug Capture → AI                     | **Adopted**                  | 使用 Jam 等成熟产品                                    |
| 14  | AI Stack Change Impact               | **Skill & Standard**         | 做 Skill，不做独立 App                                |
| 15  | Release / Publishing Steward         | **Skill & Standard**         | 做 Workspace Standard + Skill，不重做 release engine |
| 16  | Personal CRM                         | **Deprecated**               | 当前复杂度和收益不匹配                                     |
| 17  | Visual Reference Library             | **Deprecated**               | 当前需求不足，不增加新的视觉资产系统                              |

## Develop

### 01. AI Usage / Quota Hub

AI Usage / Quota Hub 不是另一个 token 或余额 Dashboard，而是为多 AI 平台并存后的**任务调度问题**提供决策层。Codex、OpenCode、OpenRouter、DeepSeek、Muse 等同时存在时，真正困难的并不是知道每个平台用了多少，而是判断当前哪个模型有足够额度、何时 reset、成本和能力是否匹配，以及一个具体任务是否值得交给它。产品因此更接近 **AI Compute Router for Humans**：综合额度、模型状态、价格、上下文长度、近期失败率和任务类型，最终回答“这个任务现在应该交给谁，以及为什么”。

- **V1：** 只做观察与推荐，不自动替用户调用模型。数据模型覆盖 `Provider / Model / RemainingQuota / ResetAt / Cost / Context / Availability / RecentFailure / CapabilityTag`，再使用 Task Profiler 区分 coding、debugging、repo-wide、research、vision、long-context 等任务。
    
- **下一阶段：** 发展 `Task-to-Model Policy Engine`。例如 small edit 优先 cheap/fast，repo-wide refactor 优先 long-context + stable quota，final review 使用 strongest model；之后再接 Codex / OpenCode，让 Agent 在任务开始前调用 `/route-task` 获取模型与预算建议。
    
- **关键限制：** 各个平台并不都会正式暴露 quota，因此所有数据必须区分 `official / inferred / scraped / manually configured`。产品不能把推算值包装成精确额度，也不能假设所有 provider 都能统一读取。
    

---

### 02. Project Context Bridge

Project Context Bridge 是一个比 Workbench 更底层、更窄的能力：**让任何 Agent 进入一个项目后，都能立即知道项目现在到底处于什么状态。** 当前信息通常散落在 Git、README、docs、issues、本地未提交文件、Agent 对话和 handoff 中，因此新的 Agent 很容易重新询问 active branch、当前目标、哪些设计已经废弃、正在做什么以及下一步是什么。Bridge 不试图保存完整历史，而是生成一个最小充分的 `Project Context Snapshot`，让 ChatGPT、Codex、Claude Code、OpenCode 等不同 Agent 读取同一份当前状态。

- **V1：** 本地 daemon 扫描 Git repository，并结合标准化 `project-state.yaml`，输出 project identity、repo、active branch、HEAD、dirty state、current goal、confirmed decisions、active work、blocked items、deprecated decisions、important artifacts 和 recent commits。
    
- **MCP：** 第一阶段只暴露 `get_project_state`、`get_recent_changes`、`get_current_decisions`、`get_open_work` 四个读取接口。
    
- **下一阶段：** 再接 GitHub Issues / PR、Obsidian、Google Drive、设计稿等来源，并加入 conflict detection。当 README、state 和实际 commit 互相冲突时返回 `STATE CONFLICT`，而不是让 Agent 自行猜测并融合；进一步可生成 handoff capsule，只携带下一个 Agent 继续执行真正需要的信息。
    
- **边界：** Cross-Agent Memory 保存长期稳定事实，Project Context Bridge 保存项目此刻的动态状态。`项目使用 pnpm` 属于 memory，`当前 branch / goal / blocked / dirty state` 属于 Context Bridge，两者不能合并成一个无限增长的状态仓库。
    

---

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
    

---

### 05. Evidence-first Portfolio Compiler

Evidence-first Portfolio Compiler 是当前开发池里最重要的方向之一。它不从 GitHub repository 直接生成一篇看起来很专业的 Portfolio，而是先建立可靠的个人工程证据层，把真实 Evidence 转成经过支持的 Claim，再由 Claim 生成不同用途的 Narrative。这样 Portfolio、CV、README、申请材料和面试表达都来自同一套 canonical evidence，而不是每次重新让 AI 根据 README 自由发挥。

核心结构本身很短，直接横向表达：

```
Evidence → Claim → Narrative
```

- **Evidence Layer：** 读取 Release、tests、commit SHA、PR、issues、GitHub assets、README、docs、screenshots、architecture decisions 等真实材料，并生成本地 `evidence.json` 或 `project-evidence.yaml`。每条 evidence 至少记录 `source / timestamp / confidence / artifact / supported_claims`。
    
- **Claim Layer：** 只有被 evidence 支持的事实才能形成 Claim。核心规则保持：**No evidence → no factual claim. No source → no metric.**
    
- **Narrative Layer：** 同一个 Claim 可以转换为 Portfolio Case Study、Resume Bullet、README Project Summary、申请项目描述或 Interview Story，同一事实只维护一次，不在多个文档里分别重写。
    
- **关键能力：** Evidence Gap Detection 负责限制 AI 过度表述。例如 bug-fix commits 可以支持“improved stability”，但如果没有 crash telemetry，就不能生成“reduced crashes by 40%”。真正的差异化因此不是页面生成，而是 provenance、anti-hallucination 和 evidence coverage。
    
- **后续：** V1 只接 GitHub；之后再扩展 Figma、摄影作品、实习资料、课程项目和 Google Drive，最终形成可以被 Portfolio、申请、面试等不同场景重复使用的 Personal Evidence Graph。
    

---

### 06. Graduate Application Evidence Matrix

Graduate Application Evidence Matrix 不应该重新成为一套申请管理系统，而是建立在 Evidence-first Portfolio Compiler 的 Personal Evidence Graph 之上。现有产品已经能够很好地管理学校列表、deadline、推荐人和文档状态，因此这里真正需要解决的是“学校要求什么”与“我有什么真实材料能够证明”之间的映射。这样查看某个项目时，重点不再是还有多少天截止，而是每一个 selection dimension 是否已经有可靠 evidence 支撑。

核心判断链可以直接压缩为：

```
School Requirement ↔ Personal Evidence → Evidence Strength → Missing Evidence → Application Artifact
```

- **核心映射：** strong programming background 对应经过验证的工程项目，research experience 对应科研、SURF 或论文，creative work 对应摄影和视觉作品。
    
- **输出：** 每所学校统一形成 `Requirement → Supporting Evidence → Strength of Evidence → Missing Evidence → Application Artifact`，从而明确哪些要求已有直接证据、哪些只有间接证据、哪些仍然存在 material gap。
    
- **V1：** 不需要复杂 UI。读取 5–10 个真实项目页面，提取官方 requirement，再和 Evidence Ledger 建立 Markdown / JSON matrix 即可。
    
- **边界：** Portfolio Compiler 和 Application Matrix 共用数据模型，但第一阶段保持两个清楚的工作层。前者负责建立“我真正做过什么”，后者负责判断“这些证据如何匹配某个项目的要求”。
    

两个项目之间的完整关系较长，因此继续使用纵向链路：

```
GitHub / 实习 / 课程 / 摄影
            ↓
      Evidence Compiler
            ↓
 Canonical Evidence Graph
            ↓
Application Evidence Matrix
            ↓
CV / Portfolio / Interview / Application
```

---

### 07. Obsidian Course Copilot

Obsidian Course Copilot 已经有明确需求、稳定标准和大量真实使用样本，因此目前保留开发方向，但不再进行大规模产品探索。它的价值不是普通的“PDF → Markdown”，而是把已经形成的 Course Notes Standard 变成真正可执行、可验证、可增量运行的课程知识 pipeline。输入是 lecture PDF / PPT、已有课程笔记和 Standard，输出则是完整、符合规则并且不会破坏已有内容的 Obsidian course package。

这里属于真正的长流程，保留纵向：

```
PDF / PPT + Existing Notes + Standard
                  ↓
                Parse
                  ↓
         Chapter Detection
                  ↓
          Note Generation
                  ↓
          Visual Decision
                  ↓
        Source Packaging
                  ↓
             Validation
                  ↓
          Write to Vault
```

- **核心能力：** Standard Enforcement Engine 把 frontmatter、目录结构、公式规则、图片来源、sources hard rule、增量更新规则等转成 machine-readable constraints，再由 validator 判断结果是否允许进入正式笔记。
    
- **后续：** 加入 course state，记录哪些 lecture 已覆盖、哪些公式仍未理解、哪些讲解还没有进入正式笔记，以及哪些知识点存在 prerequisite gap，逐渐从笔记生成器发展成课程学习状态系统。
    
- **当前优先级：** 较低。现有人工 workflow 已经成熟，因此下一步重点是产品化和自动验证，而不是继续重新设计笔记方法本身。
    

---

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

### 09. Cross-Agent Memory

Cross-Agent Memory 只承担**长期稳定事实的共享**，例如项目使用 pnpm、某 API 已废弃、某项视觉规则已经确认等。它不负责 active branch、current goal、blocking、working tree 等动态状态，否则 memory 很快会变成第二个失控 README。实际使用时优先选择 project-local memory，并让 Codex、OpenCode 等 Agent 读取同一个 MCP source；如果未来检索质量确实成为问题，再评估更重的 memory 系统，而不是一开始就建设复杂基础设施。

---

### 10. Research Evidence Stack

研究工作流保持最小化：Elicit 用于系统搜索、screening 和综合，Scite 用于检查 supporting / contrasting citation context，Zotero 作为 canonical bibliography 和文献资产库，最终自己的框架、理解和长期知识仍然进入 Obsidian。Readwise 等额外工具只有在未来确实出现大量网页、newsletter、书籍和长文需要统一阅读 inbox 时再加入，不为了单一功能继续堆应用。

标准路径适合直接横向表达：

```
Research Question → Elicit 搜索 / 综合 + Scite 证据验证 → Zotero 收录与管理 → 阅读 / 批注 → Obsidian
```

---

### 11. Conversation Capsule / Handoff

跨 Agent 对话封装优先使用现成 Agent Capsule、Handoff 等工具，不再重新开发通用 conversation exporter。它们负责把一次编码或 Agent 会话转换成可以继续工作的 handoff context，解决 Claude Code、Codex、OpenCode 等工具之间的会话迁移问题。只有未来确认 ChatGPT 网页等**非代码长对话**仍然无法稳定沉淀成 durable artifact，才重新考虑是否补一个面向知识型对话的封装层。

---

### 12. Agent Environment Manager

MCP、rules、skills、commands、hooks、配置 drift、环境错误和多 Agent 配置同步已经有专门工具处理，因此这个方向直接 Adopt，而不进入产品开发。Workspace 中应该选择一套主配置治理工具，再配合 doctor / validate / drift / reconcile 类检查，避免为了每一个 Agent 单独维护一套越来越不一致的环境。它解决的是“AI 开发环境是否健康”，不是 Project Context，也不是 Workspace Policy。

---

### 13. Bug Capture → AI

界面 Bug、浏览器问题和 Electron / Web 产品问题优先使用 Jam 等成熟工具，把 screenshot / video、browser information、console、network request 和 user actions 一次性交给 Agent。这样可以替代“截图 + 人工口述发生了什么”的低质量 bug handoff，也没有必要重新开发自己的 capture system。它作为开发工作流工具存在即可，不进入 Project Inbox 的产品开发池。

## Skill & Workspace Standard

这一类能力确实长期有价值，但不需要独立做成 App。它们应该沉淀为可被不同 Agent 复用的 Skill 和稳定 Workspace Asset：前者负责执行与判断，后者保存长期规则和已经确认的事实，从而避免同一套工作方法依赖某一段聊天历史。

### 14. AI Stack Change Impact

AI Stack Change Impact 不负责“发现 AI 新闻”，因为每日兴趣简报已经承担 discovery。它只回答一个更窄也更有价值的问题：**某个 release、model change、pricing change、authentication change、MCP schema change 或 provider policy change，会不会影响当前 workspace，如果会，需要做什么。**

统一判断链较短，直接横向表达：

```
External Change → Affected Surface → Why It Matters → Required Action → Verification
```

- **状态：** 只使用 `NO_IMPACT / WATCH / ACTION_REQUIRED / BLOCKED`，避免重新生成一篇 changelog 摘要。
    
- **Response Mode：** 普通任务中，如果发现真正影响 workspace 的变化，在最终回复里增加紧凑的 `Workspace Impact`；没有影响时完全不显示。
    
- **Persist Mode：** 只有后续 Agent 也必须长期知道的变化，才写入 `.workspace/impact/`。这里保存的是当前仍然有效的影响、处理方式和验证结果，而不是新闻历史。
    
- **规则：** 不能因为存在新版本就自动建议升级；推测不能写成确认事实；默认不自动修改配置；旧影响失效后应该 UPDATE / DELETE，而不是持续追加记录。
    

核心价值也可以压缩为一行：

```
News / Release Note → Your Workspace Consequence
```

---

### 15. Workspace Release & Publishing Steward

发布本身继续交给 GitHub Release、release-please、Changesets 等成熟工具，Workspace 层只负责维护**这个项目应该怎样发布、哪些资产必须存在、怎样验证发布是否真的完成**。因此这里不是新的 release engine，而是一套稳定的 Workspace Standard，再配合 `release-steward` Skill 执行。

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

各资产职责固定：

1. `**release-policy.yaml**`**：** 维护 SemVer、版本来源、tag 命名、默认 branch、prerelease、CHANGELOG、GitHub Release title 和发布目标等规则。
    
2. `**artifact-manifest.yaml**`**：** 定义每次发布必须包含哪些 artifact、source path、build command、release filename、required 状态和 checksum 要求。
    
3. `**verification.yaml**`**：** 维护 tests、lint、build、package integrity、version consistency、tag target SHA、Release existence、asset 数量和 checksum 等 gate。
    
4. `**impact/**`**：** 保存 AI Stack Change Impact 中仍然有效、会影响 Workspace 的外部变化。
    
5. `**reports/releases/**`**：** 每次发布完成后记录真实的 `version / tag / target SHA / release URL / assets / checksums / verification / exceptions`，以后不再依赖聊天历史重新确认。
    

`release-steward` Skill 的执行顺序固定为：

1. 读取 `.workspace/` 中的 canonical policy 和 manifest。
    
2. 检查 repository 当前状态，并运行发布前 verification gates。
    
3. 调用项目已经选择的 release automation，而不是自行重新实现发布逻辑。
    
4. 发布后重新读取真实远端状态，核对 tag、SHA、Release、assets 和 checksum。
    
5. 将最终事实写入 `reports/releases/`，最终回复只报告发布结果、验证状态和异常。
    

Project Context Bridge 与 `.workspace/` 的边界继续保持：

```
.workspace/ → “这个 workspace 应该怎样运行”
Project Context Bridge → “这个项目现在在哪里”
```

前者保存长期 policy、toolchain、artifact rule、verification 和 impact；后者保存 current goal、branch、active work、blocked 和当前 decisions。两者可以互相读取，但不能混成一份无限膨胀的状态文件。

## Deprecated

当前已经明确退出工作池的方向只保留最小记录，用于说明为什么不再继续，而不保存旧 proposal 的完整历史。

### 16. Personal CRM

当前联系人规模和维护需求不足以支撑另一套长期应用。为了偶尔维护老师、导师或职业联系人，再增加一个独立 CRM 会提高系统复杂度；只有未来联系人数量和关系维护成本明显增长时才重新评估。

---

### 17. Visual Reference Library

当前需求还不足以支撑新的视觉资产系统，也没有必要为了图片搜索和 reference management 再增加一个长期应用。摄影方向只保留 Photographer Preference Memory，用于学习个人审美，不扩展成通用图片收藏或素材管理平台。