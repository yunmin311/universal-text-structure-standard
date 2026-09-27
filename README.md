# universal-text-structure-standard

维护通用文本结构与排版规范的小型工程，当前版本为 0.1.0。规范覆盖语义结构、呈现密度和 Markdown 渲染安全，适用于笔记、研究材料、项目文档与长回答。它不规定固定章节，不复制课程或 Project Inbox 的内容模板。

## 阅读与使用

先读 [STANDARD.md](STANDARD.md)，按内容关系选择结构，再用检测器检查可静态识别的问题。[FORMAT_RULES.yaml](FORMAT_RULES.yaml) 保存 19 条稳定规则：semantic 7 条、presentation 5 条、render_safety 7 条。[来源说明](sources/README.md) 记录提取、合并、确认边界和待确认事项。

- `STANDARD.md`：供人阅读的正式定义，三层分开描述。
- `FORMAT_RULES.yaml` 与 `schemas/format-rules.schema.json`：规则登记和类型约束；编号唯一性由脚本额外检查。
- `examples/good/`：真实结构摘录与紧凑示例；`examples/bad/`：带规则编号的反例。
- `tests/fixtures/` 与 `tests/expected/cases.json`：原始测试输入和明确预期；不修改错误样本来使检测通过。
- `scripts/validate.py`：轻量检测器及一次执行的 fixture 测试。
- `sources/`：授权输入快照、原路径与校验值；仅作证据，不把来源全文当成规范。
- `CHANGELOG.md`：记录规则语义、合并、退出、schema 与检测行为变化。

## 执行验证

在 WSL2 Ubuntu 的项目目录执行。Markdown 检测仅需 Python 3.10+ 标准库；schema 和测试命令还需 PyYAML 与 jsonschema。本轮使用现有 Python 3.12.3 环境，未修改系统依赖。干净环境可自行建立虚拟环境：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install PyYAML jsonschema
.venv/bin/python scripts/validate.py --schema
.venv/bin/python scripts/validate.py --test
.venv/bin/python scripts/validate.py --strict STANDARD.md examples/good/compact.md
```

已有依赖时直接使用 `python3 scripts/validate.py --test`。检查其他文件用 `python3 scripts/validate.py path/to/document.md`；支持多个文件，路径有空格时加引号。`--json` 输出带文件、行号、稳定规则编号与级别的数组；`--strict` 将 WARNING 也视为不通过。退出码 0 表示所选门槛通过，1 表示检测或测试不通过，2 表示输入或依赖错误。单独扫描坏例返回非零是预期行为；测试命令核对预期诊断后返回 PASS。

Formatting Gate 输出标题跳级与密度提示；Render Gate 检查围栏、代码跨度、双星号、字段边界、缩进及简单表格。ERROR 表示违反受支持的明确约束；WARNING 是可疑结构，需人工判断；INFO 提醒检查未自动化的语义关系。原始 Inbox 字段仍能被 Markdown 渲染，但会显示字面星号，因此登记为 WARNING；真正丢失定界符的错误登记为 ERROR。

## 检测范围与维护

检测器不是 Markdown AST，也不是渲染器认证。它支持普通正文、ATX 标题、反引号或波浪号围栏、不同长度代码跨度、显式转义及简单管线表格；只检查双星号强调，不检查单星号、下划线强调。HTML 评论被忽略；HTML 块、复杂引用/列表内围栏、Setext 标题、链接目标、数学扩展、复杂缩进续行与完整强调定界规则不在可靠检测范围。四空格非列表行按代码处理，可能漏检列表续行；文字中的管线在近似表格区域可能误报。

密度阈值只用于提示：三个连续不超过 35 字符的正文段、超过 800 字符的正文段、连续三个空行、至少八列的列表缩进。它们不是正式段落长度、空白比例或嵌套上限。语义反例的测试只核对预期诊断与人工判定记录存在，不能声称自动证明了语义质量。Gold 摘录中合理短段也可能触发提示，应结合上下文复核。

更新时先对照来源提取并去重，再同步规范和规则登记，补充正反样本后执行完整测试。修改规则含义保留编号；合并时保留主编号并将已发布的被合并规则标为 deprecated，不复用旧编号。未经确认的想法留在提案或 experimental，不直接成为 active。测试会核对规则覆盖与首选动作文本，其他语义一致性仍需人工审读。当前无远端发布或自动修改文档功能。
