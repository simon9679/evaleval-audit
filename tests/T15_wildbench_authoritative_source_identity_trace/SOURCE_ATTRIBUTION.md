# SOURCE_ATTRIBUTION

## Frozen EEE source records

T10 provides exact source record paths and result indices for the affected
rows.

T14 Fix 4 identifies the accepted claim-governing group and exact source ids.

## Frozen OpenEval adapter

Repository:

`evaleval/every_eval_ever`

Commit:

`9bce4136e789ec006c62582f5f9d107d20f8b398`

Path:

`every_eval_ever/adapters/openeval/adapter.py`

At this frozen commit the adapter:

- reads each OpenEval metric `name`;
- accumulates `metric.models`;
- derives EEE metric ids as
  `openeval.<benchmark-slug>.<metric-slug>`;
- preserves the raw metric name in
  `metric_config.additional_details.raw_metric_name`;
- preserves source metric models in
  `metric_config.additional_details.metric_models_json`.

T15 checks the local frozen adapter source before interpreting the trace.

## Official WildBench authority

Repository:

`allenai/WildBench`

Commit:

`d6b8dcaf377d173d031980f97c16e1a82618c03d`

Relevant files:

- `README.md`
- `EVAL.md`
- `src/view_wb_eval.py`
- `leaderboard/data_dir/_merge_results.py`

The official reference distinguishes:

- individual WB Score;
- pairwise WB Reward;
- GPT-4-turbo, Claude-3-Haiku and Llama-2-70B-chat reference channels.

This is supporting semantic context only. T15 does not classify an OpenEval
source metric into one of those official channels using the metric name alone.
