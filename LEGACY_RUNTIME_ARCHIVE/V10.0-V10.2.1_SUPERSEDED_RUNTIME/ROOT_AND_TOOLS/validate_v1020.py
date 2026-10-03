#!/usr/bin/env python3
import json,sys,argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out');a=ap.parse_args();errs=[];checks={}
    actions=load(ROOT/'DATA/COMBAT_KNOWLEDGE/actions_10000.json'); graphs=load(ROOT/'29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json'); abilities=load(ROOT/'35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_MANIFESTATION_PROFILES_32.json'); idx=load(ROOT/'DATA/COMBAT_KNOWLEDGE/SEMANTIC_COMPONENT_INDEX_V10.2.0.json')
    checks['actions_count']=len(actions)==10000; checks['graph_count']=len(graphs)==18000; checks['ability_count']=len(abilities)==32; checks['index_count']=idx.get('action_count')==10000
    ids=[x.get('action_id') for x in actions]; checks['unique_action_ids']=len(set(ids))==10000
    wi=0;oi=0;state=0
    for x in actions:
        em=x.get('execution_model',{}); wc=em.get('weapon_control',{}); wb=x.get('weapon_binding',{}); ps=x.get('prompt_semantics',{}); tc=x.get('transition_contract',{});opp=x.get('opponent_response',{}); pn=x.get('preconditions_normalized',{}); sc=x.get('state_contract',{}).get('pre_state',{})
        if not (wc.get('weapon')==x.get('weapon')==wb.get('canonical_weapon')==wb.get('execution_weapon')==ps.get('weapon_identity')==tc.get('requires',{}).get('weapon_identity')==tc.get('result',{}).get('weapon_identity')): wi+=1
        if not (opp.get('outcome_class')==tc.get('result',{}).get('outcome')==tc.get('result',{}).get('outcome_class')): oi+=1
        if not (pn.get('distance_id')==em.get('distance',{}).get('id') and pn.get('stance_id')==em.get('stance',{}).get('id') and sc.get('distance_id')==em.get('distance',{}).get('id')): state+=1
    checks['weapon_integrity']=wi==0; checks['outcome_integrity']=oi==0; checks['normalized_state_integrity']=state==0
    freq=idx.get('component_frequencies',{}); checks['component_index_dimensions']=all(len(freq.get(k,{}))>0 for k in ['footwork_id','joint_id','com_id','trajectory','contact_id','reaction_id','recovery','outcome','tactical','weapon','family_name'])
    checks['current_runtime_files']=all((ROOT/p).exists() for p in ['CANONICAL_RUNTIME_V10.2.0/RUNTIME_MASTER_CANONICAL_V10.2.0.yaml','NATIVE_OUTPUT_ROUTER_V10.2.0/router.yaml','44_DEEP_PROMPT_SEMANTIC_QA_V2.0/deep_prompt_semantic_qa_v1020.py','45_NATIVE_PROMPT_COMPILER_V2.0/native_prompt_compiler_v1020.py','46_RUNTIME_EXECUTION_HARNESS_V2.0/runtime_harness_v1020.py'])
    errs=[k for k,v in checks.items() if not v]
    report={'version':'10.2.0','status':'FAIL' if errs else 'PASS','checks':checks,'errors':errs,'counts':{'actions':len(actions),'graphs':len(graphs),'abilities':len(abilities),'semantic_index_actions':idx.get('action_count')}}
    out=ROOT/'TOOLS/V10.2.0_CONTRACT_VALIDATION_REPORT.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.out: Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'V10.2.0_CONTRACT_INTEGRITY={report["status"]}')
    sys.exit(1 if errs else 0)
if __name__=='__main__': main()
