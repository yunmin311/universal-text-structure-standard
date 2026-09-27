# Changelog

## 0.2.0 — 2026-09-27

- ADD：完整定义 Chat Mode / Document Mode、段落职责、技术内容顺序、长期交接与三层 Formatting Gate；补充最小 GitHub Actions。
- UPDATE：以当前明确确认政策为最高优先级，扩写独立可读的规范；REN-004 默认技术实体只用 inline code，合法嵌套仅作例外。
- MERGE：模式、长列表、标题空壳、结构选择及留白解释并入原有 19 条规则职责，不逐句增加编号。
- SECURITY：私人来源移出受版本控制的工作树，公开资产仅保留脱敏摘录、改编教学与回归案例；旧历史仍含私人内容，未执行历史改写或强推。
- UPDATE：从未编号结构迁移到 schema_version 1；standard_version 使用独立 SemVer，examples 分为 good/bad 并进行双向引用检查。
- VALIDATOR：新增默认字段嵌套警告及例外测试，保留 ERROR / WARNING / INFO 边界；用正文覆盖与公开引用检查替代原文哈希依赖和逐字镜像检查，CI 不依赖私人源文件。

## 0.1.0 — 2026-09-27

- ADD：从本轮确认要求与 B 级结构样本建立三层规则、稳定编号及 JSON Schema。
- MERGE：将段落完整性、并列列表、真实层级、流程方向等重复表述合并为单一概念。
- ADD：加入 Project Inbox 的结构摘录和原始字段问题回归样本。
- Validator behavior：加入轻量 Formatting / Render Gate、分级诊断、规则唯一性检查和 fixture 测试；语义判断保留人工复核边界。
