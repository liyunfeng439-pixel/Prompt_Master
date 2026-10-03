# Shot Budget Controller V10.9.0

30s default: target 6–7 core Beats, hard_max 7 Beats. Each Beat may contain 1–3 camera Shots. Shot count has no fixed 7-shot hard cap.

Semantic compiler may compress text inside a shot but may not delete the only visible evidence required to preserve action/result/recovery causality. Beat compression and Shot planning happen before SHOT_IR; post-SHOT_IR text compression cannot influence Shot Budget and cannot remove physical events.


## V10.9.0 Budget-Aware Feedback
Shot budget is a constraint, not a fixed narrative template. The default 6–7 Beat allocation may be rebalanced by scene type, while the 30-second hard maximum remains 7. Budget pressure feeds back to Combat Director and Beat Graph before final SHOT_IR emission. Text compression after SHOT_IR cannot change Shot count or event existence.
