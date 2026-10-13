---
name: commit_generator
version: 1.0.0
description: Generate Conventional Commit messages from Git diffs, staged changes, and issue references.
author: kuroLabs-ai
tags: [git, commits, conventional-commits, changelog, vcs]
---

# Commit Generator Skill Routine

Disciplined procedure for inspecting Git changes and composing clear, accurate Conventional Commit messages (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`).

## Specification Standard
Follows the **Conventional Commits 1.0.0** format:
```text
<type>[optional scope]: <short summary in imperative mood>

[optional body explaining motivation and context]

[optional footer(s) such as BREAKING CHANGE or Closes #123]
```

## Routine Steps:

1. **Diff Inspection & Staging Analysis**:
   - Inspect staged changes (`git diff --staged`) or unstaged changes (`git diff`).
   - Categorize affected directories, components, or modules to identify scope (e.g. `feat(auth)`, `fix(parser)`, `docs(readme)`).

2. **Classification of Change Type**:
   - `feat`: A new user-facing feature or capability.
   - `fix`: A bug fix or error mitigation.
   - `docs`: Documentation only changes.
   - `style`: Changes that do not affect the meaning of the code (formatting, white-space).
   - `refactor`: A code change that neither fixes a bug nor adds a feature.
   - `perf`: A code change that improves performance.
   - `test`: Adding missing tests or correcting existing tests.
   - `chore`: Build process, dependency updates, or auxiliary tool changes.

3. **Message Formulation**:
   - Subject line must be concise (<= 72 characters) and use imperative, present tense ("add", "fix", "change", not "added" or "adds").
   - Do not capitalize first letter after colon; do not end with a period.
   - If breaking changes exist, include `BREAKING CHANGE:` in the footer or append `!` before the colon (e.g. `feat(api)!: drop v1 endpoints`).

4. **Multi-Commit Decomposition (When Applicable)**:
   - If the working tree contains independent logical units (e.g., a bug fix combined with an unrelated refactor), recommend staging and committing each unit separately.
