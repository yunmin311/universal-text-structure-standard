# universal-text-structure-standard

通用文本结构与排版规范，当前版本 0.3.8。先读 [STANDARD.md](STANDARD.md)：它独立解释 Chat Mode、Document Mode、完整段落、真实层级、技术文档组织与输出前检查。[FORMAT_RULES.yaml](FORMAT_RULES.yaml) 保存 19 个稳定规则编号及检测映射，供工具使用，不是第二份写作长文。

长篇任务从 [USAGE.md](USAGE.md) 进入：先读规范，再看[完整 Self-Attention 修订例](examples/good/self-attention.md)，写完后实际修订并验收。[本轮记录](evaluations/long-form-review.md)保留失败依据、改写对照和验证边界；不能再用短交接样本通过推断长文可用。

## 使用与资产职责

先依据语义写作，再运行检查，最后人工复核结构是否服务内容。正文、标题、列表、编号、表格与代码各有职责，任何单一格式都不是目标；自动化 PASS 也不能证明整篇文本语义合格。规则按 semantic 7 条、presentation 5 条、render_safety 7 条分层，未为本轮每项解释增加新编号。

- `STANDARD.md`：完整执行条件、模式差异、例外、Formatting Gate 与 Render Gate。
- `FORMAT_RULES.yaml`、`schemas/format-rules.schema.json`：简短约束、字段契约、版本和 good/bad 映射。
- `examples/good/`：两份脱敏 Gold 改编、仓库编写的长篇教学与技术交接示例，以及一个简短局部示例；不是固定模板。
- `examples/bad/`、`tests/fixtures/`、`tests/expected/`：带规则编号的反例、稳定测试输入及预期；人工判定样本明确保留边界。
- `scripts/validate.py`、`.github/workflows/validate.yml`：轻量本地检查与最小 CI。
- `references/README.md`、`CHANGELOG.md`：来源身份、脱敏说明、规则演变与历史边界。

[参考说明](references/README.md) 区分原始样本的结构依据、脱敏改编和新编教学内容。公开版本不保存私人来源全文或本机路径；私人原文可放入 `.local-sources/`，该目录已被忽略，测试与 CI 均不依赖它。

## 执行验证

使用 Python 3.10+。Markdown 文件检查仅依赖标准库，schema 与测试还需要 PyYAML、jsonschema。已有依赖时直接执行下面两条验证命令；干净环境可以先创建虚拟环境并安装依赖。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install PyYAML jsonschema
.venv/bin/python scripts/validate.py --schema
.venv/bin/python scripts/validate.py --test
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

交付检查用 `python3 scripts/validate.py --strict document.md`，支持多个文件；`--json` 返回文件、行号、规则编号、级别与说明。默认仅 ERROR 导致检查失败，`--strict` 将 WARNING 也作为待解决项返回非零。诊断输出明确区分 BLOCKED、REVIEW_REQUIRED、STATIC_CLEAN，且始终显示 SEMANTIC=NOT_EVALUATED。不带 `--strict` 的调用只用于收集诊断，不能把带警告的退出码 0 当成可交付。退出码 0 是所选门槛通过，1 是检测或测试不通过，2 是输入或依赖错误。运行坏样本得到诊断是预期；fixture 测试比对这些诊断后仍应 PASS。

`--test` 包含原有最小样本、字段修正回归、合法嵌套例外、schema 拒绝案例、规范版本独立性、双向样本引用、正文覆盖锚点、维护文档严格检查及公开工作树路径扫描。覆盖锚点只防止关键内容意外消失，不证明解释质量；工作树扫描也不是历史清理或完整隐私检测。GitHub Actions 在 push 和 pull request 时只安装必要依赖并执行 `--schema`、`--test` 与 CLI / 示例执行回归，没有发布流水线。

## 检测边界与版本维护

Automatic Gate 检查规则数据、引用和支持范围内的闭合及表格形状；数学检查仅覆盖独占行双美元配对、数学块跨入标题/列表/代码围栏和少量裸 TeX 命令，均为警告，不证明数学或显示正确。Heuristic Gate 提示短段、长段、留白、粗体伪标题、深缩进和边界疑点；Human Semantic Gate 判断并列、层级、段落职责、流程方向及交接完整性。完整清单在正式规范中，不把自然语言偏好全部变成数字阈值。

现有检测器支持普通正文、ATX 标题、反引号或波浪号围栏、不同长度代码跨度、显式转义和简单管线表格。它不是 Markdown AST：不完整处理单星号、下划线强调、HTML 块、链接目标、复杂引用/列表内围栏、Setext 标题和完整数学扩展；四空格非列表行按代码处理，可能漏检列表续行。可疑字段与合法嵌套仅警告，确定违反支持范围内的约束才报错；代码字面内容和不确定意图需要人工复核。

密度检测仍沿用既有提示参数：连续三个不超过 35 字符的正文段、超过 800 字符的正文段、连续三个空行、相邻简单列表项之间的单个空白行、至少八列的列表缩进。它们不是正式段落上限，也不执行“2–5 段 / 3–6 句”或减少留白比例。发现误报时保留合法样本、缩小检测范围，不用删除测试或改写正确文档来迁就检测器。

0.2.0 从未编号 schema 迁移到 `schema_version: 1`，并将旧 `version` 字段改为 SemVer 字符串 `standard_version`；`examples` 改为 good/bad 两组路径。此结构迁移已在 CHANGELOG 记录。以后规范版本可独立提升，仅发生结构不兼容才改变 schema_version。规则编号保留，正文扩写不要求照抄登记表动作文本；语义变化需同步规则、例外、样本和版本说明。

当前版本已移除私人快照，但首个提交 `7e49f6c` 仍保留旧内容，不能把本轮脱敏描述成完整公开历史清理。历史改写和 force push 需要单独确认；本轮只更新当前分支内容，不改变仓库可见性。
