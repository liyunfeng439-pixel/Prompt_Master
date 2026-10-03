#!/usr/bin/env python3
import json, importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text(encoding='utf-8')
def loadmod(name, rel):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def main():
    skill=read('SKILL.md'); canon=read('CANONICAL_RUNTIME_V10.18.0/RUNTIME_MASTER_CANONICAL_V10.18.0.yaml')
    harness=read('47_RUNTIME_EXECUTION_HARNESS_V3.1/runtime_harness_v1090.py')
    comp=read('48_NATIVE_PROMPT_COMPILER_V3.1/native_prompt_compiler_v1090.py')
    qa=read('49_DEEP_PROMPT_SEMANTIC_QA_V3.1/deep_prompt_semantic_qa_v1090.py')
    mod=loadmod('ultimate','25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py')
    checks={
      'VERSION_10_18_5':'version: "10.18.5"' in skill and 'version: 10.18.5' in canon,
      'EXPLICIT_SWITCH':mod.TRIGGER_PHRASE=='专属大招' and 'signature_ultimate_switch' in canon,
      'NO_TRIGGER_NO_OP':'if not trigger.get(\'enabled\')' in read('25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py'),
      '12_WEAPON_PROFILES':len(mod.PROFILES)>=12,
      'NO_NEW_EVENT': 'no_new_event' in read('25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py') and 'no_new_event' in harness,
      'SHOT_IR_SINGLE_SOURCE':'signature_ultimate' in harness and 'prompt_semantics' in harness,
      'COMPILER_CONSUMES_ULTIMATE':'signature_ultimate_core_sentence' in comp and 'semantic_override' in comp,
      'QA_ULTIMATE_SINGLE_SOURCE':'signature_ultimate_single_source' in qa,
      'MODEL_STRUCTURE_UNCHANGED': all(x in comp for x in ['universal','seedance_2_5','minimax_h3']),
      'BEAT_HARD_MAX':'len(beats)>7' in harness,
      'RESULT_LOCK_BARRIER':'result_lock' in canon and 'result_lock' in harness,
    }
    for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
    # direct profile semantics check
    bad=[]
    for weapon in mod.PROFILES:
        a={'action_id':'TEST','weapon':weapon,'prompt_semantics':{}}
        out,ult=mod.apply_signature_ultimate(a,'测试角色',weapon,{'enabled':True})
        if not ult or ult.get('weapon_category')!=weapon or not ult.get('core_sentence'): bad.append(weapon)
    print(('PASS' if not bad else 'FAIL'), 'PROFILE_APPLICATION', '' if not bad else ','.join(bad))
    raise SystemExit(0 if all(checks.values()) and not bad else 1)
if __name__=='__main__': main()
