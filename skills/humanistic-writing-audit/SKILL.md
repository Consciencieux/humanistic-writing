---
name: humanistic-writing-audit
description: 通用自然语言文稿的只读审查与版本比较。依据作品目的和实际上下文检查目标替代、机械处理、修改越界、内容损失及未完成问题，给出有位置和依据的诊断。
license: MIT
---

# Audit：语义审核与改动判定

检查文本实际完成了什么，以及修改改变了什么。对确认违反禁令的行为明确要求修复；无违规的有效表达保留。普通非虚构文本中确认的表演性口语、装饰性幽默、金句、假互动、装饰性引号和标题钩子，按 AUDIT-06 直接判定违规，不建议更换同义文案。

## 启动

完整读取[决策契约](../../shared/core.md)、[加载协议](../../shared/protocols/context.md)、[审核方法](references/review.md)和[治理禁令](references/prohibitions.md)。使用当前请求、实际稿件及必要上下文作为判断依据。

| 审查对象 | 读取的标准 |
| --- | --- |
| 内容是否形成、必要细节是否丢失 | [内容](../../shared/standards/content.md) |
| 篇章职责、顺序、重复或长度 | [组织](../../shared/standards/organization.md) |
| 句段表达、语言痕迹与实际功能 | [语言](../../shared/standards/prose.md) |
| 理由、因果、比较或结论强度 | [推理](../../shared/standards/reasoning.md) |
| 作者立场、人物声音或语域 | [声音](../../shared/standards/voice.md) |
| 事实、引文或来源支持 | [来源](../../shared/standards/sources.md) |
| 文件、版本差异、计数或成品 | [工具](../../shared/tooling/capabilities.md) |

[索引](../../shared/INDEX.md)供定位。全文审查读取完整范围及所有适用标准；专项审查不扩大为其他任务。版本比较需要原稿、改稿和修改请求；缺失材料只限制相关判定。

## 输出与交接

按审核方法给出位置、实际影响、违反的条件与修复方向，保留有效内容和授权边界。不得只给“全文更自然”“多一点思考”等无法定位的指示。

只读请求结束于诊断。已授权检查并修改时，将确认问题连同基线和需保留的关系交给 Guide；同一 Agent 切换职责后执行修订。Audit 不边审边写，不要求为消除形式命中重做无关部分。修订后的核对聚焦原问题与真实影响。
