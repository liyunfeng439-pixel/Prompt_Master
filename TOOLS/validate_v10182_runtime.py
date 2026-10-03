#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate_current_runtime():
    required=[
      'SKILL.md','CANONICAL_RUNTIME_V10.18.0/RUNTIME_MASTER_CANONICAL_V10.18.0.yaml',
      'CANONICAL_RUNTIME_V10.18.0/SHOT_IR_CONTRACT_V10.18.0.md',
      '28_ADAPTIVE_COMBAT_NARRATIVE_RUNTIME_V1.0/NARRATIVE_RUNTIME.yaml',
      '28_ADAPTIVE_COMBAT_NARRATIVE_RUNTIME_V1.0/adaptive_narrative_runtime.py',
      '27_CINEMATIC_COMBAT_DIRECTOR_INTELLIGENCE_LAYER_V1.0/CINEMATIC_DIRECTOR_RUNTIME.yaml',
      '26_PHYSICS_IMPACT_INTELLIGENCE_LAYER_V1.0/PHYSICS_IMPACT_RUNTIME.yaml',
      '47_RUNTIME_EXECUTION_HARNESS_V3.1/runtime_harness_v1090.py',
      '48_NATIVE_PROMPT_COMPILER_V3.1/native_prompt_compiler_v1090.py',
      '49_DEEP_PROMPT_SEMANTIC_QA_V3.1/deep_prompt_semantic_qa_v1090.py',
      'NATIVE_OUTPUT_ROUTER_V10.9.0/router.yaml',
      'NATIVE_OUTPUT_ROUTER_V10.9.0/universal_adapter.md',
      'NATIVE_OUTPUT_ROUTER_V10.9.0/seedance_2.5_native_adapter.md',
      'NATIVE_OUTPUT_ROUTER_V10.9.0/minimax_h3_native_adapter.md',
      'DATA/COMBAT_KNOWLEDGE/SEMANTIC_COMPONENT_INDEX_V10.9.0.json',
      '25_WEAPON_INTELLIGENCE_LAYER_2.1_WEAPON_CONTROL_MORPH_RUNTIME/WEAPON_CONTROL_RUNTIME.yaml',
      '25_WEAPON_INTELLIGENCE_LAYER_2.2_WEAPON_COMBAT_BEHAVIOR_GRAPH/WEAPON_BEHAVIOR_GRAPH.yaml',
      '25_WEAPON_INTELLIGENCE_LAYER_2.0/weapon_registry.yaml',
      'TOOLS/validate_universal_weapon_control_v1018.py'
    ]
    if any(not (ROOT/p).exists() for p in required): return False
    skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    canon=(ROOT/'CANONICAL_RUNTIME_V10.18.0/RUNTIME_MASTER_CANONICAL_V10.18.0.yaml').read_text(encoding='utf-8')
    comp=(ROOT/'48_NATIVE_PROMPT_COMPILER_V3.1/native_prompt_compiler_v1090.py').read_text(encoding='utf-8')
    narrative=(ROOT/'28_ADAPTIVE_COMBAT_NARRATIVE_RUNTIME_V1.0/NARRATIVE_RUNTIME.yaml').read_text(encoding='utf-8')
    weapon=(ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.1_WEAPON_CONTROL_MORPH_RUNTIME/WEAPON_CONTROL_RUNTIME.yaml').read_text(encoding='utf-8')
    weapon_graph=(ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.2_WEAPON_COMBAT_BEHAVIOR_GRAPH/WEAPON_BEHAVIOR_GRAPH.yaml').read_text(encoding='utf-8')
    checks=[
      'version: "10.18.5"' in skill,
      'version: 10.18.5' in canon,
      'adaptive_combat_narrative' in canon,
      'narrative_reason_integrity' in canon,
      'result_lock_barrier' in canon,
      'version: "10.18.0"' in narrative,
      'narrative_sentence' in comp,
      'semantic_override=None' in comp,
      'SHOT_IR.prompt_semantics' in comp,
      'weapon_variant_single_source' in (ROOT/'49_DEEP_PROMPT_SEMANTIC_QA_V3.1/deep_prompt_semantic_qa_v1090.py').read_text(encoding='utf-8'),
      'narrative_curve_summary' in comp,
      not any(x in comp for x in ['xiao_bailong','yun_shuying','龙鳞剑','凌云长枪']),
      'defeated_actor' in comp and "mode=='draw'" in comp,
      'applies_to: all_canonical_weapons' in weapon,
      'universal_remote_flow:' in weapon_graph,
      'remote_control_category_gate: false' in weapon_graph,
      (ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py').exists(),
      'weapon_tactical_intelligence' in canon,
      'weapon_signature_ultimate_switch' in canon,
      'signature_ultimate_explicit_switch' in canon,
      (ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py').exists(),
      'signature_ultimate_single_source' in (ROOT/'49_DEEP_PROMPT_SEMANTIC_QA_V3.1/deep_prompt_semantic_qa_v1090.py').read_text(encoding='utf-8'),
      'autonomous_threshold: 68' in (ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/WEAPON_TACTICAL_RUNTIME.yaml').read_text(encoding='utf-8'),
    ]
    return all(checks)
def main():
    ok=validate_current_runtime(); rep={'version':'10.18.5','mode':'FAST_CURRENT_RUNTIME_PREFLIGHT','status':'PASS' if ok else 'FAIL'}
    (ROOT/'TOOLS/V10.18.5_FAST_PREFLIGHT_REPORT.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    print('V10.18.5_FAST_PREFLIGHT='+rep['status'])
    raise SystemExit(0 if ok else 1)
if __name__=='__main__': main()
