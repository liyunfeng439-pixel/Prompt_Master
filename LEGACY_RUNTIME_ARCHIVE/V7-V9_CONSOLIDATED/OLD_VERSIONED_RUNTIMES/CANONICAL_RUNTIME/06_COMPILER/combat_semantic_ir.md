# Combat Semantic IR — 6.4

Intermediate representation between runtime state and prompt text.

Each semantic event expresses:
WHO, DOES_WHAT, TO_WHOM, WHY, WHEN, WHERE, WITH_WHAT, CONTACT/OUTCOME, CONSEQUENCE, NEXT_STATE.

The IR is model-neutral and traceable to source events. It is the only allowed bridge from state/runtime semantics into Prompt IR.
