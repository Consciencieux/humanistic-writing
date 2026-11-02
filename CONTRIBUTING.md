# 维护说明

先按[架构](docs/architecture.md)找到责任位置。根因判断改 shared/core.md，动作选择改 Guide 方法，违规条件改 Audit 禁令，领域语义改共享标准。入口和索引维护真实调用路径。

一个修订应改变实际决策：面对怎样的内容，选择怎样的动作，哪些有效作用继续保留，什么时候完成。案例要同时覆盖需要行动与应当保留的情境。词频、句长和改动比例不作质量判据。

角色方法保留在各自 references 中。共享层不依赖角色，独立安装包不需要兄弟角色。相对链接采用内联 Markdown；稳定职责沿用原编号，删除职责同步迁移引用。

```sh
python scripts/package_skills.py check
python -m unittest discover -s tests -v
python scripts/package_skills.py build
python scripts/package_skills.py source
```

按变更检查资源、定位及封装；既有测试可在结构迁移后更新有效场景。模型行为按[评估说明](evals/README.md)实际运行，未运行的案例不写通过结果。评估材料和运行记录不进入安装包，运行记录也不进入源码归档。

分发前更新 VERSION。build 构建自包含协调包及独立角色包，source 归档完整源码。两者都不执行远程发布。
