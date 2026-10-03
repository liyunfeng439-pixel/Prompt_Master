#!/usr/bin/env python3
import argparse,json,re,sys,math
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def ngrams(s,n=3):
    s=re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',s)
    return {s[i:i+n] for i in range(max(0,len(s)-n+1))}

def run_quality(prompts, runtime):
    forbidden=['transition_contract','execution_contract','result_lock','INFERRED','FACT','NORMALIZED','knowledge_action_id','execution_model','opponent_response','state_contract','SHOT_IR','CANON','provenance','semantic_fingerprint']
    report={}; errors=[]
    for model,v in prompts.items():
        s=v.get('prompt',''); ss=[x.strip() for x in re.split(r'[。\n]',s) if x.strip()]
        hits=[x for x in forbidden if x in s]
        exact=sum(1 for i,x in enumerate(ss) for y in ss[i+1:] if x==y)
        dm=v.get('diversity_metrics',{})
        collisions=int(dm.get('semantic_bundle_collision_pairs',0))
        reuse=float(dm.get('component_reuse_ratio',1))
        repeated_trajectory = len(re.findall('外侧斜线',s))
        repeated_body = len(re.findall('后脚蹬地带动髋肩联动',s))
        # Low-level wording repetition is reported as telemetry after removing actor/outcome boilerplate;
        # it is not a hard failure when component-level diversity already passes.
        action_sentences=[x.get('sentence','') for x in v.get('semantic_trace',[]) if x.get('type')=='action' and x.get('sentence')]
        stop_phrases=['小白龙','云疏影','剑','枪','命中后','被格挡后','对手闪出攻击线','落空后','兵器短暂锁住','抢距离','利用接触控制']
        norm_actions=[]
        for x in action_sentences:
            for sp in stop_phrases: x=x.replace(sp,'')
            norm_actions.append(x)
        counts={}
        for x in norm_actions:
            for g in ngrams(x,4): counts[g]=counts.get(g,0)+1
        repeated_ngrams=sum(1 for n in counts.values() if n>=3)
        ending_ok=v.get('invariant_manifest',{}).get('ending')==runtime.get('ending')
        # meaningful diversity: at least 4 combat families across action trace, 4 outcome classes, and 4 distinct component bundles
        trace=[x for x in v.get('semantic_trace',[]) if x.get('type')=='action']
        fams={x.get('bundle',{}).get('family') for x in trace if x.get('bundle')}
        outs={x.get('bundle',{}).get('outcome') for x in trace if x.get('bundle')}
        bundles={tuple((k,str(val)) for k,val in x.get('bundle',{}).get('selected_components',[])) for x in trace}
        gates={
          'runtime_term_leak':not hits,
          'exact_duplicate_sentence':exact==0,
          'semantic_bundle_collision':collisions==0,
          'component_reuse_ratio':reuse<=0.22,
          'ending_preserved':ending_ok,
          'family_diversity':len(fams)>=4,
          'outcome_diversity':len(outs)>=4,
          'bundle_diversity':len(bundles)>=6,
          'deep_ngram_repetition':repeated_ngrams<=2,
          'trajectory_overuse':repeated_trajectory<=2,
          'body_phrase_overuse':repeated_body<=1,
        }
        bad=[k for k,b in gates.items() if not b]
        if bad: errors.append(f'{model}:DEEP_QA_FAIL:{bad}')
        report[model]={'runtime_term_leak':hits,'exact_duplicate_sentence_count':exact,'semantic_bundle_collision_pairs':collisions,'component_reuse_ratio':reuse,'repeated_deep_ngram_types_ge_3':repeated_ngrams,'distinct_families':len(fams),'distinct_outcomes':len(outs),'distinct_component_bundles':len(bundles),'trajectory_phrase_occurrences':repeated_trajectory,'body_phrase_occurrences':repeated_body,'gates':gates,'quality_gate':'PASS' if not bad else 'FAIL'}
    status='PASS' if not errors else 'FAIL'
    return {'status':status,'errors':errors,'models':report}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prompts',required=True);ap.add_argument('--runtime',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    prompts=load(args.prompts); runtime=load(args.runtime)
    report=run_quality(prompts,runtime)
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('DEEP_PROMPT_SEMANTIC_QA='+report['status'])
    sys.exit(0 if report['status']=='PASS' else 1)

if __name__=='__main__':main()
