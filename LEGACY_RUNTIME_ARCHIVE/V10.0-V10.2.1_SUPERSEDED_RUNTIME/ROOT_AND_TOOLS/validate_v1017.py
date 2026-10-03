#!/usr/bin/env python3
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel):
 with open(ROOT/rel,encoding='utf8') as f:return json.load(f)
A=load('DATA/COMBAT_KNOWLEDGE/actions_10000.json'); G=load('29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json'); P=load('35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_MANIFESTATION_PROFILES_32.json')
errs=[]
for a in A:
 w=a.get('weapon'); wc=a.get('execution_model',{}).get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); tc=a.get('transition_contract',{}); opp=a.get('opponent_response',{}); em=a.get('execution_model',{}); sc=a.get('state_contract',{})
 if not (wc.get('weapon')==w==wc.get('weapon_identity')==wb.get('canonical_weapon')==wb.get('execution_weapon')==ps.get('weapon_identity')==tc.get('requires',{}).get('weapon_identity')==tc.get('result',{}).get('weapon_identity')): errs.append((a['action_id'],'weapon'))
 if not (opp.get('outcome_class')==tc.get('result',{}).get('outcome')==tc.get('result',{}).get('outcome_class')): errs.append((a['action_id'],'outcome'))
 if not (em.get('distance',{}).get('id')==tc.get('requires',{}).get('distance_id')): errs.append((a['action_id'],'distance'))
 if not (em.get('stance',{}).get('id')==tc.get('requires',{}).get('stance_id')): errs.append((a['action_id'],'stance'))
 if sc.get('pre_state',{}).get('distance_id') != em.get('distance',{}).get('id'): errs.append((a['action_id'],'state_contract'))
by={a['action_id']:a for a in A}
for g in G:
 a=by.get(g.get('action_id'))
 if not a or g.get('transition_contract') != a.get('transition_contract'): errs.append((g.get('graph_id'),'graph_transition_drift'))
# ability semantic uniqueness
sigs={hashlib.sha256(json.dumps({k:v for k,v in p.items() if k!='profile_id'},sort_keys=True,ensure_ascii=False).encode()).hexdigest() for p in P}
if len(P)!=32 or len(sigs)!=32: errs.append(('ABILITY_PROFILES','semantic_duplication'))
print(f'ACTIONS={len(A)} GRAPHS={len(G)} ABILITY_PROFILES={len(P)} UNIQUE_ABILITY_SIGNATURES={len(sigs)}')
print(f'ERRORS={len(errs)}')
if errs: print(errs[:20]); sys.exit(1)
print('V10.1.7_CONTRACT_INTEGRITY=PASS')
