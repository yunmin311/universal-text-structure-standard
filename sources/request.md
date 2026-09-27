你现在负责初始化并建立一个小型规范工程：

`universal-text-structure-standard`

它用于长期维护我的「通用文本结构与排版规范」。它不是课程笔记模板、README 模板、Project Inbox 模板或某一种写作风格，而是定义 AI 在 Markdown、知识笔记、研究材料、项目文档、技术说明、工作流和长回答中，如何根据真实语义选择正文、标题、列表、编号、表格、代码块、流程和空行。

核心原则：

紧凑，但不扁平；  
结构清楚，但不碎片化；  
prose-first，但不牺牲真实语义层级；  
高信息密度，但不形成 text wall；  
格式由语义关系决定，而不是套固定模板。

你是执行 Agent，不负责重新发明一套写作理论。当前已经有经过反复验证的规则和真实 Gold Reference。你的任务是把这些已确认行为转换成一个稳定、可维护、可验证、可版本化的小型规范项目。

### 1. 先读取现有材料

递归检查当前工作目录。优先寻找并完整读取：

- 当前 Custom Instructions / 个性化格式规则；
- `通用 B 级文本格式规范`；
- `Project Inbox.md`；
- 后续放入 `sources/`、`examples/` 或工作目录中的其他真实样本。

不要仅根据文件名判断内容，不要只读取开头。

如果同一规则在多个来源中重复表达，执行 `MERGE`，不要复制多份。

如果规则冲突：
1. 最新明确确认的规则优先；
2. 真实 Gold Reference 可用于判断规则实际效果；
3. 无法确定时标记 conflict，不自行创造折中规则。

### 2. 把 Project Inbox 当作第一批 Gold Reference

`Project Inbox.md` 不是模板，而是结构行为样本。

重点提取其中已经表现良好的模式：

- 大章节使用 `##`，稳定项目使用 `###`；
- 一个完整介绍段先建立主题认知；
- `V1 / 下一阶段 / 边界 / 限制 / 能力` 等真正并列属性使用紧凑 bullet；
- 状态总览使用表格；
- 严格有限状态使用编号；
- 短关系链横向表达；
- 长 pipeline 才纵向表达；
- 文件结构使用 tree；
- 同一主题不被大量 micro paragraphs 拆散。

不要把其中具体的 AI 项目内容写进通用规则。

同时把它当作真实 regression source。特别检查 Markdown Render Safety。当前文件中已经存在类似：

`**release-policy.yaml**`
以及粗体、inline code、冒号产生错误交叉的案例。

这类错误不要只在原文件中修掉后消失。必须提取成独立 bad fixture，确保 validator 以后能够发现同类问题。

### 3. 第一版项目结构

建立：

```text
universal-text-structure-standard/
├── README.md
├── STANDARD.md
├── FORMAT_RULES.yaml
├── CHANGELOG.md
├── schemas/
│   └── format-rules.schema.json
├── examples/
│   ├── good/
│   └── bad/
├── tests/
│   ├── fixtures/
│   └── expected/
├── scripts/
│   └── validate.py
└── sources/
```

不要主动增加 Web UI、Obsidian 插件、复杂 parser、Node 项目、数据库或其他基础设施。

如果一个额外文件没有明确长期职责，就不要创建。

### 4. 三层规则必须分开

所有规则必须归入以下三类之一：

1. `semantic`
   - paragraph vs list
   - bullet vs numbered list
   - table
   - heading hierarchy
   - true parent/child structure
   - flow / tree selection

2. `presentation`
   - information density
   - whitespace
   - horizontal vs vertical flow
   - list compactness
   - heading density
   - text-wall prevention

3. `render_safety`
   - paired `**`
   - inline code closure
   - fenced code block closure
   - `**字段：** 内容`
   - list indentation
   - valid tables
   - dangerous bold/code nesting

不要把三层重新混成一个巨大 prompt。

### 5. FORMAT_RULES.yaml

它是结构化规则 registry。

每条规则至少支持：

```yaml
rule_id:
category:
title:
severity:
condition:
preferred_action:
forbidden_pattern:
exceptions:
validation_method:
examples:
status:
```

`status` 第一版支持：

- `active`
- `experimental`
- `deprecated`

`rule_id` 必须稳定。一旦进入正式版本，修改规则内容时不能因为文案变化随意重新编号。

建议使用类似：

- `SEM-*`
- `PRE-*`
- `REN-*`

的 namespace，但先选择一个简单、稳定的编号方案，不要设计复杂 taxonomy。

为 `FORMAT_RULES.yaml` 创建 JSON Schema，至少验证 required fields、enum、基本类型和 `rule_id` 唯一格式。

### 6. STANDARD.md

这是 human-readable canonical specification。

它必须自己遵守正在定义的规范：

- 少量真实章节；
- prose-first；
- 不要每条规则都升级成标题；
- 并列规则使用紧凑列表；
- 不产生 micro paragraphs；
- 不堆粗体伪标题；
- 不制造大面积空白。

不要机械复制原始 B 级规范。

先进行：
`EXTRACT → MERGE → NORMALIZE → WRITE`

保留规则的真实含义，但删除重复表述。

### 7. Examples

`examples/good/` 保存真实优秀片段或完整文档。

第一批至少加入 `Project Inbox` 的代表性结构案例，并说明它证明哪些 `rule_id`。

不要把 Gold Reference 理解为“全文所有地方都绝对正确”。一个文档可以整体是 good example，同时其中某个局部被抽取成 bad fixture。

`examples/bad/` 第一批至少覆盖：

- micro paragraphs；
- fake bold headings；
- parallel items compressed into prose；
- unnecessary nested bullets；
- vertical whitespace abuse；
- text wall；
- meaningless headings；
- short flow incorrectly verticalized；
- broken Markdown emphasis；
- bold / inline-code crossing。

bad example 必须标明对应违反的 `rule_id`。

### 8. Formatting Gate 与 Render Gate

第一阶段实现轻量 validator，不追求完整 Markdown AST。

至少检查能够可靠静态检测的项目：

- unmatched `**`；
- unmatched inline backticks；
- unclosed fenced code blocks；
- 常见错误字段格式；
- 可疑的 bold + inline-code crossing；
- 过深 list indentation；
- heading level jump；
- 表格 separator / column 明显不匹配。

对于无法可靠静态判断的语义规则，例如：

- micro paragraphs；
- text wall；
- 3+ parallel items compressed into prose；
- heading 是否真正有语义价值；
- 横向还是纵向流程；

先使用 fixture + expected result 或 heuristic warning，不要假装 parser 能 100% 判断。

validator 必须区分：

`ERROR / WARNING / INFO`

Render Safety 中明确破坏 Markdown 的问题优先作为 `ERROR`。

### 9. Tests

不要一开始做复杂测试框架。

第一阶段使用 fixture-driven tests 即可：

```text
tests/
├── fixtures/
│   ├── valid/
│   └── invalid/
└── expected/
```

每个 invalid fixture 应能对应至少一个稳定 `rule_id`。

特别创建一个来自真实 `Project Inbox` 问题的 regression fixture，验证文件名 / inline code / bold / colon 的组合不会再次出现同类错误。

### 10. CHANGELOG

只记录规则系统真正变化：

- 新增规则；
- 修改规则语义；
- MERGE；
- DEPRECATE；
- schema change；
- validator behavior change。

不要记录 typo、格式整理、普通重排。

第一版版本号从 `0.1.0` 开始，不要直接宣称 `1.0.0`。

### 11. 当前边界

第一版明确禁止：

- 把规范变成某一种笔记模板；
- 为课程笔记添加专用规则；
- 为 Project Inbox 添加专用规则；
- 根据某个 Gold Reference 复制固定章节结构；
- 创建复杂 AI writing framework；
- 创建 UI；
- 创建数据库；
- 创建完整 Markdown parser；
- 为了“工程化”增加没有明确用途的文件；
- 把所有自然语言规则机械转换成无法验证的 YAML。

核心目标仍然只是：

`stable rule registry + human-readable specification + real examples + lightweight validation`

### 12. 工作方式

把规范本身当作一个长期维护的 state，而不是累积式聊天摘要。

处理新反馈时使用：

`ADD / UPDATE / MERGE / DELETE / DEPRECATE`

同一个概念只有一个当前 canonical definition。

Exploration、Proposal 和 confirmed rule 必须区分。未经明确确认的新想法不能直接进入 `active` canonical rules。

### 13. 本轮完成标准

完成第一轮后应至少能够证明：

1. 当前已确认规则已经从原始文本中提取和去重；
2. Semantic / Presentation / Render Safety 已明确分层；
3. `FORMAT_RULES.yaml` 能通过 schema validation；
4. `STANDARD.md` 与规则 registry 没有明显语义冲突；
5. Gold Reference 已进入 examples；
6. 已从真实材料提取至少一个 Markdown regression fixture；
7. validator 能发现第一批确定性的 Markdown 错误；
8. tests 可以一次执行并明确 PASS / FAIL；
9. `CHANGELOG.md` 记录 `0.1.0` 的真实建立内容；
10. 没有创建超出当前需求的大型框架。

完成后不要只回复“done”。

最终报告保持紧凑，只输出：

- `RESULT`
- `FILES CREATED / MODIFIED`
- `RULE COUNT`（按三层分类）
- `VALIDATION`
- `TESTS`
- `KNOWN LIMITATIONS`
- `OPEN DECISIONS`
- `NEXT RECOMMENDED STEP`

如果发现现有规则之间存在真正冲突，不要自行融合。在 `OPEN DECISIONS` 中精确列出冲突双方及建议，不修改 canonical rule。