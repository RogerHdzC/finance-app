## Summary
**What changed and why?**
- Brief, clear description of the change.
- Link related issues/PRs if applicable.

---

## PR Type (derived from title)
> The PR title **must** follow the Conventional Commit format and is the source of truth.

- [ ] feat
- [ ] fix
- [ ] docs
- [ ] refactor
- [ ] test
- [ ] chore
- [ ] revert
- [ ] breaking (`!` in title)

**Expected title format:**
```

<type>(<scope>)?: <subject>

````

Examples:
- `feat(ci): add PR gates`
- `fix(db): handle unique constraint`
- `docs(readme): update contribution guidelines`
- `feat!(api): remove deprecated endpoint`

---

## Versioning
> `pyproject.toml` **must be updated** and must match the PR type rules.

- Base version: `A.B.C`
- Head version: `X.Y.Z`

**Bump rules (exact):**
- `feat`  → `A.(B+1).0`
- `fix | chore | docs | refactor | test | revert` → `A.B.(C+1)`
- `*!` (breaking) → `(A+1).0.0`

- [ ] Updated `apps/api/pyproject.toml`
- [ ] Version bump matches the PR type rules
- [ ] Branch up to date with master

---

## Testing
- [ ] Tests executed locally:
```bash
  docker compose exec api uv run pytest
````

* [ ] No failing tests introduced

---

## Notes / Risks

* Database migrations?
* Backward compatibility concerns?
* Deployment or rollback considerations?
* Performance or security implications?

---

## BREAKING CHANGE (required if `!` is used)

**Describe the breaking change clearly:**

* What breaks?
* Who is affected?
* Migration steps (if any).

Example:

```md
BREAKING CHANGE:
- Removed `/api/v1/legacy-users`
- Clients must migrate to `/api/v2/users`
```