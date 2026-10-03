# V10.1.8 Runtime Stress Test Report

Scenario: 小白龙 vs 云疏影, 30s, armed sword vs spear, final 法相 duel, 云疏影 escapes after defeat, 小白龙 does not pursue.

Static validation: ACTIONS=10000, GRAPHS=18000, ABILITY_PROFILES=32, UNIQUE_DEEP_ABILITY_SIGNATURES=32, V10.1.8_CONTRACT_INTEGRITY=PASS.

Executable Harness: ACTION_CONTRACTS=10, ABILITY_CONTRACTS=2, EVENTS=27, FINAL_SHOTS=7, RUNTIME_STRESS_TEST=PASS.

Gates: weapon_integrity=True; outcome_contract=True; normalized_state=True; ability_execution=True; result_lock=True; beat_ids=True; shot_budget=True; native_compiler=True; adapter_semantic_consistency=True.

Native outputs: universal, seedance_2_5, minimax_h3; shared semantic fingerprint=efaa7df269dca6ae.

Final status: PASS
