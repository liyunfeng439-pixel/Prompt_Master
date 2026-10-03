#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('u',ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py'); u=importlib.util.module_from_spec(spec); spec.loader.exec_module(u)

def check(label, cond):
    print(('PASS' if cond else 'FAIL'), label); return cond

results=[]
results.append(check('POSITIVE_TRIGGER',u.detect_switch({'user_prompt':'甲使用剑，要求专属大招'})['enabled']))
for text in ['不要专属大招','不需要专属大招','关闭专属大招','取消专属大招','禁止专属大招']:
    results.append(check('NEGATIVE_'+text,u.detect_switch({'user_prompt':text})['enabled'] is False))
results.append(check('OTHER_BIG_MOVE_WORDS_OFF',u.detect_switch({'user_prompt':'高燃大招绝技'})['enabled'] is False))
actors={'A':{'id':'A','name':'甲','weapon':'剑'},'B':{'id':'B','name':'乙','weapon':'枪'}}
a_hit={'action_id':'HIT','weapon':'剑','opponent_response':{'outcome_class':'hit'}}
a_bind={'action_id':'BIND','weapon':'剑','opponent_response':{'outcome_class':'bind'}}
events=[{'event_id':'E1','type':'action_result','actor_id':'A','action_id':'HIT','outcome':'hit','highlight':True,'impact_profile':{'score':90}},{'event_id':'E2','type':'action_result','actor_id':'A','action_id':'BIND','outcome':'bind','highlight':False,'impact_profile':{'score':30}}]
sel,act,diag=u.select_signature_ultimate_event(events,{'HIT':a_hit,'BIND':a_bind},actors,requested_actor='A')
results.append(check('COMPATIBLE_HIT_SELECTED_OVER_BIND',sel and sel['event_id']=='E1'))
events_bad=[{'event_id':'E1','type':'action_result','actor_id':'A','action_id':'BIND','outcome':'bind','highlight':False,'impact_profile':{'score':10}}]
sel,act,diag=u.select_signature_ultimate_event(events_bad,{'BIND':a_bind},actors,requested_actor='A')
results.append(check('INCOMPATIBLE_SWORD_BIND_REJECTED',sel is None))
results.append(check('CONTINUE_COMBAT_SEMANTICS',u.apply_signature_ultimate(a_hit,'甲','剑',{'enabled':True})[1].get('continues_combat') is True))
raise SystemExit(0 if all(results) else 1)
