# Contributing

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # source .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
```

## The loop

```bash
ruff check . && ruff format . && pytest
```

Run that before every commit. CI runs exactly these checks, so a clean local run
means a green pull request.

## Branching and pull requests

`main` is protected: it takes changes only through a pull request with passing
checks. Push directly to `main` and the push is rejected.

```bash
git checkout -b fix/short-description
# ... work, commit ...
git push -u origin fix/short-description
gh pr create --fill
```

Branch names: `fix/`, `feat/`, `chore/`, `docs/` followed by a few words.

Commit messages: a short imperative subject line, then a body explaining *why*
the change is needed — the diff already shows what changed. Wrap at 72 columns.

## What a reviewable pull request looks like

- One concern per PR. Split unrelated fixes apart.
- A behaviour change comes with a test that fails without the change.
- The description says how you verified it, with real command output.
- No unrelated reformatting mixed into a logic change.

## Checks that must pass

| Check | What it enforces |
| --- | --- |
| Ruff lint and format | Style and a set of correctness lint rules |
| Tests (3.11, 3.12) | The full pytest suite on both supported versions |
| CodeQL | Static analysis for common vulnerability classes |

CodeQL findings appear under the repository's Security tab.

## Dependencies

Pin every dependency exactly (`package==1.2.3`) in `requirements.txt`, or
`requirements-dev.txt` if it is only needed for tests and linting. An unpinned
dependency makes builds non-reproducible and CI failures impossible to bisect.
