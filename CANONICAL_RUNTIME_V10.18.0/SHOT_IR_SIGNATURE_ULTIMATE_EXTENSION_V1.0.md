# SHOT_IR Signature Ultimate Extension V1.0

`signature_ultimate` is an optional semantic extension carried by an existing SHOT_IR Shot and its `action_chain.prompt_semantics`.

Rules:
- Present only when the explicit user switch phrase `专属大招` was detected.
- Must reference one existing `action_result` Event.
- Must not create a new Event, Beat, Shot, actor, weapon, or result.
- `prompt_semantics.signature_ultimate_core_sentence` is the authoritative ultimate semantic sentence.
- Native adapters must preserve the technique name, weapon category, execution/trajectory semantics, contact, physics/environment result, VFX identity, camera intent, and result-lock behavior.
- The trigger phrase itself is not required in the final prompt; the compiled technique content is.
- After the ultimate result, RESULT_LOCK prevents additional combat events.
