# Regression Suite — 6.5

Regression is a release gate. Each failure routes to its owning causal layer; regression never invents a repair.

## Existing hard cases
1. single actor / no combat
2. one-on-one melee
3. dual-weapon exchange
4. unarmed exchange
5. ranged attack
6. 1v2 target switching
7. 2v2 simultaneous timing
8. boss + minions
9. multi-shot axis continuity
10. immediate structural destruction
11. persistent damage across cuts
12. ability activation/interruption/persistence
13. conflicting reference images
14. missing/unknown weapon properties
15. long sequence state inheritance
16. target-model constraint compilation
17. camera-only repair cannot clear physics FAIL
18. explicit user ending constraint survives repair

## New 6.4 gates
19. **knowledge retrieval provenance** — every selected knowledge action resolves to a DATA source reference and is treated as candidate evidence, not canon.
20. **candidate hard filtering** — unavailable weapon, impossible distance, invalid state prerequisite or insufficient resource removes a candidate before selection.
21. **tactical selection trace** — selected action has an observable trigger/tactical reason and a recorded selection reason.
22. **action repetition control** — repeated patterns are penalized unless tactically intentional or explicitly combo-locked.
23. **power relationship outcome** — a critical contact resolves to an explicit outcome taxonomy and resulting state.
24. **injury/resource persistence** — confirmed impairment/resource depletion affects subsequent action availability until recovery.
25. **spatial evolution** — destruction that changes topology is inherited by later movement and camera planning.
26. **critical shot coverage** — every critical physical event is observed or explicitly marked off-screen by design.
27. **shot complexity budget** — overloaded shots are split without deleting required causal events.
28. **duration budget** — phase/beat/shot durations remain within requested runtime tolerance.
29. **semantic IR traceability** — every MUST prompt unit traces to Combat IR or immutable canon.
30. **cinematic quality gate isolation** — cinematic WARN/REPAIR cannot override a correctness PASS/FAIL or create new facts.
31. **model capability feedback** — adapter-driven simplification preserves semantic event hash and ending constraints.
32. **ambiguity policy** — only HARD_UNKNOWN / USER_CONFIRM_REQUIRED blocks are escalated; safe defaults are explicitly marked.


## New 6.5 gates
33. **ending state completeness** — terminal/continuation state preserves survival, condition, weapon, ability, resource, spatial and environment state.
34. **event identity stability** — one physical event retains one EVENT_ID across multiple shot observations.
35. **action scoring trace** — selected action has structured internal feature trace, selection reason and provenance.
36. **retrieval 2.0 provenance** — retrieval records source priority, applicability and conflict status.
37. **QA ownership routing** — failures route to the declared lowest causal owner and trigger downstream rebuild.
38. **executable fixture gate** — all regression fixtures validate against their contract before release.
39. **semantic hash preservation** — model simplification does not mutate canonical event semantics.
40. **contract expansion** — ending/event/scoring/history/audio/duration/model capability contracts remain schema-valid and locally resolvable.


## New 6.5 Combat-First Pacing gates
41. **combat-first pacing** — when combat is primary and no slow-intro exception exists, first meaningful combat event meets the configured deadline, intro remains within budget, combat-time ratio meets the minimum, and static character presentation is suppressed/compressed.
42. **action-first character introduction** — character identification is merged into a meaningful combat beat when sufficient asset information already exists.
43. **slow-intro override** — an explicit user request for a slow/dramatic introduction disables the hard combat-first timing gate without mutating combat correctness rules.
44. **opening-template feasibility** — selected action-first opening template passes action candidate, spatial, temporal and physics gates.


## New 6.5.1 Final Combat Sequence gates
45. **final combat sequence completeness** — required final phases exist in causal order and a combat climax cannot terminate on an unexplained pose/cut.
46. **final impact provenance** — final impact chain resolves from a valid EVENT_ID/state transition and updates MASTER_COMBAT_STATE before Ending State.
47. **result lock immutability** — Ending Shot observes RESULT_LOCK and cannot mutate result, damage, weapon, resource, spatial or environment state without an explicit additional beat.
48. **final exchange budget** — terminal exchange/impact/observation fits the dedicated budget before decorative content is retained.


## New 6.5.2 Ending Shot System gates
49. **ending-shot template compatibility** — the selected template is compatible with finish type and the observable final event.
50. **ending-shot consequence grounding** — destruction, weapon break, knockback, ability residue and dust/debris templates require corresponding grounded state/event evidence.
51. **ending-shot result neutrality** — selector and Ending Shot Runtime cannot change RESULT_LOCK or create a post-lock physical event.
52. **ending-shot combat-first closure** — decisive combat endings retain a short result-observation beat and do not replace the climax with a generic character showcase.
53. **open/cliffhanger closure** — OPEN/CLIFFHANGER endings preserve unresolved conflict and continuation state without implying an unsupported winner.
