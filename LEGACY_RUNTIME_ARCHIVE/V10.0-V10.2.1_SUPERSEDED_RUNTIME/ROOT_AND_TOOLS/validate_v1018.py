#!/usr/bin/env python3
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel):
 with open(ROOT/rel,encoding='utf8') as f:return json.load(f)
A=load('DATA/COMBAT_KNOWLEDGE/actions_10000.json'); G=load('29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json'); P=load('35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_MANIFESTATION_PROFILES_32.json')
errs=[]
for a in A:
 w=a.get('weapon'); wc=a.get('execution_model',{}).get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); tc=a.get('transition_contract',{}); opp=a.get('opponent_response',{}); em=a.get('execution_model',{}); sc=a.get('state_contract',{}); pn=a.get('preconditions_normalized',{}); rc=a.get('result_contract',{})
 if not (wc.get('weapon')==w==wc.get('weapon_identity')==wb.get('canonical_weapon')==wb.get('execution_weapon')==ps.get('weapon_identity')==tc.get('requires',{}).get('weapon_identity')==tc.get('result',{}).get('weapon_identity')): errs.append((a['action_id'],'weapon'))
 if not (opp.get('outcome_class')==tc.get('result',{}).get('outcome')==tc.get('result',{}).get('outcome_class')==rc.get('outcome_class')): errs.append((a['action_id'],'outcome'))
 if not (em.get('distance',{}).get('id')==tc.get('requires',{}).get('distance_id')==pn.get('distance_id')==sc.get('pre_state',{}).get('distance_id')): errs.append((a['action_id'],'distance'))
 if not (em.get('stance',{}).get('id')==tc.get('requires',{}).get('stance_id')==pn.get('stance_id')==sc.get('pre_state',{}).get('stance_id')): errs.append((a['action_id'],'stance'))
 if rc.get('weapon_identity')!=w or pn.get('weapon_identity')!=w: errs.append((a['action_id'],'normalized_weapon'))
by={a['action_id']:a for a in A}
for g in G:
 a=by.get(g.get('action_id'))
 if not a or g.get('transition_contract') != a.get('transition_contract'): errs.append((g.get('graph_id'),'graph_transition_drift'))
# ability deep signatures
sig=[]
for p in P:
 e=p.get('execution_contract_v2',{})
 required=['startup_vector','body_line','primary_interaction','counter_behavior','clash_resolution','break_condition','exit_transition']
 if not all(e.get(k) for k in required): errs.append((p['profile_id'],'ability_semantics_missing'))
 sig.append(hashlib.sha256(json.dumps({'archetype':p.get('archetype'), **{k:e.get(k) for k in required}},ensure_ascii=False,sort_keys=True).encode()).hexdigest())
if len(P)!=32 or len(set(sig))!=32: errs.append(('ABILITY_PROFILES','semantic_signature_duplication'))
# current authority file checks
checks=[ROOT/'SKILL.md',ROOT/'V10.1.9_RUNTIME_GOVERNANCE.md',ROOT/'CANONICAL_RUNTIME_V10.1.9/RUNTIME_MASTER_CANONICAL_V10.1.9.yaml',ROOT/'NATIVE_OUTPUT_ROUTER_V10.1.9/router.yaml',ROOT/'QA_V10.1.9/V10.1.9_REGRESSION_RULES.md',ROOT/'41_COMBAT_SEMANTIC_COMPILER_V2.0/combat_semantic_compiler_v1019.py']
for p in checks:
 if not p.exists(): errs.append(('AUTHORITY_MISSING',str(p.relative_to(ROOT))))
print(f'ACTIONS={len(A)} GRAPHS={len(G)} ABILITY_PROFILES={len(P)} UNIQUE_DEEP_ABILITY_SIGNATURES={len(set(sig))}')
print(f'ERRORS={len(errs)}')
if errs: print(errs[:40]); sys.exit(1)
print('V10.1.9_CONTRACT_INTEGRITY=PASS')
