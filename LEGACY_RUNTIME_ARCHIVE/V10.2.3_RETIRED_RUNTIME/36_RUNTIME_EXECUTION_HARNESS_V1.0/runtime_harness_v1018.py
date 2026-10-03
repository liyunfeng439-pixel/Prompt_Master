#!/usr/bin/env python3
import argparse, json, hashlib, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    p=ROOT/rel if not Path(rel).is_absolute() else Path(rel)
    with open(p,encoding='utf-8') as f:return json.load(f)
load_json=load
def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:16]

FAMILY_MAP=[('进身突入','entry'),('试探','probe'),('破防','guard_break'),('直接打击','direct_strike'),('换角','angle_change'),('缠压','bind'),('卸转','redirect'),('反击','counter'),('追击','chase'),('退击','retreat_attack'),('空中','aerial'),('低位','low_attack'),('摔投','throw'),('擒拿','grapple'),('终结','finisher')]
def family(a):
    for frag,val in FAMILY_MAP:
        if frag in a.get('name',''): return val
    return 'unknown'
def allowed_families(graph,outcome):
    key={'hit':'natural_next','bind':'natural_next','block':'conditional_next','dodge':'conditional_next','miss':'reset_next'}.get(outcome)
    if not key:return set()
    return {x.split(':',1)[1] for x in graph.get(key,[]) if isinstance(x,str) and x.startswith('family:')}

def action_contract(actor,a,event_id):
    tc=a['transition_contract']; opp=a['opponent_response']; em=a['execution_model']
    return {'execution_contract_id':'EXEC-'+a['action_id'],'knowledge_action_id':a['action_id'],'knowledge_core_id':a['core_id'],
      'actor_identity':actor['id'],'weapon_identity':a['weapon'],'pre_state':a['state_contract']['pre_state'],
      'action_name':a.get('name',''), 'decision_trigger':a.get('decision_trigger',{}),
      'execution_native':a.get('execution',{}),
      'execution':{'joint_chain':em['joint_chain'],'center_of_mass':em['center_of_mass'],'weapon_control':em['weapon_control'],'contact_geometry':em['contact_geometry'],'temporal_phases':em.get('temporal_phases',[])},
      'result':{'outcome_class':opp['outcome_class'],'distance_after':tc['result'].get('distance_after'),'recovery_output_state':tc['result'].get('recovery_output_state'),'opponent_response':opp},
      'counter':a.get('counter_logic'),'recovery':a.get('failure_and_recovery'),'transition_contract':tc,
      'presentation':{'camera':a.get('cinematic'),'vfx':a.get('vfx'),'environment':a.get('environment')},'prompt':a.get('prompt_semantics'),
      'event_id':event_id,'source_trace':{'action_id':a['action_id'],'provenance_status':'knowledge_derived'}}

def compile_native(runtime_path,shot_path,out_path,quality_path):
    compiler=ROOT/'41_COMBAT_SEMANTIC_COMPILER_V2.0/combat_semantic_compiler_v1019.py'
    subprocess.run([sys.executable,str(compiler),'--runtime',str(runtime_path),'--shot-ir',str(shot_path),'--out',str(out_path),'--quality-out',str(quality_path)],check=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--scenario',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    scen=load(args.scenario); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    actions=load('DATA/COMBAT_KNOWLEDGE/actions_10000.json'); by_action={a['action_id']:a for a in actions}
    graphs=load('29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json'); by_graph={g['action_id']:g for g in graphs}
    profiles=load('35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_MANIFESTATION_PROFILES_32.json'); by_profile={p['profile_id']:p for p in profiles}
    errors=[]; warnings=[]; events=[]; contracts=[]; last_action_by_actor={}; prev_action_by_actor={}
    actors={a['id']:a for a in scen['actors']}
    canon={aid:{'name':a.get('name'),'weapon':a.get('weapon'),'archetype':a.get('archetype'),'provenance':a.get('provenance',{})} for aid,a in actors.items()}
    # provenance guard
    for aid,a in actors.items():
        for k,info in (a.get('provenance') or {}).items():
            if isinstance(info,dict) and info.get('status')=='INFERRED' and info.get('promoted_to_canon'):
                errors.append(f'INFERENCE_PROMOTED:{aid}:{k}')
    for i,item in enumerate(scen.get('action_sequence',[]),1):
        actor=actors.get(item['actor_id']); aid=item['action_id']; a=by_action.get(aid); eid=item.get('event_id',f'EVENT-{i:03d}')
        if not actor: errors.append(f'UNKNOWN_ACTOR:{item["actor_id"]}'); continue
        if not a: errors.append(f'UNKNOWN_ACTION:{aid}'); continue
        # full contract integrity
        if a.get('weapon') != actor.get('weapon'): errors.append(f'WEAPON_CANON_MISMATCH:{aid}')
        em=a.get('execution_model',{}); tc=a.get('transition_contract',{}); wc=em.get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); opp=a.get('opponent_response',{})
        if not (wc.get('weapon')==a['weapon']==wb.get('canonical_weapon')==wb.get('execution_weapon')==ps.get('weapon_identity')==tc.get('requires',{}).get('weapon_identity')==tc.get('result',{}).get('weapon_identity')): errors.append(f'WEAPON_INTEGRITY_FAIL:{aid}')
        if not (opp.get('outcome_class')==tc.get('result',{}).get('outcome')==tc.get('result',{}).get('outcome_class')): errors.append(f'OUTCOME_CONTRACT_MISMATCH:{aid}')
        pn=a.get('preconditions_normalized',{})
        if pn.get('distance_id')!=em.get('distance',{}).get('id') or pn.get('stance_id')!=em.get('stance',{}).get('id'): errors.append(f'NORMALIZED_STATE_FAIL:{aid}')
        if a.get('state_contract',{}).get('pre_state',{}).get('distance_id')!=em.get('distance',{}).get('id'): errors.append(f'STATE_DISTANCE_FAIL:{aid}')
        # same actor direct continuation
        if actor['id'] in last_action_by_actor and item.get('continue_from_previous'):
            prev=last_action_by_actor[actor['id']]; g=by_graph.get(prev['action_id'])
            if not g: errors.append(f'MISSING_GRAPH:{prev["action_id"]}')
            else:
                allowed=allowed_families(g,prev['outcome']); nf=family(a)
                if allowed and nf not in allowed and not item.get('transition_override'): errors.append(f'TRANSITION_FAMILY_FAIL:{prev["action_id"]}->{aid}:{nf}')
        c=action_contract(actor,a,eid); contracts.append(c)
        events.append({'event_id':eid,'type':'action_result','actor_id':actor['id'],'action_id':aid,'outcome':opp['outcome_class'],'shot_id':None})
        # explicit recovery emission for failure/defense outcomes
        if opp['outcome_class'] in ('block','dodge','miss','bind'):
            rid=f'RECOVERY-{i:03d}'
            rec=a.get('failure_and_recovery',{}).get('recovery',{})
            events.append({'event_id':rid,'type':'recovery','actor_id':actor['id'],'action_id':aid,'recovery_id':rec.get('id'),'output_state':a.get('failure_and_recovery',{}).get('recovery_output_state') or tc.get('result',{}).get('recovery_output_state')})
        last_action_by_actor[actor['id']]={'action_id':aid,'outcome':opp['outcome_class']}; prev_action_by_actor[actor['id']]=item
    # abilities with detailed execution stages
    ability_contracts=[]
    for j,item in enumerate(scen.get('abilities',[]),1):
        actor=actors.get(item['actor_id']); p=by_profile.get(item['profile_id'])
        if not actor or not p: errors.append(f'ABILITY_UNKNOWN:{item.get("profile_id")}'); continue
        if p.get('archetype')!=actor.get('archetype'): errors.append(f'ABILITY_ARCHETYPE_MISMATCH:{item["profile_id"]}')
        if item.get('activation_state')!='activated': errors.append(f'ABILITY_NOT_ACTIVATED:{item["profile_id"]}')
        if not item.get('result_lock'): errors.append(f'ABILITY_RESULT_LOCK_MISSING:{item["profile_id"]}')
        stages=[f'ABILITY-{j:02d}-ACTIVATION',f'ABILITY-{j:02d}-MANIFEST',f'ABILITY-{j:02d}-WEAPON-SYNC',f'ABILITY-{j:02d}-CLASH']
        ability_contracts.append({'ability_contract_id':f'ABILITY-CONTRACT-{j:03d}','ability_family':p['subfamily'],'actor_identity':actor['id'],'manifestation_profile_id':p['profile_id'],'visual_profile':p.get('visual_profile'),'execution_contract_v2':p.get('execution_contract_v2'),'authorization_source':item.get('authorization_source'),'activation_state':item.get('activation_state'),'result':item.get('result','resolved_clash'),'result_lock':True,'result_lock_event_id':'ABILITY-FINAL-RESULT-LOCK','joint_clash_event_id':'ABILITY-FINAL-CLASH','exit_state':item.get('exit_state','resolved'),'ability_event_ids':stages})
        events += [{'event_id':e,'type':'ability','actor_id':actor['id'],'ability_contract_id':f'ABILITY-CONTRACT-{j:03d}','shot_id':None} for e in stages]
    # A two-party final 法相 duel resolves one shared clash and one shared RESULT_LOCK.
    events.append({'event_id':'ABILITY-FINAL-CLASH','type':'ability_clash','actor_ids':[a['actor_id'] for a in scen.get('abilities',[])],'ability_contract_ids':[a['ability_contract_id'] for a in ability_contracts],'shot_id':None})
    events.append({'event_id':'ABILITY-FINAL-RESULT-LOCK','type':'result_lock','actor_ids':[a['actor_id'] for a in scen.get('abilities',[])],'ability_contract_ids':[a['ability_contract_id'] for a in ability_contracts],'shot_id':None})
    ending=scen['ending']
    if not (ending.get('result_lock') and ending.get('escape') and ending.get('no_chase')): errors.append('ENDING_GATE_FAIL')
    if ending.get('victor')==ending.get('defeated_actor'): errors.append('ENDING_ACTOR_COLLISION')
    events.append({'event_id':'ENDING-RESULT-LOCK','type':'ending','defeated_actor':ending['defeated_actor'],'victor':ending['victor'],'result_lock':True,'escape':True,'no_chase':True,'shot_id':None})
    # beat/shot generation: deterministic semantic phases
    dur=float(scen['duration_s']); target=7 if dur==30 else max(1,min(7,round(dur/4.3)))
    # phase buckets keep ending in final shot and abilities in final two shots
    indexed=list(range(len(events))); shots=[]
    boundaries=[0, max(1,round(len(events)*0.12)), max(2,round(len(events)*0.27)), max(3,round(len(events)*0.43)), max(4,round(len(events)*0.61)), max(5,round(len(events)*0.77)), max(6,round(len(events)*0.90)), len(events)]
    boundaries=sorted(set(min(len(events),max(0,x)) for x in boundaries))
    if len(boundaries)<8:
        boundaries=list(range(0,len(events)+1, max(1,len(events)//7)))+[len(events)]
        boundaries=sorted(set(boundaries))
    # force exactly target groups by distributing events, but keep ending in final
    groups=[[] for _ in range(target)]
    for idx,e in enumerate(events):
        # reserve final result lock + any ability events in last two groups
        if e['event_id']=='ENDING-RESULT-LOCK': gi=target-1
        elif e['type']=='result_lock': gi=target-2
        else: gi=min(target-3, int(idx*target/len(events))) if target>3 else min(target-1,idx)
        groups[gi].append(e['event_id'])
    # ensure no empty shot by fallback sequential rebalancing
    flat=[e for g in groups for e in g]
    if any(not g for g in groups):
        groups=[[] for _ in range(target)]
        for idx,eid in enumerate(flat): groups[min(target-1,int(idx*target/len(flat)))].append(eid)
    durations=[4.0,4.0,4.0,4.0,5.0,5.0,4.0] if target==7 and dur==30 else [round(dur/target,2)]*target
    for s,g in enumerate(groups,1):
        shots.append({'shot_id':f'S{s:02d}','beat_ids':[f'BEAT-{s:03d}'],'duration':durations[s-1],'event_ids':g,'story_function':['combat_open','counter_exchange','pressure_shift','high_intensity_exchange','escalation','final_build','final_clash_result'][s-1] if target==7 else 'combat_execution'})
    if len(shots)>7 and dur==30: errors.append('SHOT_BUDGET_FAIL')
    event_to_shot={}
    for sh in shots:
        if not sh['beat_ids'][0]: errors.append(f'EMPTY_BEAT_ID:{sh["shot_id"]}')
        for eid in sh['event_ids']:
            if eid in event_to_shot: errors.append(f'EVENT_DUPLICATED:{eid}')
            event_to_shot[eid]=sh['shot_id']
    for e in events:
        if e['event_id'] not in event_to_shot: errors.append(f'EVENT_UNASSIGNED:{e["event_id"]}')
    if 'ENDING-RESULT-LOCK' not in shots[-1]['event_ids']: errors.append('ENDING_NOT_IN_FINAL_SHOT')
    # RESULT_LOCK barrier
    result_locked=False
    for sh in shots:
        for eid in sh['event_ids']:
            e=next(x for x in events if x['event_id']==eid)
            if eid in ('ABILITY-FINAL-RESULT-LOCK','ENDING-RESULT-LOCK'): result_locked=True
            elif result_locked and e['type'] in ('action_result','ability_clash'): errors.append(f'POST_RESULT_LOCK_COMBAT_EVENT:{eid}')
    # SHOT_IR
    shot_ir=[]
    all_event_ids=[e['event_id'] for e in events]
    for sh in shots:
        acts=[c for c in contracts if c['event_id'] in sh['event_ids']]
        ability_ids=[a['ability_contract_id'] for a in ability_contracts if any(e in sh['event_ids'] for e in a['ability_event_ids'])]
        actor_state={aid:{'name':v['name'],'weapon':v['weapon'],'provenance_status':(v.get('provenance') or {}).get('weapon',{}).get('status','UNKNOWN')} for aid,v in canon.items()}
        shot_ir.append({'shot_id':sh['shot_id'],'duration':sh['duration'],'story_function':sh['story_function'],'beat_ids':sh['beat_ids'],'event_ids':sh['event_ids'],'actor_state':actor_state,
          'spatial_state':scen.get('spatial_state',{'status':'INFERRED','note':'not canonized'}),
          'action_chain':[{'knowledge_action_id':c['knowledge_action_id'],'execution_contract_id':c['execution_contract_id'],'event_id':c['event_id'],'actor':c['actor_identity'],'weapon':c['weapon_identity'],'result':c['result']['outcome_class'],'state_contract_hash':sha(c['pre_state'])} for c in acts],
          'ability_contract_ids':ability_ids,
          'camera':'cause-following; preserve setup→action→contact/avoidance→reaction→recovery and keep subject readable',
          'physics':'derived from execution contracts; result follows contact/avoidance and force transfer',
          'vfx':'bound after physical result; never source the event',
          'continuity':'inherit actor identity, weapon identity, canonical state IDs and inferred provenance',
          'damage_state':scen.get('damage_state',{}),
          'ending_state':events[[e['event_id'] for e in events].index('ENDING-RESULT-LOCK')] if 'ENDING-RESULT-LOCK' in sh['event_ids'] else {'result_lock':False}})
    shot_doc={'version':'10.1.9','shot_count':len(shot_ir),'all_event_ids':all_event_ids,'spatial_provenance':scen.get('spatial_state',{}),'shots':shot_ir}
    runtime={'schema_version':'1.1','runtime_version':'10.1.9','scenario_id':scen['scenario_id'],'canon':canon,'action_contracts':contracts,'ability_contracts':ability_contracts,'events':events,'ending':ending,'qa':{}}
    # adapter compilation
    runtime_path=out/'runtime_trace.json'; shot_path=out/'shot_ir.json'; native_path=out/'native_prompts_v1019.json'
    runtime_path.write_text(json.dumps(runtime,ensure_ascii=False,indent=2),encoding='utf-8'); shot_path.write_text(json.dumps(shot_doc,ensure_ascii=False,indent=2),encoding='utf-8')
    quality_path=out/'prompt_semantic_quality.json'
    compile_native(runtime_path,shot_path,native_path,quality_path)
    native=load_json(native_path)
    qa_path=out/'prompt_semantic_qa.json'
    qa_script=ROOT/'42_PROMPT_SEMANTIC_QA_V1.0/prompt_semantic_qa_v1019.py'
    qa_proc=subprocess.run([sys.executable,str(qa_script),'--prompts',str(native_path),'--runtime',str(runtime_path),'--out',str(qa_path)],capture_output=True,text=True)
    if qa_proc.returncode!=0: errors.append('PROMPT_SEMANTIC_QA_FAIL')
    expected=set(all_event_ids)
    adapter_results={}
    for model,p in native.items():
        if not p.get('prompt') or len(p['prompt'])<80: errors.append(f'NATIVE_PROMPT_EMPTY:{model}')
        if set(p.get('event_coverage',[]))!=expected: errors.append(f'ADAPTER_EVENT_COVERAGE_FAIL:{model}')
        if p.get('invariant_manifest',{}).get('ending')!=ending: errors.append(f'ADAPTER_ENDING_DRIFT:{model}')
        adapter_results[model]={'semantic_fingerprint':p.get('semantic_fingerprint'),'source':p.get('source'),'shot_count':p.get('shot_count'),'prompt_length':len(p.get('prompt',''))}
    fps={p.get('semantic_fingerprint') for p in native.values()}
    if len(fps)!=1: errors.append('ADAPTER_SEMANTIC_FINGERPRINT_DRIFT')
    runtime['qa']={'status':'FAIL' if errors else 'PASS','errors':errors,'warnings':warnings,'counts':{'actions_dataset':len(actions),'action_contracts':len(contracts),'ability_contracts':len(ability_contracts),'events':len(events),'shots':len(shots)},'invariants':{'weapon_integrity':not any('WEAPON_' in e for e in errors),'outcome_contract':not any('OUTCOME_' in e for e in errors),'normalized_state':not any('STATE_' in e or 'NORMALIZED_' in e for e in errors),'ability_execution':not any('ABILITY_' in e for e in errors),'result_lock':not any('ENDING_' in e or 'POST_RESULT_LOCK' in e for e in errors),'beat_ids':not any('EMPTY_BEAT_ID' in e for e in errors),'shot_budget':len(shots)<=7 if dur==30 else True,'native_compiler':not any('NATIVE_PROMPT_EMPTY' in e for e in errors),'adapter_semantic_consistency':len(fps)==1,'prompt_semantic_quality':not any(e=='PROMPT_SEMANTIC_QA_FAIL' for e in errors)}}
    runtime_path.write_text(json.dumps(runtime,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'beat_graph.json').write_text(json.dumps({'version':'10.1.9','beats':[{'beat_id':s['beat_ids'][0],'shot_id':s['shot_id'],'event_ids':s['event_ids']} for s in shots]},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'adapter_outputs.json').write_text(json.dumps(native,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'qa_report.json').write_text(json.dumps(runtime['qa'],ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"RUNTIME_VERSION=10.1.9 ACTION_CONTRACTS={len(contracts)} ABILITY_CONTRACTS={len(ability_contracts)} EVENTS={len(events)} SHOTS={len(shots)} ERRORS={len(errors)}")
    print('RUNTIME_STRESS_TEST=PASS' if not errors else 'RUNTIME_STRESS_TEST=FAIL')
    sys.exit(1 if errors else 0)
if __name__=='__main__': main()
