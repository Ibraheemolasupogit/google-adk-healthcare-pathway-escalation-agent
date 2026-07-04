# Data Dictionary

All data is synthetic demonstration data only.

## Pathway Rule Fields

- `pathway_code`: controlled code such as `CANCER_2WW`.
- `pathway_name`: human-readable pathway name.
- `pathway_category`: `CANCER`, `RTT` or `UEC`.
- `target_value`: positive numeric target value.
- `target_unit`: `HOURS` or `DAYS`.
- `target_description`: plain-language target description.
- `comparison_operator`: currently `LESS_THAN_OR_EQUAL`.
- `warning_threshold_percent`: percentage used for approaching-target classification.
- `critical_threshold_percent`: percentage used for substantially-breached classification.
- `source_title`: demonstration source label.
- `source_type`: source category.
- `source_url_placeholder`: placeholder only; no live authoritative URL is invented.
- `effective_date_placeholder`: placeholder effective-date field.
- `demonstration_only`: must be true.
- `validation_required`: must be true.
- `notes`: warning and validation notes.

## Synthetic Case Fields

- `case_id`: synthetic identifier such as `SYN-CANCER-2WW-001`.
- `synthetic`: must be true.
- `pathway_code`: supported demonstration pathway code.
- `referral_or_arrival_datetime`: timezone-aware start datetime.
- `assessment_datetime`: timezone-aware assessment datetime.
- `current_stage`: synthetic operational stage.
- `priority`: `STANDARD`, `URGENT` or `HIGH`.
- `next_event_datetime`: optional timezone-aware next operational event.
- `operational_flags`: list of synthetic operational flags.
- `source_system`: synthetic source-system label.
- `notes`: synthetic operational notes.

## Output Fields

Final assessments and escalation drafts include case ID, pathway code and name, target, elapsed time, breach status, variance, risk score, risk level, risk factors, recommended actions, assumptions, warnings, demonstration-only flag, human review flag, review status and audit trace ID.

## Prohibited Fields

Do not include patient names, NHS numbers, hospital numbers, dates of birth, addresses, postcodes, phone numbers, email addresses, or real clinical notes.
