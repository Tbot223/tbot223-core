[한국어 (Korean)](../../ko/FOR_LLM/DOCUMENTATION_CONTRACT.md)

> This document is based on v4.0.0.

# Documentation Contract for LLM

> Execution guide for writing or updating repository Markdown documents other than Python docstrings.

## Read First

Read [../FOR_HUMAN/DOCUMENTATION_CONTRACT.md](../FOR_HUMAN/DOCUMENTATION_CONTRACT.md) first.

- The human-facing document is the canonical rule set.
- This file is an execution guide, not a replacement summary.

## Goal

- Unify document style without making every file mechanically identical.
- Preserve the target document type.
- Keep English and Korean file paths aligned when both files exist.
- Exclude TODO.md from this contract.
- Target GitHub Flavored Markdown as the default Markdown dialect.
- Add top-of-file version-basis metadata to README, Guide, Reference, and Contract docs.

## Workflow

1. Identify the document type: README, guide, reference, release notes, or contract.
2. Identify the target reader and current language.
3. If the file is a README, Guide, Reference, or Contract, identify a verifiable version basis from the repository.
4. Use the top metadata order `language switch link -> version basis -> title`. If no sibling language file exists, the file may start with `version basis -> title`.
5. Make the file's purpose visible near the top.
6. Apply the template for that document type.
7. Prefer structures that render correctly on GitHub.
8. Keep links relative and local to the current language tree.
9. If a bilingual pair exists, preserve matching path and filename.

## Type Heuristics

### README

- Entry-point file.
- Orientation and framing matter more than completeness.
- Should link outward to deeper docs.

### Guide

- Task, migration, or walkthrough flow.
- Needs sequence, transitions, or staged structure.
- Should help the reader move from one state to another.

### Reference

- Lookup-style information.
- Needs structured sections and low ambiguity.
- Examples are optional and should clarify behavior, not retell the whole system.

### Release Notes

- Version-based reporting.
- Group by change type.
- Keep it factual.

### Contract

- Rule document.
- Needs scope and normative language.
- Use MUST, SHOULD, and MAY when helpful.

## Extraction Rules

- Preserve verified facts from the repository.
- Do not invent commands, versions, migration guarantees, or test outcomes.
- If the exact release version cannot be verified, use a verifiable temporary basis such as `current dev branch` or `main branch HEAD` instead of inventing a release number.
- Do not silently change a document into a different type.
- Do not copy README tone into contracts or references.
- Do not introduce avoidable markdownlint warnings in new or edited sections.
- If the file already has markdownlint issues, reduce obvious low-cost ones when practical.
- Do not leave planning text, TODO markers, or chatty filler in final output.

## Bilingual Rules

- If the sibling language file exists, keep the same path and filename.
- Section order may differ, but the scope should stay aligned.
- Add a language switch link near the top when the paired file exists.
- When one file in a bilingual pair changes, review whether the version basis should also be updated in the sibling file.

## Before Finalizing

- If this is a README, Guide, Reference, or Contract, is the version basis present at the top?
- Is the version basis grounded in verifiable repository facts?
- Does the first block tell the reader what this file is for?
- Does the structure match the document type?
- Does it render cleanly on GitHub?
- Are headings shallow enough to scan?
- Are code fences tagged?
- Are links relative?
- Did you avoid adding new markdownlint warnings?
- Did you remove draft-only text?

## Paste-Ready Prompt

```text
First read docs/CONTRACT/en/FOR_HUMAN/DOCUMENTATION_CONTRACT.md,
then use docs/CONTRACT/en/FOR_LLM/DOCUMENTATION_CONTRACT.md as the execution guide
to write or revise the Markdown document I just gave you.
Keep the correct document type, preserve verified facts only,
for README, Guide, Reference, and Contract docs place the top metadata as language link -> version basis -> title,
target GitHub Flavored Markdown and clean GitHub rendering,
keep bilingual file paths aligned when a sibling file exists,
if the exact release version is unknown, use a verifiable temporary basis instead of inventing one,
avoid adding new markdownlint warnings,
and do not leave TODO-style or draft-only text in the final document.
```
