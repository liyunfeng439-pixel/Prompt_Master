#!/usr/bin/env python3
import argparse,json,hashlib,re,sys,importlib.util
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
engine_path=ROOT/'43_COMBAT_SEMANTIC_DIVERSITY_ENGINE_V1.0/semantic_diversity_engine_v1020.py'
spec=importlib.util.spec_from_file_location('sde',engine_path); sde=importlib.util.module_from_spec(spec); spec.loader.exec_module(sde)

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]

def action_map(runtime):
    payloads=runtime.get('selected_action_payloads') or runtime.get('_actions_cache') or []
    if isinstance(payloads,dict): return payloads
    return {a['action_id']:a for a in payloads}

def actor_registry(canon, shot_ir):
    actors={}
    for aid,v in canon.items():
        if isinstance(v,dict): actors[aid]=v
    for sh in shot_ir.get('shots',[]):
        for aid,v in (sh.get('actor_state') or {}).items():
            if aid not in actors: actors[aid]=v
    return actors

def identity_text(canon, shot_ir):
    actors=actor_registry(canon,shot_ir); parts=[]
    for aid,v in actors.items():
        name=v.get('name',aid); weapon=v.get('weapon') or '其锁定武器'
        parts.append(f'{name}保持参考资产身份与外观连续，始终使用{weapon}。')
    return ''.join(parts) or '保持所有角色参考资产身份、外观与武器连续。'

def scene_text(shot_ir,runtime):
    spatial=shot_ir.get('spatial_provenance') or {}
    note=spatial.get('note','') if isinstance(spatial,dict) else ''
    return '保持用户确认的战斗场景与空间关系连续；所有位置变化必须由动作、受力或明确位移产生。' + (f' {note}' if note and 'not canonized' not in note.lower() else '')

def names_for_ids(ids, canon):
    actors=actor_registry(canon,{'shots':[]}); names=[]
    for aid in ids or []:
        if aid in actors: names.append(actors[aid].get('name',aid))
    return names

def ability_sentence(ac,canon,event_id):
    aid=ac.get('actor_identity'); actors=actor_registry(canon,{'shots':[]}); actor=actors.get(aid,{}).get('name',aid or '角色'); weapon=actors.get(aid,{}).get('weapon') or '武器'; visual=ac.get('visual_profile') or '能力形态'; sem=ac.get('execution_contract_v2') or {}
    if event_id.endswith('ACTIVATION'): return f'{actor}骤然提气，力量收拢到身体主轴，{visual}从蓄势中启动。'
    if event_id.endswith('MANIFEST'): return f'{visual}沿{sem.get("body_line","本体动作轴")}成形，与{actor}保持同向运动。'
    if event_id.endswith('WEAPON-SYNC'): return f'{actor}带动{weapon}进入攻击线，{visual}与真实武器动作同步。'
    if event_id.endswith('CLASH'): return f'{actor}推动{visual}完成一次{sem.get("primary_interaction","正面交锋")}，结果沿真实攻击轴传递。'
    return ''

def fallback_camera(role):
    return {'combat_open':'近跟并锁定首次有效接触，迅速建立双方间距。','counter_exchange':'横移跟随攻击线变化，保留闪避与反击方向。','pressure_shift':'绕侧跟拍，突出控制、换线与攻守转换。','high_intensity_exchange':'低机位快速跟进，连续接触与受击反应保持可读。','escalation':'先拉开空间交代升级，再追入能量与环境反馈。','final_build':'压近蓄力动作后后撤容纳完整终局形态。','final_clash_result':'完整观察最终接触、结果与结束后的稳定状态。'}.get(role,'沿主要攻击线跟拍，接触时短促强调，恢复时回到人物重心。')
def fallback_vfx(role):
    return {'combat_open':'特效只强调首次接触产生的火花、气流或材质反馈。','counter_exchange':'残影服从变线与惯性，不遮挡武器接触。','pressure_shift':'受力方向推动气流、尘雾或能量反馈。','high_intensity_exchange':'冲击特效只在接触瞬间增强，保留身体与武器可读性。','escalation':'能量与环境反馈随动作轴同步升级。','final_build':'终局能量由本体蓄力产生并与真实动作同步。','final_clash_result':'最终冲击产生可见结果，随后特效衰减进入结果观察。'}.get(role,'特效只解释已经发生的接触、受力和环境响应。')

def event_sentence(event, runtime, canon):
    typ=event.get('type',''); actors=actor_registry(canon,{'shots':[]})
    if typ=='recovery':
        aid=event.get('actor_id'); name=actors.get(aid,{}).get('name',aid or '角色'); return f'{name}顺着前一动作的惯性完成恢复，重新建立支撑与下一条攻击线。'
    if typ=='result_lock': return '最终碰撞结果被锁定，身体、武器与环境进入稳定的结果状态，不再产生新的攻击事件。'
    if typ=='ending':
        d=actors.get(event.get('defeated_actor'),{}).get('name',event.get('defeated_actor','败者')); v=actors.get(event.get('victor'),{}).get('name',event.get('victor','胜者'))
        if event.get('escape') and event.get('no_chase'): return f'{d}脱离战场，{v}停止追击并保持终局状态。'
        return f'{v}保持已锁定的终局优势，{d}保持已锁定的失败状态。'
    if typ=='ability_clash':
        ns=names_for_ids(event.get('actor_ids',[]),canon); return f'{"与".join(ns) if ns else "双方"}的终局能力沿各自真实攻击轴发生最终接触，力量集中于接触点释放。'
    return ''

def render_action(a,actor_name,seq_usage,shot_usage,freq,role):
    sentence,bundle=sde.compile_action(a,actor_name,seq_usage,shot_usage,{k:Counter(v) for k,v in freq.items()},role,None)
    return sentence,bundle

def compile(runtime,shot_ir):
    canon=runtime.get('canon',{}); acts=action_map(runtime); contracts={c.get('event_id'):c for c in runtime.get('action_contracts',[]) if c.get('event_id')}; abilities=runtime.get('ability_contracts',[]); events={e.get('event_id'):e for e in runtime.get('events',[])}
    common='8K电影级3D CG写实，次世代PBR物理材质，UE5级电影渲染，16:9横画幅，60fps，HDR，真实全局光照与体积光，电影级景深与自然运动模糊，人物、衣物、毛发、武器材质保持高精度与真实重量、惯性、受力反馈。'
    identity=identity_text(canon,shot_ir); scene=scene_text(shot_ir,runtime)
    outputs={}; metrics={}
    idx=runtime.get('_semantic_freq',{})
    for model in ('universal','seedance_2_5','minimax_h3'):
        seq_usage={'family':Counter(),'tactical':Counter(),'components':Counter(),'outcome':Counter()}; chosen=[]; trace=[]; shot_records=[]
        shot_blocks=[]
        for sh in shot_ir.get('shots',[]):
            clauses=[]; local={'family':Counter(),'tactical_tail':[],'components':Counter(),'outcome':Counter()}
            for eid in sh.get('event_ids',[]):
                c=contracts.get(eid)
                if c and c.get('knowledge_action_id') in acts:
                    a=acts[c['knowledge_action_id']]; actor_id=c.get('actor_identity'); actor=actor_registry(canon,shot_ir).get(actor_id,{})
                    sentence,bundle=render_action(a,actor.get('name',actor_id or '角色'),seq_usage,local,idx,sh.get('story_function','combat_execution'))
                    clauses.append(sentence); chosen.append({'shot_id':sh['shot_id'],'event_id':eid,**bundle}); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'action','sentence':sentence,'story_role':sh.get('story_function'),'bundle':bundle}); continue
                found=False
                for ac in abilities:
                    if eid in ac.get('ability_event_ids',[]):
                        txt=ability_sentence(ac,canon,eid)
                        if txt: clauses.append(txt); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'ability'}); found=True; break
                if found: continue
                txt=event_sentence(events.get(eid,{'event_id':eid}),runtime,canon)
                if txt: clauses.append(txt); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':events.get(eid,{}).get('type','event')})
            uniq=[]
            for cl in clauses:
                if not any(sde.sem_sim(cl,u,0.86) for u in uniq): uniq.append(cl)
            txt=' '.join(uniq)
            camera=sh.get('camera') or fallback_camera(sh.get('story_function',''))
            physics=sh.get('physics') or '遵循准备→启动→加速→接触/避让→受力→结果→恢复的连续物理链。'
            vfx=sh.get('vfx') or fallback_vfx(sh.get('story_function',''))
            continuity=sh.get('continuity') or '保持角色身份、武器、空间方向、战损与前后状态连续。'
            damage=sh.get('damage_state') or {}
            shot_records.append({'shot_id':sh['shot_id'],'duration':sh.get('duration',0),'story_function':sh.get('story_function',''),'text':txt,'camera':camera,'physics':physics,'vfx':vfx,'continuity':continuity,'damage':damage,'ending':sh.get('ending_state',{})})
        final=runtime.get('ending',{})
        actors=actor_registry(canon,shot_ir); actor_lines=[]
        for aid,v in actors.items(): actor_lines.append(f'- {v.get("name",aid)}：保持参考资产身份与{v.get("weapon") or "锁定武器"}一致')
        shot_lines=[]
        for s in shot_records:
            action_text=s['text'] or '延续上一状态并进入下一有效战斗因果。'
            shot_lines.append((s,action_text))
        if model=='universal':
            lines=['Generation Goal: 以战斗因果为主体，30秒默认控制在不超过7个Final Shot，连续事件优先于展示。','Global Visual Direction: '+common,'Asset Lock: '+identity,'Scene / Spatial Continuity: '+scene,'Time / Shot Sequence:']
            for s,t in shot_lines: lines.append(f'{s["shot_id"]}（{s["duration"]}秒）[{s["story_function"]}]：{t} 镜头：{s["camera"]} 物理：{s["physics"]} 特效：{s["vfx"]} 连续性：{s["continuity"]}')
            lines += ['Continuity / Damage: '+json.dumps({s['shot_id']:s['damage'] for s in shot_records},ensure_ascii=False,separators=(',',':')),'Ending State: 结果锁定后只观察已发生结果，不新增攻击、命中或破坏。','Negative Constraints: 不站桩、不摆POSE、不瞬移、不无因果换位、不复制或替换武器、不延迟无因果破坏、不用镜头切换掩盖非法动作。']
        elif model=='seedance_2_5':
            lines=['Reference / Asset Lock:\n'+identity,'Creative Brief:\n战斗优先；首个有效战斗事件尽快发生；每个Shot保持单一连续可执行的因果单元；子Beat留在所属Shot内，不自动拆Shot。','Global Visual Direction:\n'+common+' '+scene,'Timeline / Shot Sequence:']
            for s,t in shot_lines: lines.append(f'{s["shot_id"]} | {s["duration"]}s | {s["story_function"]}\nMotion Continuity: {t}\nCamera Motivation: {s["camera"]}\nPhysics and VFX: {s["physics"]} {s["vfx"]}\nContinuity: {s["continuity"]}')
            lines += ['Ending State:\n'+('胜者：'+actors.get(final.get('victor'),{}).get('name',str(final.get('victor','')))+'；败者：'+actors.get(final.get('defeated_actor'),{}).get('name',str(final.get('defeated_actor',''))) if final else '保持已锁定终局状态。'),'Negative Constraints:\nNo identity drift, no weapon duplication/replacement, no teleportation, no causality-free destruction, no post-result-lock combat.']
        else:
            lines=['Scene:\n'+scene,'Characters / Asset Lock:\n'+'\n'.join(actor_lines),'Combat Objective:\n以战术因果解决当前问题并逐步升级，不以单纯爆炸规模代替战斗强度。','Action Sequence by Time:']
            for s,t in shot_lines: lines.append(f'【{s["shot_id"]} {s["duration"]}s】\nAction: {t}\nCamera: {s["camera"]}\nPhysics: {s["physics"]}\nEnvironment/VFX: {s["vfx"]}\nConsistency: {s["continuity"]}')
            lines += ['Ending State:\n结果锁定后停止新增战斗事件；只观察已锁定结果与结束状态。','Negative Constraints:\nNo static showcase opening, no impossible transitions, no weapon changes, no identity drift, no delayed impact without cause, no new attack after result lock.']
        prompt='\n'.join(lines)
        m=sde.dedup_component_metrics(chosen)
        sentences=[x for x in re.split(r'[。\n]',prompt) if x.strip()]; exact=sum(1 for i,a in enumerate(sentences) for b in sentences[i+1:] if a==b)
        runtime_hits=[w for w in ['transition_contract','execution_contract','result_lock','INFERRED','FACT','NORMALIZED','knowledge_action_id','execution_model','opponent_response','state_contract','SHOT_IR','CANON','provenance','semantic_fingerprint'] if w in prompt]
        trace_actions=[x for x in trace if x.get('type')=='action']; fams={x.get('bundle',{}).get('family') for x in trace_actions if x.get('bundle')}; outs={x.get('bundle',{}).get('outcome') for x in trace_actions if x.get('bundle')}; bundles={tuple(x.get('bundle',{}).get('selected_components',[])) for x in trace_actions}
        metrics[model]={**m,'runtime_term_leak_count':len(runtime_hits),'exact_duplicate_sentence_count':exact,'prompt_chars':len(prompt),'distinct_families':len(fams),'distinct_outcomes':len(outs),'distinct_component_bundles':len(bundles),'quality_gate':'PASS' if (not runtime_hits and exact==0 and m['semantic_bundle_collision_pairs']==0 and m['component_reuse_ratio']<=0.22) else 'FAIL'}
        locked={'actors':{k:v.get('name',k) for k,v in actors.items()},'weapons':{k:v.get('weapon') for k,v in actors.items()},'event_ids':shot_ir.get('all_event_ids',[]),'ending':final,'spatial_provenance':shot_ir.get('spatial_provenance',{})}
        outputs[model]={'prompt':prompt,'source':'SHOT_IR_V10.2.2','invariant_manifest':locked,'semantic_fingerprint':sha(locked),'shot_count':len(shot_ir.get('shots',[])),'event_coverage':shot_ir.get('all_event_ids',[]),'compiler_mode':'combat_semantic_compiler_v4_zero_copy_model_native','semantic_trace':trace,'segment_plan':shot_records,'diversity_metrics':metrics[model]}
    return outputs,metrics

def compile_native_api(runtime_path,shot_path): return compile(load(runtime_path),load(shot_path))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime',required=True); ap.add_argument('--shot-ir',required=True); ap.add_argument('--out',required=True); ap.add_argument('--quality-out',required=True); args=ap.parse_args()
    runtime=load(args.runtime)
    if not runtime.get('selected_action_payloads') and not runtime.get('_actions_cache'): runtime['_actions_cache']=load(ROOT/'DATA/COMBAT_KNOWLEDGE/actions_10000.json')
    idx=ROOT/'DATA/COMBAT_KNOWLEDGE/SEMANTIC_COMPONENT_INDEX_V10.2.1.json'; runtime['_semantic_freq']=load(idx).get('component_frequencies',{}) if idx.exists() else {}
    out,metrics=compile(runtime,load(args.shot_ir)); Path(args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); Path(args.quality_out).write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    ok=all(v['quality_gate']=='PASS' for v in metrics.values()); print('COMBAT_SEMANTIC_COMPILATION='+('PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
if __name__=='__main__': main()
