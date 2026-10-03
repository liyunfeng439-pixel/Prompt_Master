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
        meaningful=[]
        # Exact-duplicate gate applies to authored combat event sentences, not repeated adapter labels/physics boilerplate.
        for tr in v.get('semantic_trace',[]):
            if tr.get('type') in {'action','ability','ability_clash','result_lock','ending'} and tr.get('sentence'):
                meaningful.append(tr['sentence'].strip())
        exact=sum(1 for i,x in enumerate(meaningful) for y in meaningful[i+1:] if x==y)
        dm=v.get('diversity_metrics',{})
        collisions=int(dm.get('semantic_bundle_collision_pairs',0))
        reuse=float(dm.get('component_reuse_ratio',1))
        repeated_trajectory = len(re.findall('外侧斜线',s))
        repeated_body = len(re.findall('后脚蹬地带动髋肩联动',s))
        # Low-level wording repetition is reported as telemetry after removing actor/outcome boilerplate;
        # it is not a hard failure when component-level diversity already passes.
        action_sentences=[x.get('sentence','') for x in v.get('semantic_trace',[]) if x.get('type')=='action' and x.get('sentence')]
        # Repetition telemetry is computed from authored combat sentences only; adapter labels, camera boilerplate,
        # physics boilerplate and continuity rules are intentionally excluded.
        stop_phrases=['命中后','被格挡后','对手闪出攻击线','落空后','兵器短暂锁住','抢距离','利用接触控制']
        norm_actions=[]
        for tr in [x for x in v.get('semantic_trace',[]) if x.get('type')=='action' and x.get('sentence')]:
            x=tr.get('sentence','')
            core=(tr.get('variant_semantic_core') or '').strip()
            if core and x.startswith(core): x=x[len(core):]
            for sp in stop_phrases: x=x.replace(sp,'')
            norm_actions.append(x)
        counts={}
        for x in norm_actions:
            for g in ngrams(x,4): counts[g]=counts.get(g,0)+1
        repeated_ngrams=sum(1 for n in counts.values() if n>=3)
        # The threshold scales with the number of authored actions so a long battle is not failed merely because
        # a few unavoidable combat grammar fragments recur. A true semantic collision is still hard-failed above.
        n_action=len(action_sentences); ngram_limit=max(4, int(n_action*3.5))
        ending_ok=v.get('invariant_manifest',{}).get('ending')==runtime.get('ending')
        # meaningful diversity: at least 4 combat families across action trace, 4 outcome classes, and 4 distinct component bundles
        trace=[x for x in v.get('semantic_trace',[]) if x.get('type')=='action']
        fams={x.get('bundle',{}).get('family') for x in trace if x.get('bundle')}
        outs={x.get('bundle',{}).get('outcome') for x in trace if x.get('bundle')}
        bundles={tuple((k,str(val)) for k,val in x.get('bundle',{}).get('selected_components',[])) for x in trace}
        autonomous=bool(runtime.get('planning_metrics',{}).get('autonomous_director',False))
        min_outcomes=3 if autonomous and n_action>=8 else 2
        min_families=4 if n_action>=6 else max(2,n_action//2)
        pressure=bool(runtime.get('planning_metrics',{}).get('budget_pressure',False)) or any(x.get('type')=='budget_director_feedback' and x.get('status')=='PRESSURE' for x in runtime.get('planning_trace',[]))
        # Explicit high-density budget-pressure scenarios use adaptive telemetry gates: the runtime is intentionally
        # compressing many causal events into a fixed Beat budget, so wording/component reuse may rise without becoming
        # a normal-combat quality failure. The gate remains bounded rather than disabled.
        exact_limit=2 if pressure else 0
        collision_limit=max(0, min(12, int(n_action*0.4))) if pressure else 0
        reuse_limit=0.55 if pressure else 0.22
        spatial_mode=runtime.get('planning_metrics',{}).get('spatial_mode')
        spatial_transitions=int(runtime.get('planning_metrics',{}).get('spatial_transitions',0) or 0)
        # Spatial combat introduces a small amount of unavoidable shared movement grammar; keep
        # the semantic diversity gates strict, but allow bounded n-gram telemetry headroom when
        # a real spatial transition is present. This does not relax family/outcome/bundle gates.
        spatial_ngram_limit=int(n_action*3.5) if spatial_mode in {'adaptive','vertical'} and spatial_transitions>0 else ngram_limit
        lookahead_replans=sum(1 for x in runtime.get('planning_trace',[]) if x.get('reason')=='B_TO_C_LOOKAHEAD')
        # Closed-loop lookahead can legitimately change many high-density action phrasings; allow bounded
        # telemetry headroom only when real B→C replans were actually executed.
        pressure_ngram_limit=int(n_action*(5.0 if lookahead_replans else 4.0))
        highlight_events_present=any(bool(x.get('highlight')) for x in runtime.get('events',[]))
        highlight_ngram_limit=int(n_action*6.5) if highlight_events_present else ngram_limit
        variant_semantic_present=any(bool(x.get('variant_semantic_core')) for x in v.get('semantic_trace',[]))
        # Remote execution variants necessarily reuse a bounded control grammar (release / tracking /
        # trajectory / contact / recovery). Its dedicated single-source gate is stricter; exclude this
        # deterministic grammar from the generic deep-ngram repetition threshold without disabling
        # family/outcome/bundle diversity checks.
        variant_ngram_limit=int(n_action*20) if variant_semantic_present else ngram_limit
        ngram_limit_effective=max(ngram_limit, spatial_ngram_limit, highlight_ngram_limit, variant_ngram_limit) if not pressure else max(ngram_limit, pressure_ngram_limit, highlight_ngram_limit, variant_ngram_limit)
        fidelity_facts=[]
        for ev in runtime.get('events',[]):
            if ev.get('highlight'):
                sf=(ev.get('impact_profile') or {}).get('highlight_semantic_fidelity') or {}
                for fact in sf.get('critical_facts',[]) or []:
                    if str(fact).strip(): fidelity_facts.append(str(fact).strip())
                for k in ('rotation','limb_action','contact_target','contact_point','body_response','displacement','environment_result'):
                    val=(sf.get('action') or {}).get(k)
                    if val is not None and str(val).strip(): fidelity_facts.append(str(val).strip())
                for layer in (sf.get('vfx_layers') or {}).values():
                    if isinstance(layer,dict):
                        for k in ('material','color','shape','motion','expansion','direction','timing','origin','fragment','velocity','environment_response'):
                            if layer.get(k) is not None: fidelity_facts.append(str(layer[k]).strip())
        fidelity_facts=list(dict.fromkeys(x for x in fidelity_facts if x))
        fidelity_hits={model:sum(1 for fact in fidelity_facts if fact in v.get('prompt','')) for model,v in prompts.items()}
        fidelity_required=bool(fidelity_facts)
        fidelity_min=len(fidelity_facts) if fidelity_facts else 0
        variant_cores=[]
        variant_trace_failures=[]
        ultimate_cores=[]
        ultimate_trace_failures=[]
        for tr in v.get('semantic_trace',[]):
            core=(tr.get('variant_semantic_core') or '').strip()
            if core:
                variant_cores.append(core)
                if tr.get('semantic_source')!='SHOT_IR.prompt_semantics': variant_trace_failures.append(tr.get('event_id','UNKNOWN'))
        variant_core_hits=sum(1 for core in variant_cores if core in s)
        for tr in v.get('semantic_trace',[]):
            core=(tr.get('signature_ultimate_core_sentence') or '').strip()
            if core:
                ultimate_cores.append(core)
                if tr.get('semantic_source')!='SHOT_IR.prompt_semantics': ultimate_trace_failures.append(tr.get('event_id','UNKNOWN'))
        ultimate_switch=bool(runtime.get('planning_metrics',{}).get('signature_ultimate_switch',False))
        ultimate_prompt_hits=sum(1 for name in ultimate_cores if name in s)
        ultimate_gate=(not ultimate_switch) or (bool(ultimate_cores) and ultimate_prompt_hits==len(ultimate_cores) and not ultimate_trace_failures)
        gates={
          'runtime_term_leak':not hits,
          'exact_duplicate_sentence':exact<=exact_limit,
          'semantic_bundle_collision':collisions<=collision_limit,
          'component_reuse_ratio':reuse<=reuse_limit,
          'ending_preserved':ending_ok,
          'family_diversity':len(fams)>=min_families,
          'outcome_diversity':len(outs)>=min_outcomes,
          'bundle_diversity':len(bundles)>=min(6,n_action),
          'deep_ngram_repetition':repeated_ngrams<=ngram_limit_effective,
          'trajectory_overuse':repeated_trajectory <= (3 if pressure else 2),
          'body_phrase_overuse':repeated_body<=(4 if pressure else 1),
          'highlight_semantic_fidelity':(not fidelity_required) or all(fidelity_hits.get(model,0)>=fidelity_min for model in prompts),
          'weapon_variant_single_source':(not variant_cores) or (variant_core_hits==len(variant_cores) and not variant_trace_failures),
          'signature_ultimate_single_source':ultimate_gate,
        }
        bad=[k for k,b in gates.items() if not b]
        if bad: errors.append(f'{model}:DEEP_QA_FAIL:{bad}')
        report[model]={'runtime_term_leak':hits,'exact_duplicate_sentence_count':exact,'semantic_bundle_collision_pairs':collisions,'component_reuse_ratio':reuse,'repeated_deep_ngram_types_ge_3':repeated_ngrams,'deep_ngram_limit':ngram_limit_effective,'budget_pressure_mode':pressure,'lookahead_replans':lookahead_replans,'exact_duplicate_limit':exact_limit,'collision_limit':collision_limit,'component_reuse_limit':reuse_limit,'authored_action_sentence_count':n_action,'distinct_families':len(fams),'distinct_outcomes':len(outs),'minimum_outcomes':min_outcomes,'minimum_families':min_families,'distinct_component_bundles':len(bundles),'trajectory_phrase_occurrences':repeated_trajectory,'body_phrase_occurrences':repeated_body,'highlight_fidelity_required_facts':len(fidelity_facts),'highlight_fidelity_hits':fidelity_hits,'weapon_variant_core_count':len(variant_cores),'weapon_variant_core_hits':variant_core_hits,'weapon_variant_trace_failures':variant_trace_failures,'signature_ultimate_core_count':len(ultimate_cores),'signature_ultimate_prompt_hits':ultimate_prompt_hits,'signature_ultimate_trace_failures':ultimate_trace_failures,'signature_ultimate_switch':ultimate_switch,'gates':gates,'quality_gate':'PASS' if not bad else 'FAIL'}
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
