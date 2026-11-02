# Humanistic Writing

通用自然语言写作 Skill。根据作品目的与实际内容决定写什么、怎样写、改哪里以及何时完成，覆盖构思、成文、续写、修订、翻译、整理与审核。

[English](README.en.md)

## 使用

从[协调入口](SKILL.md)开始，或直接进入[Guide](skills/humanistic-writing-guide/SKILL.md)写作与修订、[Audit](skills/humanistic-writing-audit/SKILL.md)做只读审查。

> 根据这些材料写一篇短文，分析讨论时间增加却没有更多人发言的原因。

> 第二段读起来太累，整理一下，保留支撑判断的内容，给我完整稿。

> 比较两稿是否解决了原问题，有没有损失原有内容，只给分析。

Guide 主动发展内容并选择表达方法。修订以最新原稿为基线，先确定实际变化，再替换目标区域；未改文字沿用原文。Audit 根据上下文检查确认的违规行为，交付位置、影响和修复方向。

## 标题与目录

支持文章主标题和各级小标题的拟定、修改与审查。Guide 从实际内容提炼主要对象或关系，提供面向说明、汇报、读书笔记和技术文档的[命名方法](skills/humanistic-writing-guide/references/headings.md)；Audit 结合正文执行[完整标题禁令](shared/standards/organization.md#org-08)。小标题长度仅作编辑提示，主标题按全文重心与实际格式处理。只改标题时保留正文。

## 写作要求与具体禁令

宏观治理继续以[决策契约](shared/core.md)为基础：从内容决定写法、修改幅度与停止条件。针对已发现的表演性写法，[语言标准](shared/standards/prose.md#prose-09)明确**直接禁止**主持人式串词、假互动、装饰性幽默与廉价比喻、金句、排版重音及虚构对立；[组织标准](shared/standards/organization.md#org-06)禁止批量标题钩子。不设计这些违规行为的“适量使用配方”，也不以替换同义句逃避禁令。

真正需要能力建设的事项同时有正面方法：Guide 的[解释与信息展开](skills/humanistic-writing-guide/references/explain.md)负责论证中间层、术语和数据的实际含义，[语域与表达场合](skills/humanistic-writing-guide/references/registers.md)负责口头汇报、学术／正式表达和个人声音；[内容](shared/standards/content.md#content-06)、[声音](shared/standards/voice.md#voice-06)等共享标准供 Guide 与 Audit 共同判断。Audit 的[严格禁令](skills/humanistic-writing-audit/references/prohibitions.md#audit-06)对确认的违规作明确裁决。

这里禁止的是实际的表演性行为；真实引文、作者已提供的文字及明确授权的戏剧或喜剧任务依其内容处理。审核不得仅凭关键词、标点数量、句长和格式相似作出违规判定。具体能力在实际适用时加载，不要求每次写作检查全部条文。

## 架构

| 责任 | 位置 |
| --- | --- |
| 任务路由、授权与角色交接 | `SKILL.md` |
| 内容判断、手段选择、变更与完成的共同契约 | `shared/core.md` |
| 正面的成文、修订、转换、解释与语域方法 | `skills/humanistic-writing-guide/references/` |
| 审核方法与根因治理禁令 | `skills/humanistic-writing-audit/references/` |
| 内容、组织、语言禁令、推理、声音、来源的领域标准 | `shared/standards/` |
| 当前稿、资料加载与跨轮接续 | `shared/protocols/context.md` |
| 宿主工具调用、定位编辑与差异核对 | `shared/tooling/capabilities.md` |

共同启动只读取决策契约和上下文协议。随后进入当前角色方法，在实际需要时读取专项标准。语言标准在成文或语言审查时加载；[共享索引](shared/INDEX.md)供查找，不是每次写作的全库清单。

“简洁、深入、自然”等要求由具体内容判断，允许不同位置采取不同动作，也允许保留已经合适的内容。明确字数、格式和术语按任务执行。各文件的责任与交接见[架构](docs/architecture.md)。

## 源码目录

```text
humanistic-writing/
├── SKILL.md
├── skills/
│   ├── humanistic-writing-guide/
│   │   ├── SKILL.md
│   │   └── references/        # compose / revise / transform / explain / registers
│   └── humanistic-writing-audit/
│       ├── SKILL.md
│       └── references/        # review / prohibitions
├── shared/
│   ├── core.md
│   ├── INDEX.md
│   ├── standards/
│   ├── protocols/
│   └── tooling/
├── assets/                    # 可选接续状态
├── docs/                      # 文件责任与交接
├── evals/                     # 实际行为案例和原稿材料
├── scripts/                   # 资源定位、计数与封装
└── tests/                     # 工具与分发回归
```

## 定位与计数

使用 Skill 本身不需要 Python。可选脚本使用 Python 3.10+：

```sh
python -m pip install -r requirements.txt
python scripts/rules.py --list
python scripts/rules.py EDIT-02 --file
python scripts/rules.py AUDIT-03
python scripts/text_stats.py article.md --json
```

编号来自实际 Markdown 标题。定位器在源码、完整安装包及独立角色包中读取各自拥有的资源。`--file` 返回所属文件全文，适合首次加载。计数工具只处理篇幅，不修改原文。

## 分发

```sh
python scripts/package_skills.py check
python -m unittest discover -s tests -v
python scripts/package_skills.py build
python scripts/package_skills.py source
```

`source` 在 `dist/` 生成完整源码 ZIP，含文档、案例、脚本和测试。解压后可直接作为仓库使用。归档排除 `.git`、构建输出、缓存与评估运行记录。

`build` 生成协调包与独立 Guide / Audit 包。协调包携带两个内部角色，独立包只携带本角色的方法及共享能力；每个安装包只有一个 `SKILL.md`，内部链接由构建器重定位。安装时保留整个目录。

资源检查与工具测试验证加载路径和封装行为。实际写作效果按[行为评估](evals/README.md)比较原稿、请求与模型输出。维护参阅[CONTRIBUTING](CONTRIBUTING.md)。

中文为权威版本，其他语言按其语法和语用执行。[MIT 许可](LICENSE)。
