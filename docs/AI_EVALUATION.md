# AI evaluation and repeatability

The repository currently has no human-labeled golden cases. Do not report
agreement, accuracy, false-positive rates, or prompt/model improvements until
real labels have been added and the evaluator has been run against them.

`ai.evaluation` calculates score exact-agreement and mean absolute error,
pairwise ranking agreement, and binary confusion counts from caller-supplied
values. These functions do not create labels or call an AI provider.

For a future JSONL golden set, use one JSON object per case with these fields.
Human label fields are optional; `ranking_group` and `human_rank` enable
within-group pairwise ranking comparison:

```json
{"case_id":"stable-id","resume_text":"...","rubric":"...","domain_requirements":"...","human_score":42,"ranking_group":"role-1","human_rank":1,"human_positive":true}
```

The example above specifies the schema only; it is not an evaluation case or a
claim about model performance. Store consented, minimized resume text and
human labels in an access-controlled location. Record provider, model, prompt
version, run timestamp, and rubric version with each actual run. Compare the
same cases and labels when evaluating prompt or provider changes.

Run `python scripts/evaluate_golden_dataset.py DATASET.jsonl --output
results.json` to evaluate actual cases. Add `--positive-threshold N` to enable
false-positive/false-negative calculations for cases with `human_positive`
labels. The command reports metrics only for labels present in the dataset.
`python scripts/evaluate_repeatability.py DATASET.jsonl --output
repeatability.json` measures score variation across repeated provider calls.

Prompt v1 is identified by `ai.prompts.versions.v1.PROMPT_VERSION`. Provider
models are selected through `GROQ_MODEL`, `GEMINI_MODEL`, and `OLLAMA_MODEL`.
No optimization has been selected without labeled evaluation evidence.
