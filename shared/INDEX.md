# 共享能力索引

需要查找专项标准时使用。创作、修订、转换与审核方法从各自角色入口进入；本索引只维护共享能力的定位。

<a id="capabilities"></a>
## 按当前内容选择

| 需要处理的内容 | 唯一维护文件 | 常用位置 |
| --- | --- | --- |
| 任务、内容判断、取舍、授权与完成 | [决策契约](core.md) | CORE-01～CORE-05 |
| 角度、素材、细节与展开分量 | [内容](standards/content.md) | CONTENT-01～CONTENT-05 |
| 先后关系、段落职责、篇幅与形式 | [组织](standards/organization.md) | ORG-01～ORG-05 |
| 成文与语言审核中的句段表达 | [语言](standards/prose.md) | PROSE-01～PROSE-08 |
| 依据、因果、比较、结论与求解程度 | [推理](standards/reasoning.md) | LOGIC-01～LOGIC-05 |
| 作者、人物、视角、语域与立场归属 | [声音](standards/voice.md) | VOICE-01～VOICE-05 |
| 材料范围、事实、引用与来源关系 | [来源](standards/sources.md) | SRC-01～SRC-05 |
| 读取、研究、统计与定位编辑 | [工具](tooling/capabilities.md) | TOOL-01～TOOL-04 |
| 完整读取、当前稿、恢复与交接 | [上下文](protocols/context.md) | CTX-01～CTX-04 |

先按真实任务选择能力，首次使用读取完整文件。入口与操作方法决定加载时机，本表不构成每次写作的检查清单。

<a id="feedback"></a>
## 常见反馈的回查位置

| 当前待判断事项 | 对应内容 |
| --- | --- |
| “有思考”应展开什么 | [内容重心](standards/content.md#content-01)、[内容分量](standards/content.md#content-04)、[理由与结论](standards/reasoning.md#logic-02) |
| 长度来自重复还是必要关系拥挤 | [段落职责](standards/organization.md#org-02)、[长度](standards/organization.md#org-05)、[句间承接](standards/prose.md#prose-03) |
| 一种语言形式在这里有什么作用 | [修辞](standards/prose.md#prose-06)、[功能](standards/prose.md#prose-08)、[声音](standards/voice.md#voice-02) |
| 改写是否改变了作者责任或判断强度 | [真实作者](standards/voice.md#voice-04)、[范围与强度](standards/reasoning.md#logic-03)、[归属](standards/sources.md#src-03) |
| 如何保留当前稿并查看真实改动 | [变更边界](core.md#core-04)、[定位编辑](tooling/capabilities.md#tool-04)、[接续](protocols/context.md#ctx-04) |

[编号定位工具](../scripts/rules.py)从实际二级标题读取编号，支持共享标准和当前安装包的角色方法：`python scripts/rules.py CORE-03 --file`。仅安装 Audit 时可查询 REVIEW、AUDIT 及共享编号；仅安装 Guide 时可查询 WRITE、EDIT、XFORM 及共享编号。
