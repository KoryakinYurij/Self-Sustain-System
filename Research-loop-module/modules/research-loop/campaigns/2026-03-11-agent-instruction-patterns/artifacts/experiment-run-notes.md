# Experiment Run Notes

## Scope checked

- Reviewed `modules/research-loop/campaigns/2026-03-11-agent-instruction-patterns/proposal.md`.
- Reviewed `modules/research-loop/campaigns/2026-03-11-agent-instruction-patterns/experiment.md`.
- Reviewed `agents-lab/README.md`.
- Inspected the current repo-grounding delta in `agents-lab/README.md`.

## Observed change

- The concrete repo change is a single added bullet under `Что можно улучшать`:
  - `краткую карту репозитория для grounding`

## Evidence limits

- No task transcripts, benchmark runs, or before/after agent outputs were provided for the three cases.
- No instruction template change was shown that makes repo-map grounding required or even recommended at execution time.
- No enforcement mechanism or examples were added that would let us attribute agent behavior changes to this patch alone.

## Case assessment notes

- Case 1: naming the pattern is directionally helpful, but it does not demonstrate that agents will consult repo structure before editing within an existing module.
- Case 2: there is no evidence that search behavior becomes more local or less chaotic in unfamiliar parts of the repo.
- Case 3: the patch is small enough that it probably does not add overhead, but that remains an inference, not a tested result.

## Conclusion

- Conservative read: this is a valid documentation nudge, not a validated behavior change.
- Recommendation: needs-more-testing.
