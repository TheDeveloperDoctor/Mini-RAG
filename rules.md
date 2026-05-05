# Branching & Merge Rules

These rules govern how code lands in this repository. They are non-negotiable.

## Branches

- **`main`** — release-ready. Only fast-forward merges from `dev` after a release.
- **`dev`** — integration branch. All feature work converges here. Always green.
- **`feat/<short-name>`** — feature branches. Branched off `dev`, merged back into `dev`.
- **`fix/<short-name>`** — bug-fix branches. Same flow as feature branches.

## Workflow

1. **Branch off `dev`** — never branch off `main` for feature work.
   ```bash
   git checkout dev
   git pull
   git checkout -b feat/<short-name>
   ```

2. **Build the feature on the feature branch.** Commit early and often. Keep the branch focused on one feature.

3. **Test before merging.** A feature branch must not be merged into `dev` until:
   - All unit, integration, and contract tests pass locally (`make test`).
   - Eval harness still passes if retrieval/chunking/embedding code changed (`make eval`).
   - Lint and type checks pass.
   - The feature has been manually exercised end-to-end where applicable.

4. **Open a pull request into `dev`.** PR description states what changed and why.
   ```bash
   git push -u origin feat/<short-name>
   gh pr create --base dev --title "feat(<scope>): <summary>"
   ```

5. **Merge into `dev` only after tests pass and review is complete.** Use `--no-ff` to preserve history.
   ```bash
   git checkout dev
   git merge --no-ff feat/<short-name>
   git push origin dev
   git branch -d feat/<short-name>
   ```

6. **Release** — when `dev` is stable and ready to ship, fast-forward `main` from `dev`.

## Hard rules

- ❌ No direct commits to `dev` or `main`. Always go through a feature branch.
- ❌ No merging untested code into `dev`. If tests fail, fix them on the feature branch first.
- ❌ No force-pushing to `dev` or `main`.
- ❌ No skipping pre-commit hooks (`--no-verify`) without an explicit reason in the commit message.
- ✅ One feature, one branch. Don't bundle unrelated work.
- ✅ Rebase your feature branch on `dev` before opening the PR if `dev` has moved on.

## Commit message format

```
<type>(<scope>): <short summary>

What changed:
- <specific change>
- <specific change>

Why:
<reason or context>

Author: harisahmed510.00@gmail.com
```

Types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `perf`, `security`
