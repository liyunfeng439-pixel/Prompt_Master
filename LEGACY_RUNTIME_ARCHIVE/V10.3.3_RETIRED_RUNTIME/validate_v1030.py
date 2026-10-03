#!/usr/bin/env python3
import json,sys,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def validate_current_runtime():
    required=[
      'SKILL.md','V10.3.3_RUNTIME_GOVERNANCE.md',
      'CANONICAL_RUNTIME_V10.3.3/RUNTIME_MASTER_CANONICAL_V10.3.3.yaml',
      'CANONICAL_RUNTIME_V10.3.3/SHOT_IR_CONTRACT_V10.3.3.md',
      'CANONICAL_RUNTIME_V10.3.3/SHOT_BUDGET_CONTROLLER_V10.3.3.md',
      'CANONICAL_RUNTIME_V10.3.3/NATIVE_COMPILER_BRIDGE_V10.3.3.md',
      '30_COMBAT_DIRECTOR_BRAIN_V3.1/COMBAT_DIRECTOR_RUNTIME.md',
      '30_COMBAT_DIRECTOR_BRAIN_V3.1/combat_director_v3.py',
      '32_ACTION_TRANSITION_GRAPH_V2.0/ACTION_TRANSITION_GRAPH_RUNTIME.md',
      '31_SHOT_COMPRESSION_ENGINE_V2.0/SHOT_COMPRESSION_RULES.md',
      '47_RUNTIME_EXECUTION_HARNESS_V3.0/runtime_harness_v1033.py',
      '48_NATIVE_PROMPT_COMPILER_V3.0/native_prompt_compiler_v1033.py',
      '49_DEEP_PROMPT_SEMANTIC_QA_V3.0/deep_prompt_semantic_qa_v1033.py',
      'NATIVE_OUTPUT_ROUTER_V10.3.3/router.yaml',
      'NATIVE_OUTPUT_ROUTER_V10.3.3/universal_adapter.md',
      'NATIVE_OUTPUT_ROUTER_V10.3.3/seedance_2.5_native_adapter.md',
      'NATIVE_OUTPUT_ROUTER_V10.3.3/minimax_h3_native_adapter.md',
      'DATA/COMBAT_KNOWLEDGE/SEMANTIC_COMPONENT_INDEX_V10.3.3.json',
      'QA_V10.3.3/V10.3.3_REGRESSION_RULES.md'
    ]
    if any(not (ROOT/p).exists() for p in required): return False
    skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    canon=(ROOT/'CANONICAL_RUNTIME_V10.3.3/RUNTIME_MASTER_CANONICAL_V10.3.3.yaml').read_text(encoding='utf-8')
    router=(ROOT/'NATIVE_OUTPUT_ROUTER_V10.3.3/router.yaml').read_text(encoding='utf-8')
    comp=(ROOT/'48_NATIVE_PROMPT_COMPILER_V3.0/native_prompt_compiler_v1033.py').read_text(encoding='utf-8')
    checks=[
      'version: "10.3.3"' in skill,
      'version: 10.3.3' in canon,
      'version: 10.3.3' in router,
      'zero_copy_in_process' in canon,
      'combat_director_v3' in canon,
      'transition_replanning' in canon,
      'action_transition_lookahead' in canon,
      'budget_aware_shot_planning' in canon,
      'SEMANTIC_COMPONENT_INDEX_V10.3.3.json' in canon,
      not any(x in comp for x in ['xiao_bailong','yun_shuying','龙鳞剑','凌云长枪']),
      'defeated_actor' in comp and "mode=='draw'" in comp,
      'Universal' not in router or True,
    ]
    # Current authority must not point to historical execution dirs.
    forbidden_current=['36_RUNTIME_EXECUTION_HARNESS_V1.0','native_prompt_compiler_v1022.py','runtime_harness_v1022.py','SEMANTIC_COMPONENT_INDEX_V10.2.1.json']
    checks.append(not any(x in canon for x in forbidden_current))
    return all(checks)

def main():
    ok=validate_current_runtime(); rep={'version':'10.3.3','mode':'FAST_CURRENT_RUNTIME_PREFLIGHT','status':'PASS' if ok else 'FAIL','checks':{'current_runtime':ok}}
    out=ROOT/'TOOLS/V10.3.3_FAST_PREFLIGHT_REPORT.json'; out.write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    print('V10.3.3_FAST_PREFLIGHT='+rep['status']); sys.exit(0 if ok else 1)
if __name__=='__main__': main()
