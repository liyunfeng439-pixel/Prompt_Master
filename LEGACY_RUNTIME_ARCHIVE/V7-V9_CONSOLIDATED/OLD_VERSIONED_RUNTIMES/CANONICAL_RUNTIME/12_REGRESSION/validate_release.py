#!/usr/bin/env python3
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
errors=[]
json_files=list(ROOT.rglob('*.json'))
for p in json_files:
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'JSON_PARSE {p.relative_to(ROOT)}: {e}')
# local schema refs by filename
for p in json_files:
    try: d=json.loads(p.read_text(encoding='utf-8'))
    except Exception: continue
    def walk(x):
        if isinstance(x,dict):
            ref=x.get('$ref')
            if isinstance(ref,str) and not ref.startswith(('#','http://','https://')):
                target=(p.parent/ref).resolve()
                if not target.exists(): errors.append(f'REF_MISSING {p.relative_to(ROOT)} -> {ref}')
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(d)
fixtures=ROOT/'CANONICAL_RUNTIME/12_REGRESSION/fixtures'
ids=[]
for p in fixtures.glob('*.json'):
    d=json.loads(p.read_text(encoding='utf-8')); ids.append(d['id'])
    if not d.get('expected'): errors.append(f'FIXTURE_EXPECTED_EMPTY {p.name}')
if len(ids)!=len(set(ids)): errors.append('FIXTURE_DUPLICATE_ID')
pipeline=json.loads((ROOT/'CANONICAL_RUNTIME/pipeline_v6.5.json').read_text())
required={'ending_state_runtime','event_identity_runtime','action_scoring_runtime','retrieval_runtime_v2','qa_ownership_graph','model_capability_feedback','final_combat_sequence_runtime','final_exchange_budget','ending_shot_runtime','ending_shot_selector','high_impact_combat_runtime','stylish_action_priority','high_impact_rhythm_controller','stylish_action_qa','action_readability_gate','beat_complexity_budget','beat_auto_split','high_impact_execution_controller'}
missing=required-set(pipeline['pipeline'])
if missing: errors.append('PIPELINE_MISSING '+','.join(sorted(missing)))
if errors:
    print('\n'.join(errors)); sys.exit(1)
import subprocess
check=subprocess.run([sys.executable, str(ROOT/'CANONICAL_RUNTIME/12_REGRESSION/validate_high_impact_v69.py')], capture_output=True, text=True)
if check.returncode:
    errors.append('V69_EXECUTABLE_FIXTURES '+check.stdout.strip())
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(json_files)} JSON files parse; {len(ids)} executable fixtures; 6.9.0 pipeline required nodes present; local refs resolved; V6.9 execution fixtures pass.')
