#!/usr/bin/env python3
import json, sys, importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
mod=ROOT/"25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py"
spec=importlib.util.spec_from_file_location("awc",mod); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
checks=[]
def ck(name, ok): checks.append((name,bool(ok)))
ck("VERSION_10_18_3", "10.18.3" in (ROOT/"SKILL.md").read_text(encoding="utf8"))
ck("TRACKING_DISTINCT", m.REMOTE_PATTERNS.get("tracking") != m.REMOTE_PATTERNS.get("orbit"))
a={"action_id":"QA-TEST","core_id":"QA","weapon":"剑","execution_model":{"weapon_control":{"grip":"hand held"},"joint_chain":{"id":"x","path":"hand→weapon"},"center_of_mass":{"path_id":"x"}},"execution":{"startup":"hand drives weapon","body_kinematics":"arm drives weapon","trajectory":"line","contact_point":"blade","recovery_path":"return","tempo":"normal"},"physics":{"force_source":"hand","weight_transfer":"body","momentum":"mass","collision":"contact","failure_physics":"decelerate"},"prompt_semantics":{},"transition_contract":{"result":{}},"weapon_binding":{"canonical_weapon":"剑"},"opponent_response":{"outcome_class":"hit"}}
d=m.evaluate_weapon_control("剑",{"distance":"far","defense_state":"front"},[{"outcome":"block"}],a,{"control_mode":"TELEKINETIC","pattern":"tracking"},False)
v=m.build_execution_variant(a,d)
wc=v["execution_model"]["weapon_control"]
ck("REMOTE_ACTIVATES", d.get("activate"))
ck("VARIANT_CREATED", v.get("execution_variant",{}).get("mode")=="TELEKINETIC")
ck("HAND_COUPLING_REMOVED", "脱手后取消手握约束" in wc.get("grip",""))
ck("MASS_INERTIA", wc.get("mass_inertia_preserved") is True)
ck("TRACKING_PRESERVED", v.get("execution_variant",{}).get("pattern")=="tracking")
ck("TACTICAL_COST", d.get("control_cost",0)>0 and "tactical_utility" in d)
ck("SEMANTIC_CORE_VARIANTIZED", v.get("prompt_semantics",{}).get("core_sentence","").find("TELEKINETIC御器") >= 0)
ck("NATIVE_CORE_PRESERVED_AS_PROVENANCE", (not a.get("prompt_semantics",{}).get("core_sentence")) or ("native_core_sentence" in v.get("prompt_semantics",{})))
ck("SEMANTIC_VARIANT_LOCK", v.get("prompt_semantics",{}).get("variant_semantic_lock") is True)
print("WEAPON_EXECUTION_VARIANT_CHECKS=%d"%len(checks))
for n,o in checks: print(("PASS " if o else "FAIL ")+n)
failed=sum(not o for _,o in checks)
print("WEAPON_EXECUTION_VARIANT_V10.18.3="+("PASS" if failed==0 else "FAIL"))
sys.exit(1 if failed else 0)
