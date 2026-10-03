#!/usr/bin/env python3
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel,name):
 s=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
awc=load("25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py","awc")
checks=[]
def ck(n,x): checks.append((n,bool(x)))
a={"action_id":"V104-QA","core_id":"QA","weapon":"剑","execution_model":{"weapon_control":{},"joint_chain":{},"center_of_mass":{},"contact_geometry":{}},"execution":{},"physics":{},"prompt_semantics":{"core_sentence":"原手持语义"},"transition_contract":{"result":{}},"weapon_binding":{"canonical_weapon":"剑"},"opponent_response":{"outcome_class":"hit"}}
d=awc.evaluate_weapon_control("剑",{"distance":"far","defense_state":"front"},[{"outcome":"block"}],a,{"control_mode":"TELEKINETIC","control_source":"qi","pattern":"tracking"},False)
v=awc.build_execution_variant(a,d); ps=v["prompt_semantics"]
ck("REMOTE_VARIANT",v["execution_variant"]["mode"]=="TELEKINETIC")
ck("VARIANT_LOCK",ps.get("variant_semantic_lock") is True)
ck("CORE_AUTHORITATIVE",ps.get("core_sentence") and "TELEKINETIC御器" in ps["core_sentence"])
ck("NATIVE_PROVENANCE",ps.get("native_core_sentence")=="原手持语义")
canon=(ROOT/"CANONICAL_RUNTIME_V10.18.0/RUNTIME_MASTER_CANONICAL_V10.18.0.yaml").read_text(encoding="utf-8")
comp=(ROOT/"48_NATIVE_PROMPT_COMPILER_V3.1/native_prompt_compiler_v1090.py").read_text(encoding="utf-8")
qa=(ROOT/"49_DEEP_PROMPT_SEMANTIC_QA_V3.1/deep_prompt_semantic_qa_v1090.py").read_text(encoding="utf-8")
h=(ROOT/"47_RUNTIME_EXECUTION_HARNESS_V3.1/runtime_harness_v1090.py").read_text(encoding="utf-8")
ck("CANONICAL_10_18_4","version: 10.18.4" in canon)
ck("SHOT_IR_CARRIES_PROMPT_SEMANTICS", "prompt_semantics" in h)
ck("COMPILER_CONSUMES_SHOT_IR_OVERRIDE","semantic_override=semantic_override" in comp)
ck("NO_REMOTE_RECONSTRUCTION","Do not append a second reconstructed" in (ROOT/"43_COMBAT_SEMANTIC_DIVERSITY_ENGINE_V1.0/semantic_diversity_engine_v1030.py").read_text(encoding="utf-8"))
ck("QA_END_TO_END_GATE","weapon_variant_single_source" in qa)
print("V10.18.4_SINGLE_SOURCE_CHECKS=%d"%len(checks))
for n,x in checks: print(("PASS " if x else "FAIL ")+n)
sys.exit(0 if all(x for _,x in checks) else 1)
