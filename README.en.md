# Humanistic Writing

General natural-language composition, revision, transformation and review. The skill selects actions from the purpose and actual content of the work, rather than optimizing recurring surface features.

[中文（authoritative）](README.md)

## Entry points

Start with [the coordinator](SKILL.md). [Guide](skills/humanistic-writing-guide/SKILL.md) develops content and edits drafts. [Audit](skills/humanistic-writing-audit/SKILL.md) reviews text and revision effects without editing it.

Revision uses the latest designated draft as its baseline. Guide decides what needs to change, creates replacement passages, and retains untouched text from the baseline. Audit applies strict semantic prohibitions to confirmed failures and passes located repair needs back to Guide when revision is authorized.

## Concrete guidance and hard prohibitions

The decision contract governs why content is written or edited, where changes belong, and when to stop. In ordinary nonfiction, explanatory, and formal presentations, the shared prose standard directly forbids performative banter, fake audience interaction, decorative jokes and analogies, slogan-like punchlines, ornamental quotation marks, and fabricated contrasts. The organization standard forbids bulk-generated headline hooks. These are prohibited behaviors, not frequency quotas or individual banned words.

Guide adds positive methods for [substantive explanation](skills/humanistic-writing-guide/references/explain.md) and [audience/register choices](skills/humanistic-writing-guide/references/registers.md), including accessible spoken delivery and accurate academic prose. Audit enforces confirmed violations through its [prohibitions](skills/humanistic-writing-audit/references/prohibitions.md) while protecting legitimate source quotations and explicitly commissioned creative work.

## Responsibilities and loading

`shared/core.md` owns the decision contract: intended outcome, content before technique, context-sensitive choice, bounded change, and completion. Guide owns composition, revision, transformation, explanation and register methods. Audit owns review methods and governance prohibitions. Shared standards cover content, organization, prose, reasoning, voice and sources.

Every entry starts with the core and context protocol, then loads the current role's method. Domain standards are selected as needed. Read the prose standard when composing prose or reviewing language; the shared index is optional navigation. Shared resources have no dependency on role methods.

The contract is executed by the host model. Existing host tools handle targeted edits and text differences. Model behavior is evaluated separately from resource and packaging checks.

## Optional tools

The scripts require Python 3.10+:

```sh
python -m pip install -r requirements.txt
python scripts/rules.py EDIT-02 --file
python scripts/rules.py AUDIT-03
python scripts/text_stats.py article.md --json
python scripts/package_skills.py check
python -m unittest discover -s tests -v
```

The locator reads actual Markdown definitions in both source and installed layouts. Standalone packages expose only their own role methods and shared standards.

## Distribution

```sh
python scripts/package_skills.py build
python scripts/package_skills.py source
```

`build` creates self-contained coordinator, Guide and Audit archives. `source` archives the complete repository, including documentation, evaluation cases and tests, excluding builds, caches, evaluation runs and Git metadata. Neither command publishes remotely.

See [architecture](docs/architecture.md), [behavioral evaluation](evals/README.md), and [contribution guidance](CONTRIBUTING.md). [MIT license](LICENSE).

## Titles and section headings

Use the Guide's [heading method](skills/humanistic-writing-guide/references/headings.md) to name the actual subject or relationship, and the shared [heading standard](shared/standards/organization.md#org-06) and [prohibitions](shared/standards/organization.md#org-08) to review the result. Article titles and section headings have distinct scopes. Chinese heading-length ranges are editing cues, not quality scores or automatic failure thresholds. A heading-only request preserves the body text.
