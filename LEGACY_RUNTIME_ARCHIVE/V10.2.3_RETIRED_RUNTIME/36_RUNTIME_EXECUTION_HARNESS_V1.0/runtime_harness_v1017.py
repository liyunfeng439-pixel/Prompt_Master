#!/usr/bin/env python3
import argparse, json, re, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    p=ROOT/rel
    with open(p,encoding='utf-8') as f:return json.load(f)
def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:16]

actions=load('DATA/COMBAT_KNOWLEDGE/actions_10000.json')
by_action={x['action_id']:x for x in actions}
graphs=load('29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json')
by_graph={x['action_id']:x for x in graphs}
profiles=load('35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_MANIFESTATION_PROFILES_32.json')
by_profile={x['profile_id']:x for x in profiles}

FAMILY_MAP=[
('进身突入','entry'),('试探','probe'),('破防','guard_break'),('直接打击','direct_strike'),('换角','angle_change'),
('擒拿','bind'),('卸转','redirect'),('反制','counter'),('追击','chase'),('退击','retreat_attack'),('空中','aerial'),
('低位','low_attack'),('投摔','throw'),('擒抱','grapple'),('终结','finisher')]
def family(a):
    for frag,val in FAMILY_MAP:
        if frag in a.get('name',''): return val
    return 'unknown'
def allowed_families(graph,outcome):
    arr=[]
    if outcome in ('hit','bind'): arr=graph.get('natural_next',[])
    elif outcome in ('block','dodge'): arr=graph.get('conditional_next',[])
    elif outcome=='miss': arr=graph.get('reset_next',[])
    return {x.split(':',1)[1] for x in arr if isinstance(x,str) and x.startswith('family:')}

def action_contract(actor, a, event_id, state_before=None):
    w=a['weapon']; tc=a['transition_contract']; opp=a['opponent_response']; em=a['execution_model']
    result=tc['result']
    return {
      'execution_contract_id':'EXEC-'+a['action_id'], 'knowledge_action_id':a['action_id'], 'knowledge_core_id':a['core_id'],
      'actor_identity':actor['id'], 'weapon_identity':w,
      'pre_state':{
        'distance_id':em['distance']['id'],'stance_id':em['stance']['id'],'weapon_identity':w,
        'required_balance':tc['requires'].get('attacker_balance'),'opponent_state':tc['requires'].get('opponent_state')
      },
      'execution':{
        'joint_chain':em['joint_chain'],'center_of_mass':em['center_of_mass'],'weapon_control':em['weapon_control'],
        'contact_geometry':em['contact_geometry'],'temporal_phases':em.get('temporal_phases',[])
      },
      'result':{
        'outcome_class':opp['outcome_class'],'distance_after':result.get('distance_after'),
        'recovery_output_state':result.get('recovery_output_state'),'opponent_response':opp
      },
      'counter':a.get('counter_logic'), 'recovery':a.get('failure_and_recovery'),
      'transition_contract':tc,'presentation':{'camera':a.get('cinematic'), 'vfx':a.get('vfx'), 'environment':a.get('environment')},
      'prompt':a.get('prompt_semantics'), 'event_id':event_id, 'source_trace':{'action_id':a['action_id']}
    }

def main():
  ap=argparse.ArgumentParser(); ap.add_argument('--scenario',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
  scen_path=Path(args.scenario); scen=json.load(open(scen_path,encoding='utf-8')); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
  errors=[]; warns=[]
  actors={a['id']:a for a in scen['actors']}
  canon={}
  for aid,a in actors.items():
    canon[aid]={'name':a.get('name'), 'weapon':a.get('weapon'), 'archetype':a.get('archetype'), 'provenance':a.get('provenance',{})}
    if not a.get('weapon'): errors.append(f'CANON_WEAPON_MISSING:{aid}')
    for field,info in (a.get('provenance') or {}).items():
      if isinstance(info,dict) and info.get('status')=='INFERRED' and info.get('promoted_to_canon'):
        errors.append(f'INFERENCE_PROMOTED:{aid}:{field}')
  # Resolve actions and contracts
  contracts=[]; events=[]; last_by_actor={}; previous_item=None
  for i,item in enumerate(scen.get('action_sequence',[]),1):
    actor=actors.get(item['actor_id']); aid=item['action_id']; event_id=item.get('event_id',f'EVENT-{i:03d}')
    if not actor: errors.append(f'UNKNOWN_ACTOR:{item["actor_id"]}'); continue
    a=by_action.get(aid)
    if not a: errors.append(f'UNKNOWN_ACTION:{aid}'); continue
    w=a.get('weapon');
    if w != actor.get('weapon'): errors.append(f'WEAPON_CANON_MISMATCH:{aid}:{w}!={actor.get("weapon")}')
    ps=a.get('prompt_semantics',{}); wc=a.get('execution_model',{}).get('weapon_control',{}); wb=a.get('weapon_binding',{}); tc=a.get('transition_contract',{}); opp=a.get('opponent_response',{})
    if not (wc.get('weapon')==w==wc.get('weapon_identity')==wb.get('canonical_weapon')==ps.get('weapon_identity')==tc.get('requires',{}).get('weapon_identity')==tc.get('result',{}).get('weapon_identity')):
      errors.append(f'WEAPON_INTEGRITY_FAIL:{aid}')
    if opp.get('outcome_class') != tc.get('result',{}).get('outcome') or opp.get('outcome_class') != tc.get('result',{}).get('outcome_class'):
      errors.append(f'OUTCOME_CONTRACT_MISMATCH:{aid}')
    em=a.get('execution_model',{}); sc=a.get('state_contract',{})
    if em.get('distance',{}).get('id') != tc.get('requires',{}).get('distance_id'):
      errors.append(f'STATE_DISTANCE_MISMATCH:{aid}')
    if em.get('stance',{}).get('id') != tc.get('requires',{}).get('stance_id'):
      errors.append(f'STANCE_MISMATCH:{aid}')
    # same-actor direct continuation validation. Interleaved opponent turns are not treated as an implicit self-transition.
    is_direct_continuation = bool(previous_item and previous_item.get('actor_id') == item['actor_id']) or bool(item.get('continue_from_previous'))
    if is_direct_continuation and item['actor_id'] in last_by_actor:
      prev=last_by_actor[item['actor_id']]
      g=by_graph.get(prev['action_id'])
      if not g: errors.append(f'MISSING_GRAPH:{prev["action_id"]}')
      else:
        allowed=allowed_families(g,prev['outcome'])
        nf=family(a)
        if allowed and nf not in allowed:
          errors.append(f'TRANSITION_FAMILY_FAIL:{prev["action_id"]}->{aid}:{nf} not in {sorted(allowed)}')
        prev_dist=prev['distance_after']; next_dist=em['distance']['id']
        if prev_dist not in ('state_derived',None) and next_dist not in ('state_derived',prev_dist):
          if not item.get('transition_override'):
            errors.append(f'TRANSITION_DISTANCE_FAIL:{prev["action_id"]}->{aid}:{prev_dist}->{next_dist}')
    c=action_contract(actor,a,event_id); contracts.append(c); events.append({'event_id':event_id,'type':'action_result','actor_id':actor['id'],'action_id':aid,'outcome':opp['outcome_class'],'shot_id':None})
    last_by_actor[actor['id']]={'action_id':aid,'outcome':opp['outcome_class'],'distance_after':tc['result'].get('distance_after')}
    previous_item=item
  # abilities
  ability_contracts=[]
  for j,item in enumerate(scen.get('abilities',[]),1):
    actor=actors.get(item['actor_id']); pid=item['profile_id']; p=by_profile.get(pid)
    if not actor or not p: errors.append(f'ABILITY_PROFILE_UNKNOWN:{pid}'); continue
    if p.get('archetype') != actor.get('archetype'): errors.append(f'ABILITY_ARCHETYPE_MISMATCH:{pid}')
    auth=item.get('authorization_source','user_hard_constraint')
    if p.get('required_authorization') and auth not in ('user_hard_constraint','canon','verified_knowledge'):
      errors.append(f'ABILITY_UNAUTHORIZED:{pid}')
    if item.get('activation_state')!='activated': errors.append(f'ABILITY_NOT_ACTIVATED:{pid}')
    ability_event=[f'ABILITY-{j:02d}-ACTIVATION',f'ABILITY-{j:02d}-MANIFEST',f'ABILITY-{j:02d}-CLASH',f'ABILITY-{j:02d}-RESULT_LOCK']
    ability_contracts.append({
      'ability_contract_id':f'ABILITY-CONTRACT-{j:03d}','ability_family':p['ability_family'],'actor_identity':actor['id'],
      'manifestation_profile_id':pid,'authorization_source':auth,'activation_state':item.get('activation_state'),'manifestation_state':p,
      'weapon_sync':p['synchronization_rule'],'ability_motion':p['manifestation_axis'],'contact_or_field_result':item.get('result','resolved_clash'),
      'result_lock':bool(item.get('result_lock',True)),'exit_state':item.get('exit_state','resolved'),'ability_event_ids':ability_event
    })
    events += [{'event_id':e,'type':('result_lock' if 'RESULT_LOCK' in e else 'ability'),'actor_id':actor['id'],'shot_id':None} for e in ability_event]
  # ending
  ending=scen['ending']; defeated=ending.get('defeated_actor'); victor=ending.get('victor')
  if ending.get('result_lock') is not True: errors.append('ENDING_RESULT_LOCK_MISSING')
  if ending.get('escape') is not True: errors.append('ENDING_ESCAPE_NOT_LOCKED')
  if ending.get('no_chase') is not True: errors.append('ENDING_NO_CHASE_NOT_LOCKED')
  if not defeated or not victor: errors.append('ENDING_ACTORS_MISSING')
  end_event={'event_id':'ENDING-RESULT-LOCK','type':'ending','defeated_actor':defeated,'victor':victor,'no_chase':True}
  events.append(end_event)
  # Shot budget and SHOT_IR
  dur=float(scen['duration_s']); default=(dur==30)
  target=7 if default else max(1,min(7,round(dur/4.3)))
  hard=7 if default else target
  shots=scen.get('shots')
  if not shots:
    # deterministic distribution, preserve action order; final 2 slots reserved for abilities/ending when available
    chunks=[]
    n_events=len(events)
    for s in range(target):
      start=round(s*n_events/target); end=round((s+1)*n_events/target); chunks.append(events[start:end])
    shots=[]
    for s,ch in enumerate(chunks,1):
      shots.append({'shot_id':f'S{s:02d}','duration':(4.0 if s<=2 else 5.0 if s<=5 else 4.0 if s==6 else 3.0) if default else round(dur/target,2),'events':[e['event_id'] for e in ch]})
  if len(shots)>hard: errors.append(f'SHOT_BUDGET_FAIL:{len(shots)}>{hard}')
  event_to_shot={}
  for sh in shots:
    for eid in sh.get('events',[]):
      if eid in event_to_shot: errors.append(f'EVENT_DUPLICATED:{eid}')
      event_to_shot[eid]=sh['shot_id']
  for e in events:
    if e.get('event_id') not in event_to_shot: errors.append(f'EVENT_UNASSIGNED:{e.get("event_id")}')
  # Last shot must hold result lock and ending
  if shots:
    last_events=set(shots[-1].get('events',[]))
    if 'ENDING-RESULT-LOCK' not in last_events: errors.append('ENDING_NOT_IN_FINAL_SHOT')
  shot_ir=[]
  for sh in shots:
    evs=[e for e in events if e.get('event_id') in sh.get('events',[])]
    acts=[c for c in contracts if c['event_id'] in sh.get('events',[])]
    shot_ir.append({
      'shot_id':sh['shot_id'],'duration':sh['duration'],'story_function':sh.get('story_function','combat_execution'),
      'beat_ids':sh.get('beat_ids',[f'BEAT-{sh["shot_id"]}']), 'event_ids':sh.get('events',[]),
      'actor_state':canon,'spatial_state':scen.get('spatial_state',{'status':'INFERRED','note':'asset-inferred until explicitly locked'}),
      'action_chain':[{'action_id':c['knowledge_action_id'],'actor':c['actor_identity'],'weapon':c['weapon_identity'],'result':c['result']['outcome_class'],'event_id':c['event_id']} for c in acts],
      'camera':sh.get('camera','cause-following; preserve contact/reaction/recovery'),
      'physics':'derived from resolved action contracts; contact→force→reaction→recovery',
      'vfx':'bound to physical result; no VFX-created event',
      'continuity':'identity/weapon/spatial/state inherited from previous shot',
      'damage_state':scen.get('damage_state',{}),
      'ending_state':end_event if 'ENDING-RESULT-LOCK' in sh.get('events',[]) else {'result_lock':False}
    })
  # adapter invariant manifest
  invariant={'event_ids':[x['event_ids'] for x in shot_ir],'causal_order':[x['event_ids'] for x in shot_ir], 'actor_identity':sorted(actors.keys()),'weapon_identity':{k:v['weapon'] for k,v in actors.items()},'ending_state':end_event}
  inv_hash=sha(invariant)
  adapters={m:{'source':'SHOT_IR_V10.1.7','invariant_hash':inv_hash,'events_preserved':True,'text':f'{m} native compilation from SHOT_IR; preserve actor identity, weapon identity, causal order, physical result, ending state.'} for m in ['universal','seedance_2_5','minimax_h3']}
  # QA
  qa={'status':'FAIL' if errors else 'PASS','errors':errors,'warnings':warns,'counts':{'actions':len(actions),'contracts':len(contracts),'abilities':len(ability_contracts),'shots':len(shots)},'invariants':{'weapon_integrity':not any('WEAPON_' in e for e in errors),'outcome_contract':not any('OUTCOME_' in e for e in errors),'state_contract':not any('STATE_' in e or 'STANCE_' in e for e in errors),'shot_budget':len(shots)<=hard,'ending_lock':ending.get('result_lock') is True,'no_chase':ending.get('no_chase') is True,'adapter_invariant_hash':inv_hash}}
  runtime={'schema_version':'1.0','runtime_version':'10.1.7','scenario_id':scen['scenario_id'],'canon':canon,'action_contracts':contracts,'ability_contracts':ability_contracts,'events':events,'ending':ending,'qa':qa}
  (out/'runtime_trace.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2),encoding='utf-8')
  (out/'beat_graph.json').write_text(json.dumps({'version':'10.1.7','beats':[{'beat_id':s.get('beat_ids',[''])[0],'shot_id':s['shot_id'],'event_ids':s.get('events',[])} for s in shots]},ensure_ascii=False,indent=2),encoding='utf-8')
  (out/'shot_ir.json').write_text(json.dumps({'version':'10.1.7','shot_count':len(shot_ir),'shots':shot_ir},ensure_ascii=False,indent=2),encoding='utf-8')
  (out/'adapter_outputs.json').write_text(json.dumps(adapters,ensure_ascii=False,indent=2),encoding='utf-8')
  (out/'qa_report.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
  print(f'RUNTIME_VERSION=10.1.7 ACTION_CONTRACTS={len(contracts)} ABILITY_CONTRACTS={len(ability_contracts)} SHOTS={len(shots)} ERRORS={len(errors)}')
  print('PASS' if not errors else 'FAIL')
  sys.exit(1 if errors else 0)
if __name__=='__main__': main()
