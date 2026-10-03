# Ambiguity Policy — 6.4

Classify missing information as:
- HARD_UNKNOWN: blocks a required invariant or would materially change identity/outcome.
- SOFT_UNKNOWN: may remain unknown without contradiction.
- DEFAULTABLE: safe production convention may be chosen and marked as a default.
- USER_CONFIRM_REQUIRED: multiple plausible interpretations materially diverge.

Ask only for USER_CONFIRM_REQUIRED items. Never ask for information that can be safely defaulted without changing hard constraints.
