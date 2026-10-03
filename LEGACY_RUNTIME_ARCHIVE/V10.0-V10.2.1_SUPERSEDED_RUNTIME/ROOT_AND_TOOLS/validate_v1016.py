#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel):
    with open(ROOT/rel,encoding='utf8') as f:return json.load(f)
A=load('DATA/COMBAT_KNOWLEDGE/actions_10000.json')
W=load('DATA/COMBAT_KNOWLEDGE/weapon_actions_1000.json')
M=load('DATA/MARTIAL_DATABASE/martial_unified_2000_full.json')
G=load('29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json')
C=load('DATA/COMBAT_KNOWLEDGE/combo_tree_1000.json')
errors=[]
for a in A:
    w=a.get('weapon')
    wc=a.get('execution_model',{}).get('weapon_control',{})
    wb=a.get('weapon_binding',{})
    ps=a.get('prompt_semantics',{})
    tc=a.get('transition_contract',{})
    if wc.get('weapon')!=w or wc.get('weapon_identity')!=w: errors.append((a['action_id'],'weapon_control'))
    if wb.get('canonical_weapon')!=w or wb.get('execution_weapon')!=w or ps.get('weapon_identity')!=w: errors.append((a['action_id'],'binding/prompt'))
    if tc.get('requires',{}).get('weapon_identity')!=w or tc.get('result',{}).get('weapon_identity')!=w: errors.append((a['action_id'],'transition_contract'))
    if 'transition_contract' not in a: errors.append((a['action_id'],'missing_transition_contract'))
for x in W:
    if x.get('weapon')!=x.get('weapon_identity') or x.get('native_execution',{}).get('weapon')!=x.get('weapon'): errors.append((x.get('weapon_action_id'),'weapon_actions'))
for x in M:
    if x.get('weapon_identity')!=x.get('weapon'): errors.append((x.get('motion_id'),'martial'))
for x in G:
    if x.get('weapon_identity')!=x.get('weapon'): errors.append((x.get('graph_id'),'action_graph'))
print(f'ACTIONS={len(A)} WEAPON_ACTIONS={len(W)} MARTIAL={len(M)} GRAPH={len(G)} COMBO={len(C)}')
print(f'ERRORS={len(errors)}')
if errors:
    print(errors[:20]);sys.exit(1)
print('WEAPON_EXECUTION_INTEGRITY=PASS')
print('ABILITY_CONTRACT_PATH=PASS' if (ROOT/'35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_EXECUTION_CONTRACT.md').exists() else 'ABILITY_CONTRACT_PATH=FAIL')
