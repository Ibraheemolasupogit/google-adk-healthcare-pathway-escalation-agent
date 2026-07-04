# Risk Scoring Methodology

Milestone 2 implements a deterministic operational risk score from 0 to 10. The score is not clinical: it does not assess diagnosis, acuity, treatment need, harm, or clinical prioritisation.

## Factors and Weights

- **Pathway breach severity:** within target 0.0, approaching 1.0, at target 1.5, breached 2.5, substantially breached 4.0.
- **Percentage of target consumed:** under 75% 0.0, 75% to under 100% 0.8, 100% to 125% 1.2, over 125% 2.0.
- **Operational priority:** standard 0.0, urgent 1.0, high 1.5.
- **Missing next event:** 1.0 when no next operational event is recorded.
- **Next event after target:** 1.25 when the next event occurs after the demonstration target point.
- **Operational flags:** 0.4 per flag, capped at 1.2.
- **Substantial breach:** 1.0 when the case is beyond the configured critical threshold.
- **Time-sensitive category:** 0.5 for Cancer and UEC categories.

Every factor is emitted as a `RiskFactor` with a code, name, contribution, explanation, source type and `deterministic=true`.

## Risk Levels

- **LOW:** 0 to 2.
- **MODERATE:** greater than 2 to 4.
- **HIGH:** greater than 4 to 6.
- **CRITICAL:** greater than 6 to 10.

Scores are summed, rounded to two decimal places where displayed, and clamped to 0 to 10.

## Breach and Threshold Inputs

Breach status is derived from the rule's `warning_threshold_percent` and `critical_threshold_percent`:

- consumption above critical threshold: `SUBSTANTIALLY_BREACHED`
- consumption above 100%: `BREACHED`
- consumption exactly 100%: `AT_TARGET`
- consumption at or above warning threshold: `APPROACHING_TARGET`
- otherwise: `WITHIN_TARGET`

## Examples

- A within-target RTT case with no flags remains low risk.
- A Cancer 2WW case near 85% target consumption becomes approaching target and gains warning-related risk.
- A UEC case beyond the critical threshold receives substantial-breach and time-sensitive-category factors.

## Limitations

The model uses demonstration targets and synthetic data only. It is intentionally operational, transparent and simple. It must not be used to make clinical decisions or infer clinical urgency.

## Human Review

Every final output includes `human_review_required=true` and `review_status=PENDING`. Human review is required before any escalation is finalised.
