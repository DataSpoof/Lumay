## What changed

<!-- One or two sentences. What does this PR do, and why now? -->

## Why this approach

<!-- Alternatives you considered, and anything a reviewer would otherwise have
     to reverse-engineer from the diff. -->

## How it was verified

<!-- Be specific: commands run and their result, not "tests pass". -->

- [ ] `pytest` passes locally
- [ ] `ruff check .` and `ruff format --check .` are clean
- [ ] Behaviour change is covered by a test that fails without this change
- [ ] Manually exercised the affected endpoint(s), if any

## Risk

<!-- What breaks if this is wrong? Does it change the API contract, the
     database schema, or anything a deployed client depends on? -->

---

### For AI-assisted changes

<!-- Delete this section if no AI assistance was involved. -->

- [ ] I read the full diff, not just the summary
- [ ] Every claim in the description above is one I verified myself
- [ ] No dependency was added without pinning it in `requirements*.txt`
- [ ] No test was weakened, skipped, or deleted to make CI pass
