#!/usr/bin/env python3
import argparse, json, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT/'TOOLS/V10.2.1_FAST_PREFLIGHT_REPORT.json'))
    ap.add_argument('--full', action='store_true', help='Also run the historical deep validator; not used by the runtime harness.')
    args=ap.parse_args()
    snap=json.loads((ROOT/'TOOLS/V10.2.1_CONTRACT_SNAPSHOT.json').read_text(encoding='utf-8'))
    checks={}; errors=[]
    for rel in snap['files']:
        p=ROOT/rel['path']; ok=p.exists()
        if not ok: errors.append('MISSING:'+rel['path']); checks[rel['path']]=False; continue
        got=sha256_file(p); ok=got==rel['sha256']; checks[rel['path']]=ok
        if not ok: errors.append('HASH_MISMATCH:'+rel['path'])
    required=[
      'CANONICAL_RUNTIME_V10.2.1/RUNTIME_MASTER_CANONICAL_V10.2.1.yaml',
      'CANONICAL_RUNTIME_V10.2.1/SHOT_IR_CONTRACT_V10.2.1.md',
      '47_RUNTIME_EXECUTION_HARNESS_V3.0/runtime_harness_v1021.py',
      '48_NATIVE_PROMPT_COMPILER_V3.0/native_prompt_compiler_v1021.py',
      '49_DEEP_PROMPT_SEMANTIC_QA_V3.0/deep_prompt_semantic_qa_v1021.py',
      'TOOLS/validate_v1021.py'
    ]
    checks['required_runtime_paths']=all((ROOT/p).exists() for p in required)
    if not checks['required_runtime_paths']: errors.append('REQUIRED_RUNTIME_PATH_FAIL')
    rep={'version':'10.2.1','mode':'FAST_STREAMING_PREFLIGHT','status':'FAIL' if errors else 'PASS','checks':checks,'errors':errors,'counts':snap['counts']}
    Path(args.out).write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    print('V10.2.1_FAST_PREFLIGHT='+rep['status'])
    if args.full:
        import subprocess
        p=subprocess.run([sys.executable,str(ROOT/'TOOLS/validate_v1020.py')],capture_output=True,text=True)
        print(p.stdout); print(p.stderr,end='')
        if p.returncode!=0: sys.exit(p.returncode)
    sys.exit(1 if errors else 0)
if __name__=='__main__': main()
