#!/usr/bin/env python3
import json, importlib.util, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
mod=ROOT/"25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py"
spec=importlib.util.spec_from_file_location("awc",mod); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
checks=[]
def ck(name,ok): checks.append((name,bool(ok)))
a={"action_id":"SEM-QA","core_id":"QA","weapon":"剑","execution_model":{"weapon_control":{"grip":"hand held"},"joint_chain":{"id":"x","path":"hand→weapon"},"center_of_mass":{"path_id":"x","description":"body drives weapon"},"contact_geometry":{"id":"blade","name":"点接触"}},"execution":{"startup":"hand drives weapon","body_kinematics":"arm drives weapon","trajectory":"line","contact_point":"blade","recovery_path":"return","tempo":"normal"},"physics":{"force_source":"hand","weight_transfer":"body","momentum":"mass","collision":"contact","failure_physics":"decelerate"},"prompt_semantics":{"core_sentence":"原手持动作核心：手臂驱动剑完成攻击"},"transition_contract":{"result":{}},"weapon_binding":{"canonical_weapon":"剑"},"opponent_response":{"outcome_class":"hit"}}
d=m.evaluate_weapon_control("剑",{"distance":"far","defense_state":"front"},[{"outcome":"block"}],a,{"control_mode":"TELEKINETIC","control_source":"qi","pattern":"tracking"},False)
v=m.build_execution_variant(a,d); ps=v.get("prompt_semantics",{})
ck("FINAL_VARIANT_REMOTE",v.get("execution_variant",{}).get("mode")=="TELEKINETIC")
ck("CORE_IS_REMOTE", "TELEKINETIC御器" in ps.get("core_sentence",""))
ck("HANDHELD_CORE_NOT_ACTIVE", "手臂驱动剑完成攻击" not in ps.get("core_sentence",""))
ck("NATIVE_CORE_PROVENANCE", ps.get("native_core_sentence")=="原手持动作核心：手臂驱动剑完成攻击")
ck("VARIANT_LOCK", ps.get("variant_semantic_lock") is True)
ck("CAUSAL_CHAIN_REMOTE", "independent_weapon_motion" in ps.get("causal_chain",""))
ck("NO_NEW_EVENT", v.get("weapon_control_runtime",{}).get("no_new_event") is True)
canon=(ROOT/"CANONICAL_RUNTIME_V10.18.0/RUNTIME_MASTER_CANONICAL_V10.18.0.yaml").read_text(encoding="utf-8")
ck("CANONICAL_VERSION", "version: 10.18.3" in canon)
ck("CANONICAL_VARIANT_AFTER_LOOKAHEAD", canon.index("action_transition_lookahead") < canon.index("weapon_execution_variant_intelligence"))
print("V10.18.3_SEMANTIC_VARIANT_CHECKS=%d"%len(checks))
for n,o in checks: print(("PASS " if o else "FAIL ")+n)
failed=sum(not o for _,o in checks)
print("WEAPON_SEMANTIC_VARIANT_V10.18.3="+("PASS" if failed==0 else "FAIL"))
sys.exit(1 if failed else 0)
