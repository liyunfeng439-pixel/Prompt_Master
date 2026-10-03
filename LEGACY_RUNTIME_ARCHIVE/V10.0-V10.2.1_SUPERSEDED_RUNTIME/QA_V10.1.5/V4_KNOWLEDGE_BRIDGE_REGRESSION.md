# V4 Knowledge Bridge Regression Suite

Run these checks on every build.

1. **Source integrity** — all V4 source files exist and contain expected counts: 10,000 actions, 1,000 combo entries, 18,000 action graph nodes, 500 bindings.
2. **Resolver integrity** — every selected action can produce an ACTION_EXECUTION_CONTRACT.
3. **State binding** — distance/stance/weapon/terrain mismatches reject candidates.
4. **Causal phases** — setup/load/acceleration/contact/result/recovery remain ordered.
5. **Reaction binding** — opponent_response produces target state used by next decision.
6. **Counter gating** — counter is conditional, never automatic.
7. **Recovery gating** — miss/block/dodge/bind cannot silently disappear when recovery is required.
8. **Transition contract** — next action satisfies pre/post state requirements.
9. **Camera causality** — camera follows the action phases and cannot hide illegal transitions.
10. **VFX causality** — VFX occurs only after its triggering physical event.
11. **Environment persistence** — damage/debris/marks persist across subsequent shots.
12. **Traceability** — knowledge_action_id → execution_contract_id → event_id → beat_id → shot_id remains intact.
13. **SHOT_IR** — final action_chain is generated from resolved contracts, not raw knowledge text.
14. **Adapter invariants** — Universal / Seedance 2.5 / MiniMax H3 preserve physical facts and event order.
15. **No legacy override** — no V10.1.4 legacy file can become current authority.
