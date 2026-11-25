# Changelog

## [0.2.0-dev] - 2026-11-25

- Split `ORG-06` and `ORG-08` out of `shared/standards/organization.md` into `shared/standards/titles.md` and relaxed `scripts/rules.py` prefix exclusivity while keeping per-ID uniqueness.
- Embedded `shared/core.md` and `CTX-01`–`CTX-03` into built `SKILL.md` entries via `scripts/package_skills.py`, cleaning embed markers in combined-package role files.
- Unified Guide dependency routing (`[必需]` / `[条件]` / `[回查]`), deduplicated `prohibitions.md` and `voice.md`, and eliminated the `core.md` ↔ `prose.md` cycle.
- Added `skills/humanistic-writing-guide/references/closings.md`, `AUDIT-09`, grounded `PROSE-03` / `CLOSING-03` examples, and evaluation cases `CASE-57`–`CASE-60`.

## [0.1.0] - 2026-11-02

- 新增协调入口、Guide 和 Audit，以及共享的决策契约、领域标准、加载协议和工具说明。
- Guide 新增成文、修订、转换、解释、语域和标题方法。Audit 新增审查方法与治理禁令。
- 语言标准新增表演性表达禁令。组织标准新增标题命名规则和 14 项标题禁令，并接入 Guide、Audit 与行为案例。
- 新增 Release 工作流。标签与 `VERSION` 一致时运行检查和测试，并发布协调包、Guide、Audit 与源码归档。
