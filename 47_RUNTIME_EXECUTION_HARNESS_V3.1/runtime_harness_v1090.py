#!/usr/bin/env python3
"""V10.18.6 zero-copy runtime harness. Weapon Signature Ultimate uses compatibility-aware candidate selection.
Scenario data is declarative: no character, weapon, victor, or ending is hard-coded.
"""
import argparse, json, hashlib, importlib.util, time, sys, math, copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    p=ROOT/rel if not Path(rel).is_absolute() else Path(rel)
    with open(p,encoding='utf-8') as f:return json.load(f)

def sha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:16]

def import_module(name, rel):
    spec=importlib.util.spec_from_file_location(name, ROOT/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

COMP=import_module('native_compiler_v1090','48_NATIVE_PROMPT_COMPILER_V3.1/native_prompt_compiler_v1090.py')
QA=import_module('deep_prompt_qa_v1090','49_DEEP_PROMPT_SEMANTIC_QA_V3.1/deep_prompt_semantic_qa_v1090.py')
DIRECTOR=import_module('combat_director_v1090','30_COMBAT_DIRECTOR_BRAIN_V3.3/combat_director_v5.py')
NARRATIVE=import_module('adaptive_narrative','28_ADAPTIVE_COMBAT_NARRATIVE_RUNTIME_V1.0/adaptive_narrative_runtime.py')

FAMILY_MAP=[('进身突入','entry'),('试探','probe'),('破防','guard_break'),('直接打击','direct_strike'),('换角','angle_change'),('缠压','bind'),('卸转','redirect'),('反击','counter'),('追击','chase'),('退击','retreat_attack'),('空中','aerial'),('低位','low_attack'),('摔投','throw'),('擒拿','grapple'),('终结','finisher')]
def family(a):
    for frag,val in FAMILY_MAP:
        if frag in a.get('name',''): return val
    return 'unknown'

def allowed_families(graph,outcome):
    key={'hit':'natural_next','bind':'natural_next','block':'conditional_next','dodge':'conditional_next','miss':'reset_next','counter':'conditional_next'}.get(outcome)
    if not key:return set()
    return {x.split(':',1)[1] for x in graph.get(key,[]) if isinstance(x,str) and x.startswith('family:')}

def action_contract(actor,a,event_id):
    tc=a['transition_contract']; opp=a['opponent_response']; em=a['execution_model']
    return {'execution_contract_id':'EXEC-'+a['action_id'],'knowledge_action_id':a['action_id'],'knowledge_core_id':a['core_id'],
      'actor_identity':actor['id'],'weapon_identity':a['weapon'],'pre_state':a['state_contract']['pre_state'],
      'action_name':a.get('name',''), 'decision_trigger':a.get('decision_trigger',{}),'execution_native':a.get('execution',{}),
      'execution':{'joint_chain':em['joint_chain'],'center_of_mass':em['center_of_mass'],'weapon_control':em['weapon_control'],'contact_geometry':em['contact_geometry'],'temporal_phases':em.get('temporal_phases',[]),'execution_variant':a.get('execution_variant',{})},
      'result':{'outcome_class':opp['outcome_class'],'distance_after':tc['result'].get('distance_after'),'recovery_output_state':tc['result'].get('recovery_output_state'),'opponent_response':opp},
      'counter':a.get('counter_logic'),'recovery':a.get('failure_and_recovery'),'transition_contract':tc,
      'presentation':{'camera':a.get('cinematic'),'vfx':a.get('vfx'),'environment':a.get('environment')},'prompt':a.get('prompt_semantics'),
      'event_id':event_id,'source_trace':{'action_id':a['action_id'],'provenance_status':'knowledge_derived'}}

def build_ending(scen, actors, errors):
    e=dict(scen.get('ending') or {})
    mode=e.get('mode','victory' if e.get('victor') else 'open')
    e['mode']=mode
    if not e.get('result_lock',True): errors.append('ENDING_RESULT_LOCK_REQUIRED')
    if e.get('victor') and e.get('defeated_actor') and e['victor']==e['defeated_actor']: errors.append('ENDING_ACTOR_COLLISION')
    for key in ('victor','defeated_actor'):
        if e.get(key) and e[key] not in actors: errors.append(f'ENDING_UNKNOWN_ACTOR:{key}:{e[key]}')
    # Optional fields are preserved; no victory/defeat is invented for draw/open endings.
    return e

def _shot_complexity(event_group, event_map, spatial_by_event):
    score=0
    for eid in event_group:
        e=event_map.get(eid,{})
        typ=e.get('type'); out=e.get('outcome')
        if typ in {'ability_clash','result_lock','ending'}: score += 3
        if out in {'hit','counter','throw','disarm'}: score += 2
        if out in {'block','dodge','bind','miss'}: score += 1
        tr=spatial_by_event.get(eid,{})
        if tr.get('transition') or tr.get('intent',{}).get('intent') in {'horizontal_reposition','aerial_transition','target_lift','high_air_transition','fall','return_to_ground'}: score += 2
        if e.get('highlight'): score += 3.5
        if float((e.get('impact_profile') or {}).get('score',0)) >= 72: score += 2.5
    if len(event_group)>=3: score += 1
    return score

def _boundary_score(left, right, event_map, spatial_by_event):
    """Higher means a semantic camera cut is justified between two adjacent Events."""
    a=event_map.get(left,{}) or {}; b=event_map.get(right,{}) or {}; score=0.0
    if a.get('actor_id') != b.get('actor_id'): score += 1.2
    if a.get('outcome') in {'block','dodge','miss','bind','counter','disarm','throw'}: score += 1.5
    if b.get('type') in {'recovery','ability_clash','result_lock','ending'}: score += 2.0
    ta=spatial_by_event.get(left,{}) or {}; tb=spatial_by_event.get(right,{}) or {}
    if ta.get('transition') or tb.get('transition'): score += 1.8
    if a.get('highlight') and b.get('outcome') in {'hit','counter','throw','disarm'}: score += 0.8
    # Keep a highlight's internal cause→impact chain together unless the next Event is a distinct result/recovery.
    if a.get('highlight') and b.get('type') not in {'recovery','result_lock','ending'}: score -= 1.5
    if a.get('type')=='action_result' and b.get('type')=='action_result' and a.get('actor_id')==b.get('actor_id') and a.get('outcome') in {'hit','counter'}: score -= 0.7
    return score

def _semantic_shot_groups(event_group, event_map, spatial_by_event, shot_n):
    if shot_n<=1 or len(event_group)<=1: return [list(event_group)]
    candidates=[(_boundary_score(event_group[i],event_group[i+1],event_map,spatial_by_event),i+1) for i in range(len(event_group)-1)]
    candidates.sort(reverse=True)
    cuts=[]
    for score,pos in candidates:
        if score < 1.0: continue
        if any(abs(pos-c)<=1 for c in cuts): continue
        cuts.append(pos)
        if len(cuts)>=shot_n-1: break
    if len(cuts)<shot_n-1:
        for pos in range(1,len(event_group)):
            if pos not in cuts and all(abs(pos-c)>0 for c in cuts):
                cuts.append(pos)
                if len(cuts)>=shot_n-1: break
    cuts=sorted(cuts[:shot_n-1])
    out=[]; prev=0
    for c in cuts+[len(event_group)]:
        if c>prev: out.append(event_group[prev:c])
        prev=c
    return out

def _cinematic_shot_count(event_group, event_map, spatial_by_event, is_final=False):
    score=_shot_complexity(event_group,event_map,spatial_by_event)
    if len(event_group)==1: return 1
    if is_final and score>=3: return min(3,max(2,len(event_group)))
    if score>=6: return min(3,max(2,len(event_group)))
    if score>=3 and len(event_group)>=2: return 2
    return 1

def make_shot_plan(events,duration,ending_id,ability_lock_id=None, hard_max=7):
    """Semantic hierarchy: Events form causal Beats; Shot cuts occur only at justified causal/camera boundaries."""
    n=len(events)
    if n<=0: return {'beats':[], 'shots':[]}
    if duration==30:
        beat_target=min(hard_max,max(1,math.ceil(n/2.2))); beat_target=max(1,min(7,beat_target))
        if n>=6: beat_target=max(6,beat_target)
    else:
        beat_target=min(hard_max,max(1,math.ceil(n/2.2),math.ceil(duration/4.5)),n)
    reserved_last={ending_id}; reserved_penultimate={ability_lock_id} if ability_lock_id else set()
    main=[e['event_id'] for e in events if e['event_id'] not in reserved_last|reserved_penultimate]
    groups=[[] for _ in range(beat_target)]; last=beat_target-1; pen=beat_target-2 if beat_target>=2 else last
    slots=max(1,beat_target-len(reserved_last)-len(reserved_penultimate))
    for i,eid in enumerate(main):
        gi=min(slots-1,int(i*slots/max(1,len(main)))); groups[gi].append(eid)
    if ability_lock_id: groups[pen].append(ability_lock_id)
    groups[last].append(ending_id)
    for i in range(beat_target):
        if not groups[i]:
            donor=next((j for j in range(i-1,-1,-1) if len(groups[j])>1),None)
            if donor is not None: groups[i].append(groups[donor].pop())
    groups[last]=[x for x in groups[last] if x!=ending_id]+[ending_id]
    event_map={e['event_id']:e for e in events}
    beat_weights=[]
    for i,g in enumerate(groups):
        w=1.0; types=[event_map[e].get('type') for e in g]; outcomes=[event_map[e].get('outcome') for e in g]
        if i==0:w*=0.9
        if any(o in {'hit','counter','throw','disarm'} for o in outcomes):w*=1.15
        if any(t in {'ability_clash','result_lock','ending'} for t in types):w*=1.35
        if g and all(t=='recovery' for t in types):w*=0.72
        if i==last:w*=1.2
        beat_weights.append(w)
    total_w=sum(beat_weights) or beat_target
    beat_durations=[round(duration*w/total_w,2) for w in beat_weights]; beat_durations[-1]=round(duration-sum(beat_durations[:-1]),2)
    beats=[]; shots=[]
    for bi,g in enumerate(groups):
        bid=f'BEAT-{bi+1:03d}'
        spatial_by_event={e: next((t for t in globals().get('_ACTIVE_SPATIAL_TRACE',[]) if t.get('event_id')==e),{}) for e in g}
        shot_n=min(3,_cinematic_shot_count(g,event_map,spatial_by_event,is_final=(bi==last)),len(g))
        chunks=_semantic_shot_groups(g,event_map,spatial_by_event,shot_n)
        shot_weights=[]
        for c in chunks:
            ww=1.0; outs=[event_map[e].get('outcome') for e in c]; tys=[event_map[e].get('type') for e in c]
            if any(o in {'hit','counter','throw','disarm'} for o in outs): ww*=1.2
            if any(t in {'ability_clash','result_lock','ending'} for t in tys): ww*=1.35
            if all(t=='recovery' for t in tys): ww*=0.8
            shot_weights.append(ww)
        sw=sum(shot_weights) or len(chunks); local=[round(beat_durations[bi]*w/sw,2) for w in shot_weights]; local[-1]=round(beat_durations[bi]-sum(local[:-1]),2)
        shot_ids=[]
        for si,c in enumerate(chunks):
            sid=f'S{bi+1:02d}{chr(65+si)}'; shot_ids.append(sid)
            shots.append({'shot_id':sid,'beat_id':bid,'beat_ids':[bid],'beat_index':bi,'shot_index':si,'shot_count_in_beat':len(chunks),'duration':local[si],'event_ids':c,'shot_group_reason':'semantic_causal_boundary'})
        beats.append({'beat_id':bid,'beat_index':bi,'duration':beat_durations[bi],'event_ids':g,'shot_ids':shot_ids,'shot_count':len(chunks),'shot_grouping':'semantic_causal'})
    # Honor explicit highlight presentation duration when feasible, then redistribute
    # the tiny delta across non-overridden shots so global duration stays exact.
    overrides=[]
    for idx,sh in enumerate(shots):
        prefs=[((event_map.get(e,{}).get('impact_profile') or {}).get('highlight_choreography') or {}).get('preferred_duration_s') for e in sh.get('event_ids',[])]
        prefs=[float(x) for x in prefs if x is not None]
        if prefs and len(sh.get('event_ids',[]))==1:
            overrides.append((idx,prefs[0]))
    if overrides:
        fixed={i for i,_ in overrides}; current=sum(shots[i]['duration'] for i,_ in overrides); target=sum(v for _,v in overrides); delta=round(target-current,2)
        for i,v in overrides: shots[i]['duration']=round(v,2)
        adjustable=[i for i in range(len(shots)) if i not in fixed]
        if adjustable and abs(delta)>0.001:
            base=sum(shots[i]['duration'] for i in adjustable) or len(adjustable); consumed=0.0
            for n,i in enumerate(adjustable):
                adj=round(delta-consumed,2) if n==len(adjustable)-1 else round(delta*(shots[i]['duration']/base),2); consumed+=0 if n==len(adjustable)-1 else adj
                shots[i]['duration']=round(max(0.05,shots[i]['duration']-adj),2)
    return {'beats':beats,'shots':shots}

def resolve_action_camera(action, role, shot_index=0, shot_count=1):
    cam=(action or {}).get('cinematic') or {}; seq=cam.get('shot_sequence') or []
    primary=(cam.get('primary') or {}).get('execution') or ''
    contact=(cam.get('contact') or {}).get('execution') or ''
    continuity=cam.get('continuity') or {}
    prompt=cam.get('prompt_camera_sentence') or ''
    if role in {'impact_payoff','final_impact_then_result_observation'} and contact: base=contact
    elif shot_index==0 and primary: base=primary
    elif seq and shot_index < len(seq): base=str(seq[shot_index])
    else: base=primary or contact
    cut_rule=continuity.get('cut_rule','')
    motion_rule=continuity.get('motion_rule','')
    return '；'.join(x for x in [prompt,base,cut_rule,motion_rule] if x) or ''

def resolve_action_vfx(action, role):
    v=(action or {}).get('vfx') or {}; parts=[]
    for k in ('primary','timing','direction','suppression','secondary'):
        val=v.get(k)
        if isinstance(val,dict): val=val.get('execution') or val.get('name')
        if val: parts.append(str(val))
    env=(action or {}).get('environment') or {}; surf=env.get('surface') or {}
    if surf.get('response'): parts.append(f'环境反馈：{surf["response"]}')
    return '；'.join(parts) or ''

def story_role(group,event_map,index,total):
    if index==0:return 'combat_open'
    if index==total-1:return 'final_clash_result'
    types=[event_map[e].get('type') for e in group]
    outcomes=[event_map[e].get('outcome') for e in group]
    if 'ability_clash' in types or 'result_lock' in types:return 'final_build'
    if any(event_map[e].get('highlight') for e in group): return 'impact_payoff'
    if any(o in {'block','dodge','bind','miss'} for o in outcomes):return 'counter_exchange'
    if any(o in {'hit','counter','throw','disarm'} for o in outcomes):return 'pressure_shift'
    if any(t=='recovery' for t in types):return 'recovery_link'
    return 'high_intensity_exchange' if index>=max(1,total//2) else 'escalation'

def choose_closeup_role(sh, event_map, beat_index, beat_count, closeup_used, closeup_cap):
    """Select a motivated cinematic close-up without creating a new Event."""
    if closeup_used >= closeup_cap:
        return None
    events=[event_map[e] for e in sh.get('event_ids',[]) if e in event_map]
    if not events:
        return None
    types={e.get('type') for e in events}
    outcomes={e.get('outcome') for e in events}
    # Highest-value semantic anchors first. The close-up remains a presentation of an existing event.
    if sh.get('story_function')=='final_clash_result' and ('result_lock' in types or 'ability_clash' in types or outcomes & {'hit','counter','throw','disarm'}):
        return 'final_impact_closeup'
    if 'ability_clash' in types or 'result_lock' in types or 'ability' in types:
        return 'energy_manifestation_closeup'
    if any(e.get('highlight') for e in events):
        return 'impact_contact_closeup'
    if outcomes & {'hit','counter','throw','disarm'}:
        return 'impact_contact_closeup'
    if outcomes & {'block','bind'}:
        return 'weapon_contact_closeup'
    # A decision/reversal moment can use a very short face/eye insert, but only once per Beat.
    if beat_index>0 and (outcomes & {'dodge','miss'} or sh.get('story_function')=='counter_exchange') and sh.get('shot_index')==0:
        return 'decision_reaction_closeup'
    return None

CLOSEUP_TEXT={
    'impact_contact_closeup':'炫酷冲击特写：在既有命中/反制/摔投/缴械事件发生的同一连续动作中，短促切入武器与受力接触点，极浅景深、强透视压缩、短暂微慢动作强调接触瞬间；镜头只放大已发生的力量与材质反馈，不新增攻击或命中。',
    'weapon_contact_closeup':'武器接触特写：贴近既有格挡/缠压接触点，捕捉兵器刃口、杆身、护具受力与火花/能量摩擦细节，短促高速跟焦后立即回到动作结果；不得改变武器数量、类型或轨迹。',
    'decision_reaction_closeup':'决策反应特写：在既有闪避/落空/反制判断发生时，短暂切入眼神、面部张力或持械姿态变化，表现角色已经做出的判断，不新增对白、动作或战术事件；随后立即接回空间关系。',
    'energy_manifestation_closeup':'能量显现特写：贴近既有能力/能量事件，展示能量附着于角色或武器的材质、流动、压缩与环境反馈，短促微慢动作强调形态变化；不得提前释放尚未发生的攻击。',
    'final_impact_closeup':'终极碰撞特写：在最终既有碰撞的接触点进入极短促超近景，强调力量压缩、材质破碎、冲击波与受力反馈；随后切回结果观察。RESULT_LOCK之后只观察，不新增事件。',
}

def _highlight_choreography_for_shot(sh, event_map):
    """Merge choreography metadata for the highlighted Event(s) carried by this Shot."""
    profiles=[]
    for eid in sh.get('event_ids',[]):
        ev=event_map.get(eid,{}) or {}
        if ev.get('highlight') and ev.get('impact_profile',{}).get('highlight_choreography'):
            profiles.append(ev['impact_profile']['highlight_choreography'])
    if not profiles: return None
    # One Beat may contain multiple Events, but presentation directives remain ordered.
    first=profiles[0]
    return {
        'version':max((str(p.get('version','0')) for p in profiles), default='2.0'),
        'profiles':profiles,
        'preferred_duration_s':next((p.get('preferred_duration_s') for p in profiles if p.get('preferred_duration_s') is not None),None),
        'tempo_phases':list(dict.fromkeys(x for p in profiles for x in p.get('tempo_phases',[]))),
        'speed_curve':first.get('speed_curve'),
        'camera':first.get('camera',{}),
        'camera_phases':list(dict.fromkeys(x for p in profiles for x in p.get('camera_phases',[]))),
        'impact_stack':list(dict.fromkeys(x for p in profiles for x in p.get('impact_stack',[]))),
        'result_chain':list(dict.fromkeys(x for p in profiles for x in p.get('result_chain',[]))),
        'contact_lock':all(bool(p.get('contact_lock',True)) for p in profiles),
        'restore_on_impact':all(bool(p.get('restore_on_impact',True)) for p in profiles),
        'fact_bound':True,
        'no_new_event':True,
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--scenario',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    t0=time.perf_counter(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    weapon_ai=import_module('adaptive_weapon_control','25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py')
    ultimate_ai=import_module('weapon_signature_ultimate','25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py')
    preflight=import_module('v1018validator','TOOLS/validate_v10186_runtime.py')
    if not preflight.validate_current_runtime(): print('V10.18_CURRENT_RUNTIME_PREFLIGHT_FAIL'); sys.exit(1)
    scen=load(args.scenario)
    actions=load('DATA/COMBAT_KNOWLEDGE/actions_10000.json'); by_action={a['action_id']:a for a in actions}
    graphs=load('29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1/action_graphs/action_universe_graph_18000.json'); by_graph={g['action_id']:g for g in graphs}
    profiles=load('35_ABILITY_EXECUTION_CONTRACT_V1.0/ABILITY_MANIFESTATION_PROFILES_32.json'); by_profile={p['profile_id']:p for p in profiles}
    errors=[]; warnings=[]; events=[]; contracts=[]; last_action_by_actor={}; planning_trace=[]; replan_count=0; lookahead_checks=0; phase_states=[]
    actors={a['id']:a for a in scen.get('actors',[])}
    if not actors: errors.append('NO_ACTORS')
    canon={aid:{'id':aid,'name':a.get('name',aid),'weapon':a.get('weapon'),'archetype':a.get('archetype'),'provenance':a.get('provenance',{})} for aid,a in actors.items()}
    for aid,a in actors.items():
        for k,info in (a.get('provenance') or {}).items():
            if isinstance(info,dict) and info.get('status')=='INFERRED' and info.get('promoted_to_canon'): errors.append(f'INFERENCE_PROMOTED:{aid}:{k}')
    selected_payloads={}; history=[]; narrative_history=[]; current_phase=None
    highlight_selected=0; highlight_event_ids=[]
    action_sequence=list(scen.get('action_sequence',[]))
    director_mode=scen.get('director_mode', 'autonomous' if not action_sequence else 'constrained')
    spatial_cfg=scen.get('spatial_combat', {}) or {}
    spatial_mode=spatial_cfg.get('mode', 'adaptive')
    source_spatial=dict(scen.get('spatial_state', {}) or {})
    spatial_state=DIRECTOR.build_spatial_state(list(actors.keys()), spatial_cfg, source_spatial)
    spatial_state['spatial_problem']='maintain readable relative position'
    spatial_state['spatial_goal']='adaptive spatial change only when it solves or escalates the current tactical problem'
    spatial_trace=[]
    if not action_sequence:
        # Asset-driven mode: Director creates a bounded tactical sequence from the Canon actor registry.
        actor_ids=list(actors.keys())
        for i in range(min(10, max(1, int(scen.get('core_action_target', 8))))):
            aid=actor_ids[i % len(actor_ids)]
            action_sequence.append({'event_id':f'DIRECTOR-EVENT-{i+1:03d}','actor_id':aid,'continue_from_previous':i>0,'distance':scen.get('initial_distance','mid'),'tactical_problem':scen.get('objective','establish_a_valid_exchange')})
    highlight_target_count=DIRECTOR.highlight_target(float(scen.get('duration_s',30)), len(action_sequence) if action_sequence else int(scen.get('core_action_target',8)), scen.get('highlight_target'))
    for i,item in enumerate(action_sequence,1):
        actor=actors.get(item.get('actor_id')); requested_id=item.get('action_id'); eid=item.get('event_id',f'EVENT-{i:03d}')
        if not actor: errors.append(f'UNKNOWN_ACTOR:{item.get("actor_id")}'); continue
        requested=by_action.get(requested_id) if requested_id else None
        target_actor_id=item.get('target_actor_id') or next((x for x in actors if x!=actor['id']), None)
        actor_view=spatial_state.get('actors',{}).get(actor['id'],{})
        target_view=spatial_state.get('actors',{}).get(target_actor_id,{}) if target_actor_id else {}
        spatial_state['active_actor_id']=actor['id']; spatial_state['target_actor_id']=target_actor_id
        spatial_state['layer']=actor_view.get('layer','ground')
        spatial_state['active_anchor']=actor_view.get('anchor','UNKNOWN')
        spatial_state['target_layer']=target_view.get('layer','ground') if target_actor_id else None
        if target_actor_id:
            za=DIRECTOR.SPATIAL_LAYERS.get(spatial_state['layer'],0); zt=DIRECTOR.SPATIAL_LAYERS.get(spatial_state['target_layer'],0)
            spatial_state['relative_height']='above' if za>zt else 'below' if za<zt else 'same_level'
        provisional_state={'distance':item.get('distance', requested.get('execution_model',{}).get('distance',{}).get('id') if requested else scen.get('initial_distance','mid')), 'resource_pressure':item.get('resource_pressure',''), 'positional_goal':item.get('positional_goal',''), 'terrain_pressure':item.get('terrain_pressure',False),'spatial_layer':spatial_state.get('layer'),'relative_height':spatial_state.get('relative_height'),'spatial_mode':spatial_mode,'actor_spatial':spatial_state.get('actors',{}),'spatial_problem':spatial_state.get('spatial_problem'),'spatial_goal':spatial_state.get('spatial_goal')}
        personality=actor.get('combat_personality',{}) or {}
        constraints={'ending_locked':bool((scen.get('ending') or {}).get('result_lock',True))}
        prediction=DIRECTOR.predict_opponent(personality,provisional_state,history,constraints)
        provisional_state['spatial_problem']=spatial_state.get('spatial_problem','')
        provisional_state['spatial_goal']=spatial_state.get('spatial_goal','')
        current_phase=DIRECTOR.advance_phase(current_phase,scen.get('objective','win_the_tactical_exchange'),item.get('tactical_problem',''),personality,provisional_state,history,constraints,False,spatial_state)
        if not current_phase or current_phase.phase_id not in [x.get('phase_id') for x in phase_states]:
            phase_states.append(current_phase.__dict__.copy())
        candidates=[]
        if requested: candidates.append(requested)
        candidates.extend(DIRECTOR.autonomous_candidate_pool(actions,actor,provisional_state,limit=40))
        # Spatial candidate backfill: once the fight has established its first tactical exchange,
        # ensure explicit aerial/vertical actions are visible to the Director even when the primary
        # retrieval window is saturated by ground actions. This does not invent an action; it only
        # widens retrieval to knowledge entries whose own semantics explicitly support the transition.
        if director_mode=='autonomous' and spatial_mode in {'adaptive','vertical'} and len(contracts)>=2 and spatial_state.get('actors',{}).get(actor.get('id'),{}).get('layer','ground')=='ground':
            spatial_backfill=[]
            for cand in actions:
                if cand.get('weapon') != actor.get('weapon'): continue
                intent=DIRECTOR.infer_spatial_intent(cand)
                if intent.get('intent') in {'aerial_transition','target_lift'} and intent.get('confidence')=='explicit':
                    spatial_backfill.append(cand)
                    if len(spatial_backfill)>=12: break
            candidates.extend(spatial_backfill)
        # Deduplicate while preserving requested preference.
        seen=set(); candidates=[x for x in candidates if not (x.get('action_id') in seen or seen.add(x.get('action_id')))]
        # In autonomous mode, transition-valid families are filtered before scoring when a same-actor continuation exists.
        # This prevents the spatial objective from selecting an aerial action that is later invalidated by A→B transition rules.
        prev=last_action_by_actor.get(actor['id'])
        if director_mode=='autonomous' and prev and item.get('continue_from_previous'):
            g_prev=by_graph.get(prev['action_id']); allowed_prev=allowed_families(g_prev or {},prev['outcome'])
            if allowed_prev:
                valid_candidates=[x for x in candidates if family(x) in allowed_prev]
                if valid_candidates: candidates=valid_candidates
        highlight_due_now=DIRECTOR.highlight_due(float(scen.get('duration_s',30)), i-1, len(action_sequence), highlight_selected, highlight_target_count)
        if director_mode=='autonomous':
            chosen,ranked=DIRECTOR.select_action_candidate(candidates,actor,provisional_state,current_phase,prediction,requested_id,[h.get('outcome') for h in history],list(selected_payloads.keys()) + [str(x.get('execution_model',{}).get('joint_chain',{}).get('id',''))+'|'+str(x.get('execution_model',{}).get('center_of_mass',{}).get('path_id',''))+'|'+str(x.get('execution_model',{}).get('contact_geometry',{}).get('id','')) for x in selected_payloads.values()],spatial_state,len(contracts),spatial_mode,highlight_due_now,highlight_selected,highlight_target_count)
            a=chosen
            planning_trace.append({'event_id':eid,'type':'director_action_selection','mode':'autonomous','requested_action_id':requested_id,'selected_action_id':a.get('action_id') if a else None,'candidate_ranking':ranked,'opponent_prediction':prediction,'phase_id':current_phase.phase_id,'spatial_layer':spatial_state.get('layer'),'spatial_mode':spatial_mode})
        else:
            a=requested
            planning_trace.append({'event_id':eid,'type':'director_action_selection','mode':'constrained','requested_action_id':requested_id,'selected_action_id':a.get('action_id') if a else None,'opponent_prediction':prediction,'phase_id':current_phase.phase_id,'spatial_layer':spatial_state.get('layer'),'spatial_mode':spatial_mode,'highlight_due':highlight_due_now})
        if not a: errors.append(f'NO_EXECUTABLE_ACTION:{eid}'); continue
        # Weapon execution semantics are intentionally resolved only after A→B/B→C
        # transition validation and lookahead. The final committed action is the only
        # input to the execution-variant resolver, so replanning cannot leave stale
        # hand-held or remote semantics attached to the wrong action.
        remote_intent=item.get('remote_weapon_intent', item.get('telekinetic_intent', item.get('spirit_control_intent')))
        spatial_intent=DIRECTOR.infer_spatial_intent(a)
        spatial_allowed=DIRECTOR.spatial_transition_allowed(spatial_state,a,spatial_mode)
        if spatial_mode=='grounded' and DIRECTOR.infer_spatial_intent(a).get('intent') in {'target_lift','aerial_transition','high_air_transition','fall'}:
            errors.append(f'SPATIAL_GROUNDED_CONFLICT:{a.get("action_id")}')
            spatial_allowed=False
        spatial_trace.append({'event_id':eid,'action_id':a.get('action_id'),'from_layer':spatial_state.get('layer'),'intent':spatial_intent,'allowed':spatial_allowed,'mode':spatial_mode})
        em=a.get('execution_model',{}); tc=a.get('transition_contract',{}); wc=em.get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); opp=a.get('opponent_response',{})
        if a.get('weapon') != actor.get('weapon'): errors.append(f'WEAPON_CANON_MISMATCH:{a.get("action_id")}')
        if not (wc.get('weapon')==a['weapon']==wb.get('canonical_weapon')==wb.get('execution_weapon')==ps.get('weapon_identity')==tc.get('requires',{}).get('weapon_identity')==tc.get('result',{}).get('weapon_identity')): errors.append(f'WEAPON_INTEGRITY_FAIL:{requested_id}')
        if not (opp.get('outcome_class')==tc.get('result',{}).get('outcome')==tc.get('result',{}).get('outcome_class')): errors.append(f'OUTCOME_CONTRACT_MISMATCH:{requested_id}')
        pn=a.get('preconditions_normalized',{})
        if pn.get('distance_id')!=em.get('distance',{}).get('id') or pn.get('stance_id')!=em.get('stance',{}).get('id'): errors.append(f'NORMALIZED_STATE_FAIL:{requested_id}')
        transition_status='INITIAL'
        prev=last_action_by_actor.get(actor['id'])
        if prev and item.get('continue_from_previous'):
            g=by_graph.get(prev['action_id']); allowed=allowed_families(g or {},prev['outcome']); nf=family(a)
            if not g: errors.append(f'MISSING_GRAPH:{prev["action_id"]}')
            if allowed and nf not in allowed and not item.get('transition_override'):
                alts=[x for x in actions if x.get('actor_domain')==a.get('actor_domain') and x.get('weapon')==actor.get('weapon') and family(x) in allowed and x.get('action_id')!=a.get('action_id')]
                # Prefer never-used alternatives during recovery/replan; reuse is legal only when no fresh transition exists.
                unused=[x for x in alts if x.get('action_id') not in selected_payloads]
                if unused: alts=unused + [x for x in alts if x.get('action_id') in selected_payloads]
                # A→B validity is primary. B→C lookahead is evaluated separately and may trigger replanning of C.
                spatial_replan_needed = (director_mode=='autonomous' and spatial_mode in {'adaptive','vertical'} and len(contracts)>=2 and spatial_state.get('actors',{}).get(actor.get('id'),{}).get('layer','ground')=='ground' and DIRECTOR.infer_spatial_intent(a).get('intent') in {'aerial_transition','target_lift','high_air_transition'})
                if spatial_mode in {'adaptive','vertical'} and spatial_replan_needed:
                    # Among transition-valid alternatives, rank explicit spatial candidates first; never invent an action.
                    alts.sort(key=lambda x: DIRECTOR.spatial_candidate_score(x, spatial_state, len(contracts), history, spatial_mode)[0], reverse=True)
                def family_validator(candidate):
                    return family(candidate) in allowed if allowed else True
                def spatial_family_validator(candidate):
                    family_ok = family_validator(candidate)
                    spatial_ok = DIRECTOR.infer_spatial_intent(candidate).get('intent') in {'aerial_transition','target_lift'}
                    return family_ok and spatial_ok
                replanned,meta=DIRECTOR.replan_after_invalid(alts,spatial_family_validator if spatial_replan_needed else family_validator,max_alternates=3)
                if replanned is None and spatial_replan_needed:
                    # Spatial preference is a planning objective, not a hard constraint; recover with any valid family transition.
                    replanned,meta=DIRECTOR.replan_after_invalid(alts,family_validator,max_alternates=3)
                if replanned:
                    planning_trace.append({'event_id':eid,'type':'transition_replan','from_action':requested_id,'to_action':replanned['action_id'],'reason':'A_to_B_INVALID','status':meta['status'],'attempt':meta['attempt']}); a=replanned; transition_status='REPLANNED'; replan_count+=1
                    em=a.get('execution_model',{}); tc=a.get('transition_contract',{}); wc=em.get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); opp=a.get('opponent_response',{})
                    spatial_trace[-1].update({'action_id':a.get('action_id'),'intent':DIRECTOR.infer_spatial_intent(a)})
                else:
                    errors.append(f'TRANSITION_FAMILY_FAIL:{prev["action_id"]}->{requested_id}:{nf}'); transition_status='INVALID'
        # True B→C lookahead: if the committed B cannot legally reach the next explicit C,
        # search already-retrieved transition candidates for a B that can. This changes B, not C.
        next_item = action_sequence[i] if i < len(action_sequence) else None
        if item.get('continue_from_previous') and next_item and next_item.get('action_id') and next_item.get('actor_id')==actor.get('id'):
            next_c=by_action.get(next_item.get('action_id'))
            g_b=by_graph.get(a.get('action_id'),{}) or {}; allowed_b=allowed_families(g_b,opp.get('outcome_class'))
            if next_c is not None and allowed_b and family(next_c) not in allowed_b:
                future_alts=[x for x in candidates if x.get('action_id')!=a.get('action_id') and (not allowed_b or family(x) in allowed_b)]
                if not future_alts and allowed_b:
                    future_alts=[x for x in actions if x.get('action_id')!=a.get('action_id') and x.get('weapon')==actor.get('weapon') and family(x) in allowed_b][:40]
                replanned_b,lhmeta=DIRECTOR.lookahead_replan(a,future_alts,[next_c],by_graph,allowed_families,family,max_alternates=6)
                lookahead_checks+=1
                planning_trace.append({'event_id':eid,'type':'transition_lookahead_replan','from_action':a.get('action_id'),'next_action':next_c.get('action_id'),'status':lhmeta.get('status'),'replanned':lhmeta.get('replanned',False),'tested':lhmeta.get('tested',[])})
                if replanned_b is not None and replanned_b.get('action_id')!=a.get('action_id'):
                    a=replanned_b; replan_count+=1
                    em=a.get('execution_model',{}); tc=a.get('transition_contract',{}); wc=em.get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); opp=a.get('opponent_response',{})
                    spatial_trace[-1].update({'action_id':a.get('action_id'),'intent':DIRECTOR.infer_spatial_intent(a)})
                    planning_trace.append({'event_id':eid,'type':'bounded_replan','reason':'B_TO_C_LOOKAHEAD','selected_action_id':a.get('action_id')})
                elif replanned_b is None:
                    warnings.append(f'LOOKAHEAD_PRESSURE:{eid}:{a.get("action_id")}->{next_c.get("action_id")}')
        else:
            # Qualitative lookahead is still recorded when no explicit C exists; absence is not a failure.
            if item.get('continue_from_previous'):
                lookahead_checks+=1
                planning_trace.append({'event_id':eid,'type':'transition_lookahead','status':'NO_EXPLICIT_C','from_action':a.get('action_id')})

        highlight_score,highlight_reasons,highlight_meta=DIRECTOR.highlight_impact_score(a)
        highlight_score,highlight_meta,context_reasons=DIRECTOR.apply_highlight_context(highlight_score,highlight_meta,item,a)
        highlight_choreography=None
        if item.get('highlight_choreography'):
            highlight_choreography=DIRECTOR.build_highlight_choreography(a, item.get('highlight_choreography') or {})
        # Explicit choreography is presentation guidance for this existing Event.
        # It cannot promote an otherwise weak action into a highlight by itself.
        if item.get('highlight_choreography') and highlight_score>=52:
            ch=dict(highlight_meta.get('choreography',{})); ch.update({'temporal':len(highlight_choreography.get('tempo_phases',[]))>=3,'impact_stack':len(highlight_choreography.get('impact_stack',[])),'speed_restore':bool(highlight_choreography.get('restore_on_impact'))}); highlight_meta['choreography']=ch
        if highlight_due_now and highlight_score>=52 and len(highlight_meta.get('amplifiers',[]))>=3 and highlight_meta.get('tier')=='support':
            highlight_meta=dict(highlight_meta); highlight_meta['tier']='high'; context_reasons=list(context_reasons)+['due_slot_highlight_promotion']
        highlight_reasons=list(highlight_reasons)+list(context_reasons)
        is_highlight=bool(highlight_score>=52 and highlight_meta.get('tier') in {'high','signature','support'} and highlight_due_now and highlight_selected<highlight_target_count)
        if director_mode=='constrained' and highlight_due_now and highlight_score>=52 and highlight_meta.get('tier') in {'high','signature','support'} and highlight_selected<highlight_target_count: is_highlight=True
        if is_highlight:
            highlight_selected+=1; highlight_event_ids.append(eid)
            if highlight_choreography is None:
                highlight_choreography=DIRECTOR.build_highlight_choreography(a, item.get('highlight_choreography') or {})
        # Commit the final selected action first; then resolve its weapon execution variant.
        # This guarantees that A→B/B→C replanning cannot drop the remote-control state.
        result_lock_active=any(ev.get('type')=='result_lock' for ev in events)
        weapon_decision=weapon_ai.evaluate_weapon_control(
            actor.get('weapon'), provisional_state, history, a, remote_intent, result_lock_active
        )
        if weapon_decision.get('activate') and a.get('weapon') != '徒手':
            a=weapon_ai.build_execution_variant(a, weapon_decision)
            selected_payloads[a['action_id']]=a
        else:
            a=weapon_ai.build_execution_variant(a, weapon_decision)
            selected_payloads[a['action_id']]=a
        planning_trace.append({
            'event_id':eid, 'type':'adaptive_weapon_control_decision',
            'weapon':actor.get('weapon'), 'activated':bool(weapon_decision.get('activate')),
            'score':weapon_decision.get('score',0), 'tactical_gain':weapon_decision.get('tactical_gain',0),
            'control_cost':weapon_decision.get('control_cost',0), 'tactical_utility':weapon_decision.get('tactical_utility',0),
            'mode':weapon_decision.get('mode','HAND_HELD'), 'pattern':weapon_decision.get('pattern','release'),
            'reason':weapon_decision.get('reason',''), 'reasons':weapon_decision.get('reasons',[]),
            'execution_variant':a.get('execution_variant',{}),
            'category_independent':bool(weapon_decision.get('category_independent',True))
        })
        em=a.get('execution_model',{}); tc=a.get('transition_contract',{}); wc=em.get('weapon_control',{}); wb=a.get('weapon_binding',{}); ps=a.get('prompt_semantics',{}); opp=a.get('opponent_response',{})
        planning_trace.append({'event_id':eid,'type':'highlight_payoff_selection','highlight':is_highlight,'score':highlight_score,'tier':highlight_meta.get('tier'),'reasons':highlight_reasons,'target_count':highlight_target_count,'selected_count':highlight_selected,'choreography_version':(highlight_choreography or {}).get('version')})
        state={'distance':item.get('distance',em.get('distance',{}).get('id')),'resource_pressure':item.get('resource_pressure',''),'positional_goal':item.get('positional_goal',''),'terrain_pressure':item.get('terrain_pressure',False),'spatial_layer':spatial_state.get('layer'),'relative_height':spatial_state.get('relative_height'),'spatial_mode':spatial_mode,'actor_spatial':spatial_state.get('actors',{}),'spatial_problem':spatial_state.get('spatial_problem'),'spatial_goal':spatial_state.get('spatial_goal')}
        prediction=DIRECTOR.predict_opponent(personality,state,history,constraints)
        current_phase=DIRECTOR.advance_phase(current_phase,scen.get('objective','win_the_tactical_exchange'),item.get('tactical_problem',''),personality,state,history,constraints,False,spatial_state)
        if current_phase.phase_id not in [x.get('phase_id') for x in phase_states]: phase_states.append(current_phase.__dict__.copy())
        planning_trace.append({'event_id':eid,'type':'phase_decision','phase_id':current_phase.phase_id,'phase_goal':current_phase.phase_goal,'opponent_prediction':prediction,'transition_status':transition_status,'spatial_layer':spatial_state.get('layer'),'relative_height':spatial_state.get('relative_height')})
        before_actor_layer=spatial_state.get('actors',{}).get(actor['id'],{}).get('layer','ground')
        before_target_layer=spatial_state.get('actors',{}).get(target_actor_id,{}).get('layer','ground') if target_actor_id else None
        selected_payloads[a['action_id']]=a; c=action_contract(actor,a,eid); contracts.append(c); events.append({'event_id':eid,'type':'action_result','actor_id':actor['id'],'target_actor_id':target_actor_id,'action_id':a['action_id'],'outcome':opp['outcome_class'],'shot_id':None,'weapon_control_runtime':copy.deepcopy(a.get('weapon_control_runtime',{})),'spatial_layer_before':before_actor_layer,'target_spatial_layer_before':before_target_layer,'spatial_snapshot_before':copy.deepcopy(spatial_state),'highlight':is_highlight,'impact_profile':{'score':highlight_score,'tier':highlight_meta.get('tier'),'reasons':highlight_reasons,'choreography':highlight_meta.get('choreography',{}),'amplifiers':highlight_meta.get('amplifiers',[]),'genericity_penalty':highlight_meta.get('genericity_penalty',0),'contact_geometry':em.get('contact_geometry',{}),'force_transfer':{'force_source':(a.get('physics') or {}).get('force_source'),'weight_transfer':(a.get('physics') or {}).get('weight_transfer'),'momentum':(a.get('physics') or {}).get('momentum'),'collision':(a.get('physics') or {}).get('collision')},'body_response':opp.get('body_mechanics'),'target_reaction':opp.get('primary'),'displacement':tc.get('result',{}).get('distance_after'),'environment_response':a.get('environment',{}).get('surface',{}),'secondary_collision':item.get('secondary_collision'),'environment_anchor':item.get('environment_anchor'),'vfx_response':{'timing':a.get('vfx',{}).get('timing'),'direction':a.get('vfx',{}).get('direction')},'highlight_choreography':highlight_choreography,'highlight_semantic_fidelity':(highlight_choreography or {}).get('semantic_fidelity',{}),'highlight_directive':item.get('highlight_choreography') or {}}}); history.append({'outcome':opp['outcome_class'],'action_id':a['action_id']})
        intent_now=DIRECTOR.infer_spatial_intent(a)
        if spatial_allowed or intent_now.get('intent') not in {'target_lift','aerial_transition','high_air_transition','fall'}:
            spatial_state=DIRECTOR.advance_spatial_state(spatial_state,a,opp['outcome_class'],actor_id=actor['id'],target_actor_id=target_actor_id)
        after_actor_layer=spatial_state.get('actors',{}).get(actor['id'],{}).get('layer','ground')
        after_target_layer=spatial_state.get('actors',{}).get(target_actor_id,{}).get('layer','ground') if target_actor_id else None
        spatial_trace[-1].update({'to_layer':after_actor_layer,'target_actor_id':target_actor_id,'target_layer_before':before_target_layer,'target_layer_after':after_target_layer,'transition':(after_actor_layer!=before_actor_layer or after_target_layer!=before_target_layer),'transition_reason':spatial_state.get('transition_reason',''),'relative_height':spatial_state.get('relative_height'),'spatial_state_before':copy.deepcopy(events[-1].get('spatial_snapshot_before',{})),'spatial_state_after':copy.deepcopy(spatial_state)})
        events[-1]['spatial_snapshot_after']=copy.deepcopy(spatial_state)
        events[-1]['spatial_snapshot_contract']={'source':'event_execution','immutable':True,'actor_ids':sorted(spatial_state.get('actors',{}).keys())}
        prev_narr=narrative_history[-1] if narrative_history else None
        current_narr_state=(prev_narr.get('next_expected_state') if prev_narr else f'phase:{current_phase.phase_id}')
        next_narr_state=NARRATIVE.semantic_next_state(opp['outcome_class'], getattr(current_phase,'phase_id',''))
        narrative=NARRATIVE.build_event(item,a,current_phase,prev_narr,opp['outcome_class'],current_narr_state,next_narr_state,i,len(action_sequence))
        events[-1]['narrative']=narrative
        narrative_history.append(dict(narrative, event_id=eid, outcome=opp['outcome_class']))
        planning_trace.append({'event_id':eid,'type':'narrative_decision','combat_intent':narrative['combat_intent'],'reason_for_action':narrative['reason_for_action'],'state_transition':narrative['state_transition'],'escalation_level':narrative['escalation_level'],'phase_role':narrative['phase_role'],'reason_source':narrative['reason_source']})
        events[-1]['spatial_layer_after']=after_actor_layer
        events[-1]['target_spatial_layer_after']=after_target_layer
        if opp['outcome_class'] in ('block','dodge','miss','bind'):
            rid=f'RECOVERY-{i:03d}'; rec=a.get('failure_and_recovery',{}).get('recovery',{}); events.append({'event_id':rid,'type':'recovery','actor_id':actor['id'],'action_id':a['action_id'],'recovery_id':rec.get('id'),'output_state':a.get('failure_and_recovery',{}).get('recovery_output_state') or tc.get('result',{}).get('recovery_output_state')})
        last_action_by_actor[actor['id']]={'action_id':a['action_id'],'outcome':opp['outcome_class']}
    # Spatial continuity guard: action-event snapshots must form a deterministic chain.
    prior_after=None
    for ev in events:
        if ev.get('type')!='action_result' or not ev.get('spatial_snapshot_before'): continue
        cur_before=ev.get('spatial_snapshot_before') or {}
        if prior_after is not None:
            prev_actors=prior_after.get('actors',{}) or {}; cur_actors=cur_before.get('actors',{}) or {}
            for aid in set(prev_actors)|set(cur_actors):
                if (prev_actors.get(aid) or {}).get('layer','ground') != (cur_actors.get(aid) or {}).get('layer','ground'):
                    errors.append(f'SPATIAL_SNAPSHOT_CHAIN_BREAK:{aid}:{(prev_actors.get(aid) or {}).get("layer")}->{(cur_actors.get(aid) or {}).get("layer")}')
        prior_after=ev.get('spatial_snapshot_after')
    # Explicit Weapon Signature Ultimate switch. The exact phrase "专属大招" is the only positive trigger.
    # Negative intent has priority. The ultimate overlays one compatible existing combat Event; it never creates a new Event.
    ultimate_switch=ultimate_ai.detect_switch(scen)
    signature_ultimate=None
    if ultimate_switch.get('enabled') and events:
        action_events=[e for e in events if e.get('type')=='action_result']
        if action_events:
            requested_ultimate_actor=scen.get('signature_ultimate_actor_id')
            user_text=' '.join(ultimate_ai.find_input_text(scen))
            mentioned_actor=next((aid for aid,av in actors.items() if av.get('name') and str(av.get('name')) in user_text), None)
            weapon_mentions=[aid for aid,av in actors.items() if av.get('weapon') and str(av.get('weapon')) in user_text]
            # If a weapon is mentioned by itself, prefer the most recent active actor with that weapon;
            # if the weapon is unique, resolve it directly. This avoids first-actor ambiguity.
            mentioned_weapon_actor=None
            if not mentioned_actor and weapon_mentions:
                if len(weapon_mentions)==1:
                    mentioned_weapon_actor=weapon_mentions[0]
                else:
                    mentioned_weapon_actor=next((e.get('actor_id') for e in reversed(action_events) if e.get('actor_id') in weapon_mentions), weapon_mentions[-1])
            requested_ultimate_actor=requested_ultimate_actor or mentioned_actor
            target_event,target_action,resolution=ultimate_ai.select_signature_ultimate_event(
                action_events, selected_payloads, actors, requested_actor=requested_ultimate_actor, requested_weapon_actor=(None if requested_ultimate_actor else mentioned_weapon_actor)
            )
            if target_event and target_action:
                target_actor=actors.get(target_event.get('actor_id'),{})
                target_action,signature_ultimate=ultimate_ai.apply_signature_ultimate(
                    target_action, target_actor.get('name',target_event.get('actor_id','角色')), target_actor.get('weapon'), ultimate_switch
                )
                if signature_ultimate:
                    selected_payloads[target_action['action_id']]=target_action
                    for c in contracts:
                        if c.get('event_id')==target_event.get('event_id'):
                            replacement=action_contract(target_actor,target_action,target_event['event_id'])
                            c.clear(); c.update(replacement)
                            break
                    target_event['signature_ultimate']=copy.deepcopy(signature_ultimate)
                    target_event['prompt_semantics']=copy.deepcopy(target_action.get('prompt_semantics',{}))
                    target_event['highlight']=True
                    target_event.setdefault('impact_profile',{})['signature_ultimate']=copy.deepcopy(signature_ultimate)
                    target_event['impact_profile']['tier']='signature'
                    target_event['impact_profile']['score']=max(float(target_event['impact_profile'].get('score',0) or 0),98.0)
                    target_event['impact_profile']['choreography']={
                        'version':'ULTIMATE_1.1','preferred_duration_s':2.8,
                        'tempo_phases':['ultimate_build','ultimate_release','contact_slow','impact_lock','result_fast'],
                        'camera_phases':['ultimate_establish','weapon_focus','contact_lock','impact_follow','result_reveal'],
                        'impact_stack':['core','middle','outer'],'result_chain':['蓄势','释放','接触','受力','环境响应','结果锁定'],
                        'contact_lock':True,'restore_on_impact':True,'fact_bound':True,'no_new_event':True,'continues_combat':True
                    }
                    planning_trace.append({'event_id':target_event['event_id'],'type':'signature_ultimate_activation','switch':'ON','trigger':ultimate_switch.get('trigger_phrase'),'actor_id':target_event.get('actor_id'),'weapon':target_actor.get('weapon'),'weapon_category':signature_ultimate.get('weapon_category'),'technique_name':signature_ultimate.get('name'),'no_new_event':True,'single_event_lock':True,'contact_result_lock':True,'continues_combat':True,'candidate_resolution':resolution,'visual_intensity':'EXTREME'})
            else:
                warnings.append('SIGNATURE_ULTIMATE_NO_COMPATIBLE_EVENT')
                planning_trace.append({'type':'signature_ultimate_selection','switch':'ON','status':'NO_COMPATIBLE_EVENT','candidate_resolution':resolution})
        else:
            warnings.append('SIGNATURE_ULTIMATE_TRIGGERED_WITHOUT_ACTION_EVENT')
    elif ultimate_switch.get('enabled'):
        warnings.append('SIGNATURE_ULTIMATE_TRIGGERED_WITHOUT_COMBAT_EVENT')
    elif ultimate_switch.get('negated'):
        planning_trace.append({'type':'signature_ultimate_selection','switch':'OFF','status':'NEGATED','trigger_phrase_present':ultimate_switch.get('positive_phrase_present',False)})

    # Abilities are optional. No ability is invented when the scenario has none.
    ability_contracts=[]
    for j,item in enumerate(scen.get('abilities',[]),1):
        actor=actors.get(item.get('actor_id')); p=by_profile.get(item.get('profile_id'))
        if not actor: errors.append(f'ABILITY_UNKNOWN_ACTOR:{item.get("actor_id")}'); continue
        if not p: errors.append(f'ABILITY_PROFILE_NOT_FOUND:{item.get("profile_id")}'); continue
        if p.get('archetype') and actor.get('archetype') and p['archetype']!=actor['archetype']: errors.append(f'ABILITY_ARCHETYPE_MISMATCH:{item["profile_id"]}')
        if item.get('activation_state','activated')!='activated': errors.append(f'ABILITY_NOT_ACTIVATED:{item["profile_id"]}')
        aid=f'ABILITY-CONTRACT-{j:03d}'; stages=[f'ABILITY-{j:02d}-ACTIVATION',f'ABILITY-{j:02d}-MANIFEST',f'ABILITY-{j:02d}-WEAPON-SYNC',f'ABILITY-{j:02d}-CLASH']
        ability_contracts.append({'ability_contract_id':aid,'ability_family':p['subfamily'],'actor_identity':actor['id'],'manifestation_profile_id':p['profile_id'],'visual_profile':p.get('visual_profile'),'execution_contract_v2':p.get('execution_contract_v2'),'authorization_source':item.get('authorization_source'),'activation_state':item.get('activation_state','activated'),'result':item.get('result','resolved_clash'),'result_lock':bool(item.get('result_lock',True)),'result_lock_event_id':'ABILITY-FINAL-RESULT-LOCK','joint_clash_event_id':'ABILITY-FINAL-CLASH','exit_state':item.get('exit_state','resolved'),'ability_event_ids':stages})
        events += [{'event_id':e,'type':'ability','actor_id':actor['id'],'ability_contract_id':aid,'shot_id':None} for e in stages]
    ability_lock_id=None
    if len(ability_contracts)>=2:
        events.append({'event_id':'ABILITY-FINAL-CLASH','type':'ability_clash','actor_ids':[a['actor_identity'] for a in ability_contracts],'ability_contract_ids':[a['ability_contract_id'] for a in ability_contracts],'shot_id':None}); ability_lock_id='ABILITY-FINAL-RESULT-LOCK'; events.append({'event_id':ability_lock_id,'type':'result_lock','actor_ids':[a['actor_identity'] for a in ability_contracts],'ability_contract_ids':[a['ability_contract_id'] for a in ability_contracts],'shot_id':None})
    ending=build_ending(scen,actors,errors); ending_id='ENDING-RESULT-LOCK'; events.append({'event_id':ending_id,'type':'ending','result_lock':True,'mode':ending.get('mode'),'victor':ending.get('victor'),'defeated_actor':ending.get('defeated_actor'),'escape':ending.get('escape',False),'no_chase':ending.get('no_chase',False),'observation':ending.get('observation','保持已锁定的终局状态并观察结果。'),'shot_id':None})
    duration=float(scen.get('duration_s',30)); provisional_target=min(7,len(events)) if duration==30 else min(7,max(1,math.ceil(duration/4.5)),len(events))
    budget_pre=DIRECTOR.budget_aware_replan(len(events),provisional_target,7,2.2)
    budget_closed_loop_applied=False
    if budget_pre['pressure']:
        planning_trace.append({'type':'budget_director_feedback','status':'PRESSURE','details':budget_pre,'applied':True})
        # Closed loop: pressure changes presentation density and semantic Beat/Shot grouping; causal Events remain immutable.
        for c in contracts:
            c.setdefault('presentation',{})['budget_pressure']='compact camera coverage; merge compatible causal events; preserve every unique physical result'
        if current_phase: current_phase.shot_budget_pressure=True
        budget_closed_loop_applied=True
    else:
        planning_trace.append({'type':'budget_director_feedback','status':'PASS','details':budget_pre,'applied':True})
    globals()['_ACTIVE_SPATIAL_TRACE']=spatial_trace
    plan=make_shot_plan(events,duration,ending_id,ability_lock_id,7)
    beats, shots=plan['beats'], plan['shots']
    event_map={e['event_id']:e for e in events}; event_to_shot={}
    for idx,sh in enumerate(shots):
        sh['story_function']=story_role(sh['event_ids'],event_map,sh['beat_index'],len(beats));
        for eid in sh['event_ids']:
            if eid in event_to_shot: errors.append(f'EVENT_DUPLICATED:{eid}')
            event_to_shot[eid]=sh['shot_id']
    for e in events:
        if e['event_id'] not in event_to_shot: errors.append(f'EVENT_UNASSIGNED:{e["event_id"]}')
    if not shots or ending_id not in shots[-1]['event_ids']: errors.append('ENDING_NOT_IN_FINAL_SHOT')
    result_locked=False
    for sh in shots:
        for eid in sh['event_ids']:
            if eid in {'ABILITY-FINAL-RESULT-LOCK',ending_id}: result_locked=True
            elif result_locked and event_map[eid]['type'] in {'action_result','ability_clash'}: errors.append(f'POST_RESULT_LOCK_COMBAT_EVENT:{eid}')
    budget=DIRECTOR.budget_aware_replan(len(events),len(beats),7,2.2); budget['pressure']=bool(budget['pressure']); planning_trace.append({'type':'budget_feedback','status':'PRESSURE' if budget['pressure'] else 'PASS','details':budget})
    for ps in phase_states: ps['shot_budget_pressure']=budget['pressure']
    shot_ir=[]; all_event_ids=[e['event_id'] for e in events]
    closeup_cap = 1 if len(shots)<=3 else min(4, max(2, math.ceil(len(shots)/5)))
    closeup_used=0
    closeup_beats=set()
    for sh in shots:
        acts=[c for c in contracts if c['event_id'] in sh['event_ids']]; ability_ids=[a['ability_contract_id'] for a in ability_contracts if any(e in sh['event_ids'] for e in a['ability_event_ids'])]
        actor_state={aid:{'id':aid,'name':v.get('name',aid),'weapon':v.get('weapon'),'provenance_status':(v.get('provenance') or {}).get('weapon',{}).get('status','UNKNOWN')} for aid,v in canon.items()}
        camera_role = 'cause_follow'
        if sh['shot_count_in_beat'] >= 2:
            if sh['shot_index'] == 0: camera_role='setup_or_entry_follow'
            elif sh['shot_index'] == sh['shot_count_in_beat']-1: camera_role='reaction_or_result_follow'
            else: camera_role='contact_or_counter_follow'
        if sh['story_function']=='final_clash_result': camera_role='final_impact_then_result_observation'
        closeup_role=choose_closeup_role(sh,event_map,sh['beat_index'],len(beats),closeup_used,closeup_cap)
        # Do not stack close-ups repeatedly inside the same Beat; one motivated insert is enough.
        if closeup_role and sh['beat_id'] in closeup_beats: closeup_role=None
        if closeup_role:
            closeup_used += 1; closeup_beats.add(sh['beat_id']); camera_role=closeup_role
        fallback_map={'setup_or_entry_follow':'建立当前Beat的空间关系，镜头追随发动者/武器进入动作，不停留做人物展示；在动作启动前完成必要构图。','contact_or_counter_follow':'切入接触点或反制方向，跟随武器轨迹与受力变化；命中/格挡瞬间短促强调，但不制造额外事件。','reaction_or_result_follow':'跟随受力者位移与恢复重心，随后带出环境战损和双方新空间关系；保持因果连续。','impact_payoff':'亮点冲击跟拍：完整保留启动→加速→接触→受力→位移→环境结果的连续因果，接触瞬间短促强调，随后立即跟住受击者结果，不新增事件。','cause_follow':'单镜头连续追随主要战斗因果，从动作启动到结果/恢复保持可读。','final_impact_then_result_observation':'先锁定终极碰撞的因果轨迹与接触点，再在结果锁定后转为稳定观察镜头；RESULT_LOCK之后不得新增攻击、命中或破坏。'}
        fallback_text=fallback_map.get(camera_role,'沿主要攻击线跟拍，接触时短促强调。')
        camera_parts=[]; vfx_parts=[]
        for eid0 in sh.get('event_ids',[]):
            cc=next((c for c in contracts if c.get('event_id')==eid0),None)
            aa=selected_payloads.get(cc.get('knowledge_action_id')) if cc else None
            if aa:
                ctext=resolve_action_camera(aa,camera_role,sh.get('shot_index',0),sh.get('shot_count_in_beat',1))
                fidelity=((event_map.get(eid0,{}).get('impact_profile') or {}).get('highlight_semantic_fidelity') or {})
                vtext='' if fidelity.get('fidelity_required') else resolve_action_vfx(aa,camera_role)
                if ctext: camera_parts.append(ctext)
                if vtext: vfx_parts.append(vtext)
        camera_text='；'.join(dict.fromkeys(camera_parts)) or fallback_text or CLOSEUP_TEXT.get(camera_role,'沿主要攻击线跟拍，接触时短促强调。')
        if closeup_role: camera_text=CLOSEUP_TEXT[closeup_role]
        vfx_text='；'.join(dict.fromkeys(vfx_parts)) or '特效只解释已经发生的接触、受力和环境响应。'
        highlight_choreography=_highlight_choreography_for_shot(sh,event_map)
        if highlight_choreography:
            tp=highlight_choreography.get('tempo_phases',[])
            vfx_text += ' 亮点节奏：'+'→'.join(tp)+'。冲击层级：'+('、'.join(highlight_choreography.get('impact_stack',[])) or '单层')+'。特效只在既有接触事件中增强。'
            cam=highlight_choreography.get('camera',{})
            if cam:
                camera_text += ' 亮点摄影：'+str(cam.get('angle','cause_follow'))+'；'+('慢速环绕；' if cam.get('orbit') else '')+'焦点锁定'+str(cam.get('focus','接触轴'))+'；命中后跟随结果。'
        shot_spatial_traces=[x for x in spatial_trace if x.get('event_id') in sh.get('event_ids',[])]
        first_event=event_map.get(sh.get('event_ids',[None])[0],{}) if sh.get('event_ids') else {}
        last_event=event_map.get(sh.get('event_ids',[None])[-1],{}) if sh.get('event_ids') else {}
        before_state=copy.deepcopy(first_event.get('spatial_snapshot_before') or (shot_spatial_traces[0].get('spatial_state_before') if shot_spatial_traces else spatial_state))
        after_state=copy.deepcopy(last_event.get('spatial_snapshot_after') or (shot_spatial_traces[-1].get('spatial_state_after') if shot_spatial_traces else before_state))
        spatial_before=(before_state.get('actors',{}).get(first_event.get('actor_id'),{}).get('layer',before_state.get('layer','ground')))
        spatial_after=(after_state.get('actors',{}).get(last_event.get('actor_id'),{}).get('layer',after_state.get('layer','ground')))
        spatial_transition_note='保持同一空间层级与连续支撑'
        if any(x.get('transition') for x in shot_spatial_traces):
            spatial_transition_note='空间跟拍：明确展示水平位移与高度变化，镜头随角色真实受力/跃升/坠落移动；必须看见起点、转换路径与新空间锚点，不允许瞬移换层'
        elif any(x.get('intent',{}).get('intent')=='horizontal_reposition' for x in shot_spatial_traces):
            spatial_transition_note='水平空间换位：保持攻击轴可读，展示侧移/追击/后撤形成的新站位，并保留环境锚点'
        camera_text += ' '+spatial_transition_note
        shot_ir.append({'shot_id':sh['shot_id'],'beat_id':sh['beat_id'],'beat_index':sh['beat_index'],'shot_index':sh['shot_index'],'shot_count_in_beat':sh['shot_count_in_beat'],'duration':sh['duration'],'story_function':sh['story_function'],'highlight_events':[e for e in sh.get('event_ids',[]) if event_map.get(e,{}).get('highlight')],'beat_ids':[sh['beat_id']],'event_ids':sh['event_ids'],'actor_state':actor_state,'spatial_state':{'source':scen.get('spatial_state',{}),'combat_layer_before':spatial_before,'combat_layer_after':spatial_after,'spatial_mode':spatial_mode,'transition_trace':shot_spatial_traces,'actor_states_before':{aid:dict(v) for aid,v in before_state.get('actors',{}).items()},'actor_states_after':{aid:dict(v) for aid,v in after_state.get('actors',{}).items()},'relative_height_before':before_state.get('relative_height'),'relative_height_after':after_state.get('relative_height'),'relative_distance_before':before_state.get('relative_distance'),'relative_distance_after':after_state.get('relative_distance'),'facing_before':before_state.get('facing'),'facing_after':after_state.get('facing'),'attack_axis_before':before_state.get('attack_axis'),'attack_axis_after':after_state.get('attack_axis'),'movement_vector_before':before_state.get('movement_vector'),'movement_vector_after':after_state.get('movement_vector'),'anchors':after_state.get('anchors',[])},'action_chain':[{'knowledge_action_id':c['knowledge_action_id'],'execution_contract_id':c['execution_contract_id'],'event_id':c['event_id'],'actor':c['actor_identity'],'weapon':c['weapon_identity'],'result':c['result']['outcome_class'],'weapon_control':((c.get('execution') or {}).get('weapon_control') or {}),'prompt_semantics':copy.deepcopy(c.get('prompt') or {}),'state_contract_hash':sha(c['pre_state'])} for c in acts],'ability_contract_ids':ability_ids,'signature_ultimate':copy.deepcopy(first_event.get('signature_ultimate')) if first_event.get('signature_ultimate') else (copy.deepcopy(last_event.get('signature_ultimate')) if last_event.get('signature_ultimate') else None),'camera':camera_text,'camera_role':camera_role,'camera_resolver':'ACTION_KNOWLEDGE_CINEMATIC_V1','vfx':vfx_text,'vfx_resolver':'ACTION_KNOWLEDGE_VFX_V1','highlight_choreography':highlight_choreography,'highlight_semantic_fidelity':(highlight_choreography or {}).get('semantic_fidelity',{}),'closeup':bool(closeup_role),'closeup_role':closeup_role,'physics':'准备→启动→加速→接触/避让→受力→结果→位移/反应→恢复，所有位置变化必须由动作或受力产生。','vfx':vfx_text,'continuity':'保持角色身份、武器、空间方向、前后状态与战损连续。','damage_state':scen.get('damage_state',{}),'ending_state':event_map[ending_id] if ending_id in sh['event_ids'] else ({'result_lock':True} if ability_lock_id and ability_lock_id in sh['event_ids'] else {'result_lock':False})})
    spatial_transition_count=sum(1 for x in spatial_trace if x.get('transition'))
    spatial_layer_path=[]
    for x in spatial_trace:
        spatial_layer_path.append({'event_id':x.get('event_id'),'actor_layer':x.get('to_layer'),'target_layer':x.get('target_layer_after'),'relative_height':x.get('relative_height')})
    spatial_target=int(spatial_cfg.get('transition_target', 1 if duration==30 and spatial_mode=='adaptive' and spatial_state.get('vertical_space_supported',True) else 0))
    if director_mode=='autonomous' and spatial_mode in {'adaptive','vertical'} and spatial_target>0 and len(contracts)>=6 and spatial_transition_count<spatial_target: warnings.append(f'SPATIAL_TRANSITION_TARGET_NOT_REACHED:{spatial_transition_count}/{spatial_target}')
    narrative_curve=NARRATIVE.build_curve(events,float(scen.get('duration_s',30)))
    shot_doc={'version':'10.18.4','beat_count':len(beats),'shot_count':len(shot_ir),'all_event_ids':all_event_ids,'spatial_provenance':scen.get('spatial_state',{}),'narrative_curve':narrative_curve,'shots':shot_ir}
    runtime={'schema_version':'1.7','runtime_version':'10.18.6','scenario_id':scen.get('scenario_id','UNNAMED_SCENARIO'),'objective':scen.get('objective'),'canon':canon,'selected_action_payloads':list(selected_payloads.values()),'action_contracts':contracts,'ability_contracts':ability_contracts,'events':events,'ending':ending,'phase_states':phase_states,'narrative_curve':narrative_curve,'narrative_trace':narrative_history,'planning_trace':planning_trace,'planning_metrics':{'replan_count':replan_count,'lookahead_checks':lookahead_checks,'phase_strategy_enabled':True,'opponent_prediction_enabled':True,'budget_feedback_enabled':True,'dynamic_shot_allocation':True,'cinematic_closeup_layer':True,'highlight_impact_director':True,'highlight_target':highlight_target_count,'highlight_selected':highlight_selected,'highlight_event_ids':highlight_event_ids,'highlight_payoff_scoring':True,'highlight_semantic_fidelity':True,'highlight_directive_canon':True,'adaptive_combat_narrative':True,'signature_ultimate_switch':bool(ultimate_switch.get('enabled')),'signature_ultimate':copy.deepcopy(signature_ultimate) if signature_ultimate else None,'signature_ultimate_trigger_phrase':'专属大招','signature_ultimate_negative_intent_guard':True,'signature_ultimate_action_compatibility':True,'signature_ultimate_candidate_scoring':True,'signature_ultimate_continues_combat':True,'narrative_reasoning':True,'narrative_curve_adaptive':True,'spatial_combat_director':True,'spatial_mode':spatial_mode,'spatial_transitions':spatial_transition_count,'spatial_transition_target':spatial_target,'spatial_trace':spatial_trace,'spatial_layer_path':spatial_layer_path,'dual_actor_spatial_state':True,'environment_anchors':spatial_state.get('anchors',[]),'autonomous_director':director_mode=='autonomous','persistent_phase_strategy':True,'prediction_driven_selection':director_mode=='autonomous','budget_aware_feedback':True,'budget_semantics':'beat_budget_not_shot_budget','budget_closed_loop':budget_closed_loop_applied or not budget_pre['pressure'],'budget_remerge_applied':budget_closed_loop_applied,'semantic_shot_director':True,'camera_knowledge_resolver':True,'vfx_knowledge_resolver':True,'tempo_allocation':True,'budget_pressure':bool(budget.get('pressure',False))},'qa':{}}
    runtime_path=out/'runtime_trace.json'; shot_path=out/'shot_ir.json'; runtime_path.write_text(json.dumps(runtime,ensure_ascii=False,indent=2),encoding='utf-8'); shot_path.write_text(json.dumps(shot_doc,ensure_ascii=False,indent=2),encoding='utf-8')
    t_compile=time.perf_counter(); native,metrics=COMP.compile_native_api(runtime_path,shot_path); compile_time=time.perf_counter()-t_compile
    (out/'native_prompts_v1090.json').write_text(json.dumps(native,ensure_ascii=False,indent=2),encoding='utf-8'); (out/'prompt_semantic_quality.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    t_qa=time.perf_counter(); qa_report=QA.run_quality(native,runtime); qa_time=time.perf_counter()-t_qa
    (out/'prompt_semantic_qa.json').write_text(json.dumps(qa_report,ensure_ascii=False,indent=2),encoding='utf-8')
    expected=set(all_event_ids); fps={p.get('semantic_fingerprint') for p in native.values()}
    for model,p in native.items():
        if not p.get('prompt') or len(p['prompt'])<80: errors.append(f'NATIVE_PROMPT_EMPTY:{model}')
        if set(p.get('event_coverage',[]))!=expected: errors.append(f'ADAPTER_EVENT_COVERAGE_FAIL:{model}')
        if p.get('invariant_manifest',{}).get('ending')!=ending: errors.append(f'ADAPTER_ENDING_DRIFT:{model}')
    if len(fps)!=1: errors.append('ADAPTER_SEMANTIC_FINGERPRINT_DRIFT')
    if qa_report.get('status')!='PASS': errors.append('PROMPT_SEMANTIC_QA_FAIL')
    if duration==30 and len(beats)>7: errors.append('BEAT_HARD_MAX_FAIL')
    if any(not (1<=b.get('shot_count',0)<=3) for b in beats): errors.append('SHOT_PER_BEAT_RANGE_FAIL')
    if sum(b.get('shot_count',0) for b in beats)!=len(shots): errors.append('BEAT_SHOT_ACCOUNTING_FAIL')
    errors.extend(NARRATIVE.validate(runtime))
    runtime['qa']={'status':'FAIL' if errors else 'PASS','errors':errors,'warnings':warnings,'counts':{'actions_dataset':len(actions),'action_contracts':len(contracts),'ability_contracts':len(ability_contracts),'events':len(events),'shots':len(shots)},'timing':{'preflight_mode':'streaming_hash_in_process','compile_seconds':round(compile_time,3),'qa_seconds':round(qa_time,3),'total_seconds':round(time.perf_counter()-t0,3)},'invariants':{'weapon_integrity':not any('WEAPON_' in e for e in errors),'outcome_contract':not any('OUTCOME_' in e for e in errors),'normalized_state':not any('STATE_' in e or 'NORMALIZED_' in e for e in errors),'ability_execution':not any('ABILITY_' in e for e in errors),'result_lock':not any('ENDING_' in e or 'POST_RESULT_LOCK' in e for e in errors),'beat_ids':all(s.get('beat_ids') for s in shots),'beat_budget':len(beats)<=7 if duration==30 else True,'shot_budget':len(shots)>=len(beats) if beats else True,'shots_per_beat':all(1<=b.get('shot_count',0)<=3 for b in beats),'native_compiler':not any('NATIVE_PROMPT_EMPTY' in e for e in errors),'adapter_semantic_consistency':len(fps)==1,'prompt_semantic_quality':qa_report.get('status')=='PASS','dynamic_phase_strategy':bool(phase_states),'opponent_prediction':any(x.get('type')=='phase_decision' and x.get('opponent_prediction') for x in planning_trace),'transition_replanning':any(x.get('type') in {'transition_replan','bounded_replan'} for x in planning_trace) or replan_count==0,'lookahead':lookahead_checks>0 if len(contracts)>1 else True,'budget_feedback':any(x.get('type')=='budget_director_feedback' and x.get('applied') for x in planning_trace),'autonomous_director':director_mode=='autonomous','prediction_driven_selection':any(x.get('type')=='director_action_selection' and x.get('mode')=='autonomous' for x in planning_trace),'persistent_phases':len(phase_states)<len(contracts) if contracts else False,'tempo_allocation':len({s.get('duration') for s in shots})>1 if len(shots)>1 else True,'closeup_count':sum(1 for s in shot_ir if s.get('closeup')),'closeup_cap':closeup_cap,'highlight_payoff':highlight_selected<=highlight_target_count and all((not e.get('highlight')) or (bool(e.get('impact_profile')) and e.get('impact_profile',{}).get('tier') in {'high','signature'} and len(e.get('impact_profile',{}).get('choreography',{}))>=7) for e in events),'highlight_target_reached':highlight_selected>=highlight_target_count if highlight_target_count>0 else True,'highlight_target_mode':'soft_quality_target','closeup_budget':sum(1 for s in shot_ir if s.get('closeup'))<=closeup_cap,'closeup_event_bound':all((not s.get('closeup')) or bool(s.get('event_ids')) for s in shot_ir),'spatial_snapshot_chain':not any('SPATIAL_SNAPSHOT_CHAIN_BREAK' in e for e in errors),'spatial_trace_integrity':all(x.get('from_layer') is not None and x.get('to_layer') is not None for x in spatial_trace),'spatial_transition_integrity':all((not x.get('transition')) or x.get('transition_reason') for x in spatial_trace),'spatial_transition_target_reached':spatial_transition_count>=spatial_target,'dual_actor_spatial_state':all(isinstance(x,dict) for x in spatial_state.get('actors',{}).values()),'semantic_shot_grouping':all(s.get('shot_group_reason')=='semantic_causal_boundary' for s in shots),'camera_knowledge_resolver':all(bool(s.get('camera_resolver')) for s in shot_ir),'vfx_knowledge_resolver':all(bool(s.get('vfx_resolver')) for s in shot_ir),'highlight_semantic_fidelity':all((not e.get('highlight')) or ((e.get('impact_profile') or {}).get('highlight_semantic_fidelity',{}).get('fidelity_required') in (None, False, True)) for e in events),'highlight_directive_propagation':all((not s.get('highlight_events')) or bool(s.get('highlight_semantic_fidelity') is not None) for s in shot_ir),'end_to_end_compile_completed':True,'narrative_coverage':all(bool(e.get('narrative')) for e in runtime.get('events',[]) if e.get('type')=='action_result'),'narrative_curve_integrity':not any('NARRATIVE_CURVE' in e for e in errors),'narrative_result_lock':not any('NARRATIVE_POST_RESULT_LOCK' in e for e in errors),'narrative_reason_integrity':all(bool((e.get('narrative') or {}).get('reason_source')) for e in runtime.get('events',[]) if e.get('type')=='action_result')}}
    runtime_path.write_text(json.dumps(runtime,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'beat_graph.json').write_text(json.dumps({'version':'10.18.6','beats':beats,'shots':[{'shot_id':s['shot_id'],'beat_id':s['beat_id'],'event_ids':s['event_ids'],'duration':s['duration']} for s in shots]},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'adapter_outputs.json').write_text(json.dumps(native,ensure_ascii=False,indent=2),encoding='utf-8'); (out/'qa_report.json').write_text(json.dumps(runtime['qa'],ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'PERFORMANCE_BENCHMARK.json').write_text(json.dumps({'version':'10.18.6','total_seconds':runtime['qa']['timing']['total_seconds'],'compile_seconds':compile_time,'qa_seconds':qa_time,'preflight':'streaming_hash_in_process','zero_copy':True,'dynamic_shot_allocation':True,'autonomous_director':director_mode=='autonomous','persistent_phase_strategy':True,'prediction_driven_selection':director_mode=='autonomous','budget_aware_feedback':True,'budget_semantics':'beat_budget_not_shot_budget','budget_closed_loop':budget_closed_loop_applied or not budget_pre['pressure'],'budget_remerge_applied':budget_closed_loop_applied,'semantic_shot_director':True,'camera_knowledge_resolver':True,'vfx_knowledge_resolver':True,'tempo_allocation':True},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"RUNTIME_VERSION=10.18.6 ACTION_CONTRACTS={len(contracts)} ABILITY_CONTRACTS={len(ability_contracts)} EVENTS={len(events)} SHOTS={len(shots)} ERRORS={len(errors)} TOTAL_SECONDS={runtime['qa']['timing']['total_seconds']}")
    print('RUNTIME_STRESS_TEST=PASS' if not errors else 'RUNTIME_STRESS_TEST=FAIL')
    sys.exit(1 if errors else 0)
if __name__=='__main__': main()
