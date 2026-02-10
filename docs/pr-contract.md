## PR → Version Contract (finance-app)

### 0) Scope

This contract applies to **every Pull Request targeting `master`**.

---

## 1) Source of truth for change type

**The source of truth is the PR title** (not labels, not commits).

### Mandatory PR title format (Conventional PR Title)

```
<type>(<scope>)?: <subject>
```

* `<type>` allowed: `feat | fix | chore`
* `<scope>`: optional. `[a-z0-9-]+` (e.g. `auth`, `users`, `db`, `ci`, `docker`, `deps`)
* `<subject>`: required, minimum 8 characters, must **not** end with a period.

**Suggested strict regex:**

```
^(feat|fix|chore)(\([a-z0-9-]+\))?: (?!.*\.$).{8,}$
```

Valid examples:

* `feat(users): add user profile endpoint`
* `fix(db): handle unique constraint conflict`
* `chore(ci): add pr title validation`

Invalid examples:

* `feature: add users` (invalid type)
* `fix: ok.` (too short / ends with a period)
* `feat(users) add endpoint` (missing `: `)

---

## 2) Canonical version and where it lives

The version is read **only** from:

* `pyproject.toml` → **`[project].version`**

Required format: strict SemVer `MAJOR.MINOR.PATCH`
(no `-rc`, no `+build` suffixes)

Regex:

```
^\d+\.\d+\.\d+$
```

---

## 3) Base rule: every PR must bump the version

**Every PR must modify the `version` field in `pyproject.toml`.**
If the version does not change → **rejected**.

---

## 4) Bump rules (exactly +1)

The version in `master` (base) is compared against the version in the PR branch (head).

Let base be `A.B.C` and head be `X.Y.Z`.

---

### 4.1 `feat` → minor bump

Must satisfy **exactly**:

* `X = A`
* `Y = B + 1`
* `Z = 0`

Example:

* base `0.3.7` → head **`0.4.0`**

---

### 4.2 `fix | chore | docs | refactor | test | revert` → `A.B.(C+1)`` → patch bump

Must satisfy **exactly**:

* `X = A`
* `Y = B`
* `Z = C + 1`

Example:

* base `0.3.7` → head **`0.3.8`**

---

## 5) When `MAJOR` (`+1.0.0`) is allowed

Although the project is currently in `0.y.z` (pre-1.0) and SemVer allows more freedom, this contract enforces strict automation.

### 5.1 Major bump only for breaking changes

A **major bump is allowed only if the PR title explicitly indicates a breaking change**.

**Format:**

```
feat!: ...
fix!: ...
chore!: ...
```

Then the version must satisfy:

* `X = A + 1`
* `Y = 0`
* `Z = 0`

Examples:

* base `0.9.4` → head **`1.0.0`**
* base `1.2.3` → head **`2.0.0`**

> Note: This is intentionally strict. While in `0.x` you might want to signal large changes without jumping to `1.0.0`, that introduces ambiguity. This contract avoids that entirely.

---

### 5.2 Additional requirement (optional but recommended)

If `!` is used, the PR **should include** a section in its description:

```
BREAKING CHANGE:
- ...
```

(This can be validated later; for now, the `!` in the title is sufficient.)

---

## 6) Rejection rules

A PR is **rejected** if **any** of the following occurs:

* The title does **not** match the contract regex.
* The type is not one of `feat | fix | chore`
  (or `feat! | fix! | chore!` when breaking is enabled).
* The `pyproject.toml` version is not changed.
* The version bump does not exactly match the rule for the PR type
  (including resetting patch to `0` on minor bumps).
* The head version is not strict SemVer `x.y.z`.

---

## 7) Standard error messages (developer-facing)

Recommended error messages:

* **Invalid title**

  > “PR title must match: `<type>(<scope>)?: <subject>` where type ∈ {feat, fix, chore}. Example: `feat(users): add ...`”

* **Version not bumped**

  > “`pyproject.toml` version must be bumped for every PR.”

* **Incorrect bump**

  > “PR type is `fix` → expected patch bump: base `0.3.7` → head `0.3.8`, got `0.4.0`.”

---

## 8) Explicit exclusions (contract closed)

The following are **explicitly out of scope** for now:

* pre-releases (`-alpha`, `-rc`)
* build metadata (`+build`)
* larger-than-minimum bumps
  (e.g. allowing `0.3.7 → 0.3.9` for a `fix`)

**Not allowed**: the contract requires an exact `+1` bump.
