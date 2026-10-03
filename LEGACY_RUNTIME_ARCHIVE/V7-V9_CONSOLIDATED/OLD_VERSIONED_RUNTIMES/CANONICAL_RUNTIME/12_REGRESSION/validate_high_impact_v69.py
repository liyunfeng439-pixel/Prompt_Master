#!/usr/bin/env python3
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
FIX = ROOT/'CANONICAL_RUNTIME/12_REGRESSION/fixtures'
errors=[]
for p in FIX.glob('high_impact_execution_v69*.json'):
    d=json.loads(p.read_text(encoding='utf-8'))
    exp=d['expected']
    for b in d['input']['beats']:
        readability = b['readability_score'] >= 70 and all(b['signals'].get(k,False) for k in ('clear_intent','clear_attack_line','clear_contact_or_avoidance'))
        budget = b['change_count'] <= (5 if b['id'] in ('B6','B8') else 4)
        auto_split = b['change_count'] > 5
        if 'readability_gate_pass' in exp and readability != exp['readability_gate_pass']: errors.append(f'{p.name}:{b["id"]}:readability')
        if 'complexity_budget_pass' in exp and budget != exp['complexity_budget_pass']: errors.append(f'{p.name}:{b["id"]}:budget')
        if 'auto_split_required' in exp and auto_split != exp['auto_split_required']: errors.append(f'{p.name}:{b["id"]}:autosplit')
        if exp.get('stylish_priority_blocked') and readability: errors.append(f'{p.name}:{b["id"]}:style_should_block')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('PASS: V6.9 readability gate, complexity budget and auto-split fixtures validated.')
