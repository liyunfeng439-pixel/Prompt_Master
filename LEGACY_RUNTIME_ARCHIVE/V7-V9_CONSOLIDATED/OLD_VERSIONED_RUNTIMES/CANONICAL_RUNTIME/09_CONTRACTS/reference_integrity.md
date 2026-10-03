# Reference Integrity Contract — 6.4

This hardens existing Runtime links; it adds no new combat capability.

## Required identity links
- every Beat/Transition has a unique `beat_id` or `transition_id`;
- every physical event has a unique `event_id`;
- every Shot references existing `observed_beat_ids`;
- every Decision references an existing actor and selected action;
- every Ability event/actor reference resolves when present;
- every `source_event` resolves to an existing event or explicit external input record.

## Failure rules
- broken reference = QA FAIL;
- orphaned derived state = QA FAIL;
- missing predecessor/successor is allowed only at an explicit sequence boundary;
- the same physical event may be observed by multiple shots, but a shot cannot create a new physical event merely by observation.

Reference validation occurs before final compilation and after every dependency rebuild.
