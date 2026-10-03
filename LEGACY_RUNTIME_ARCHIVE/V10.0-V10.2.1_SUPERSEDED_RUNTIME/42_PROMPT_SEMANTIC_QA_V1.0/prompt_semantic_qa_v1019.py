#!/usr/bin/env python3
import argparse,json,re,sys

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--prompts',required=True); ap.add_argument('--runtime',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    p=json.load(open(a.prompts,encoding='utf-8')); r=json.load(open(a.runtime,encoding='utf-8'))
    forbidden=['transition_contract','execution_contract','result_lock','INFERRED','FACT','NORMALIZED','knowledge_action_id','execution_model','opponent_response','state_contract','SHOT_IR','CANON','provenance','semantic_fingerprint']
    generic=['保持动作连续','重新建立可执行支撑状态','避免中途轨迹漂移','真实运动模糊','保持同一角色与武器身份','脚—髋—脊柱—肩—肘/腕依次传递','地面→脚踝→膝→髋→躯干→肩→肘→末端']
    errs=[]; report={}
    for model,v in p.items():
        s=v.get('prompt',''); hits=[x for x in forbidden if x in s]; ss=[x.strip() for x in re.split(r'[。\n]',s) if x.strip()]
        exact=sum(1 for i,x in enumerate(ss) for y in ss[i+1:] if x==y)
        repeated=[g for g in generic if s.count(g)>1]
        ending_ok=v.get('invariant_manifest',{}).get('ending')==r.get('ending')
        if hits: errs.append(f'{model}:RUNTIME_TERM_LEAK:{hits}')
        if exact: errs.append(f'{model}:EXACT_DUPLICATE_SENTENCE:{exact}')
        if len(repeated)>1: errs.append(f'{model}:GENERIC_REPETITION:{repeated}')
        if not ending_ok: errs.append(f'{model}:ENDING_DRIFT')
        report[model]={'runtime_term_leak':hits,'exact_duplicate_sentence_count':exact,'repeated_generic_phrases':repeated,'prompt_chars':len(s),'ending_preserved':ending_ok,'quality_gate':'PASS' if not (hits or exact or len(repeated)>1 or not ending_ok) else 'FAIL'}
    status='PASS' if not errs else 'FAIL'
    json.dump({'status':status,'errors':errs,'models':report},open(a.out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print('PROMPT_SEMANTIC_QA='+status)
    sys.exit(1 if errs else 0)
if __name__=='__main__':main()
