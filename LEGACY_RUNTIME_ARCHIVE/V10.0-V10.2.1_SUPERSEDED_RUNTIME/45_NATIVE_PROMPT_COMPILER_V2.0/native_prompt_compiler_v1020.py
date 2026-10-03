#!/usr/bin/env python3
import argparse,json,hashlib,re,sys,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
engine_path=ROOT/'43_COMBAT_SEMANTIC_DIVERSITY_ENGINE_V1.0/semantic_diversity_engine_v1020.py'
spec=importlib.util.spec_from_file_location('sde',engine_path); sde=importlib.util.module_from_spec(spec); spec.loader.exec_module(sde)

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]

def similarity(a,b,th=0.82):
    a=a.strip(); b=b.strip()
    if a==b:return True
    A={a[i:i+2] for i in range(max(0,len(a)-1))};B={b[i:i+2] for i in range(max(0,len(b)-1))}
    return bool(A and B and len(A&B)/len(A|B)>=th)

def action_map(runtime): return {a['action_id']:a for a in runtime.get('_actions_cache',[])}

def ability_sentence(ac,canon,event_id):
    aid=ac['actor_identity']; actor=canon[aid]['name']; weapon=canon[aid]['weapon']; visual=ac.get('visual_profile') or '法相'; sem=ac.get('execution_contract_v2') or {}
    if event_id.endswith('ACTIVATION'): return f'{actor}骤然提气，周身力量收拢到身体主轴，法相从蓄势中启动。'
    if event_id.endswith('MANIFEST'): return f'身后的{visual}沿{sem.get("body_line","本体动作轴")}成形，与{actor}保持同向运动。'
    if event_id.endswith('WEAPON-SYNC'): return f'{actor}抬起{weapon}，法相同步占据同一攻击线，蓄力与本体动作完全一致。'
    if event_id.endswith('CLASH'): return f'{actor}带动法相完成一次{sem.get("primary_interaction","正面交锋")}，接触结果沿真实攻击轴传递。'
    return ''

def story_camera(story):
    return {
    'combat_open':'三分之四近跟，先看清双方间距，再锁住枪剑接触线。',
    'counter_exchange':'低机位横移跟拍，先保留闪避方向，再追进反击线路。',
    'pressure_shift':'绕侧跟拍，围绕两人的轴线移动，突出兵器控制到攻守转换。',
    'high_intensity_exchange':'低机位快速推进，连续接触保持在画面中心，受击反应紧跟其后。',
    'escalation':'中远景拉开空间，再迅速向两人的能量轴推进，让升级过程一口气完成。',
    'final_build':'镜头先压近双方蓄力姿态，再后撤到足以容纳完整双法相的距离。',
    'final_clash_result':'大远景完整呈现法相碰撞，随后贴住败者逃离，最后停在没有追击的胜者身后.'
    }.get(story,'沿主要攻击线跟拍，接触时短促强调，恢复时回到人物重心。')

def story_vfx(story):
    return {
    'combat_open':'初次剑枪接触只留下短促冰蓝火花，碰撞方向和身体位移一致。',
    'counter_exchange':'变线时保留短促武器残影，闪避后的惯性清楚可见。',
    'pressure_shift':'兵器绑定处出现压缩气流，随后云雾沿受力方向被推出。',
    'high_intensity_exchange':'连续碰撞的火星只在接触瞬间爆开，不遮挡剑锋与枪尖。',
    'escalation':'银白龙气与青蓝灵光逐层聚拢，能量扩散服从本体运动轴。',
    'final_build':'法相轮廓随着本体蓄力同步放大，能量从身体向外扩张。',
    'final_clash_result':'双法相碰撞掀开云海，败者法相碎裂成碎光，逃离方向保持连续。'
    }.get(story,'特效只解释已经发生的接触、受力和环境响应。')

def compile(runtime,shot_ir):
    canon=runtime['canon']; acts=action_map(runtime); contracts={c['event_id']:c for c in runtime['action_contracts']}; abilities=runtime.get('ability_contracts',[])
    common='8K电影级3D CG写实，次世代PBR物理材质，UE5级电影渲染，16:9横画幅，60fps，HDR，真实全局光照与体积光，电影级景深，真实运动模糊，细腻皮肤、毛发、衣物与金属材质，真实重量、惯性与受力反馈。'
    identity=f'{canon["xiao_bailong"]["name"]}保持参考资产外观，始终使用龙鳞剑；{canon["yun_shuying"]["name"]}保持参考资产外观，始终使用凌云长枪。'
    scene='以人物参考图的东方仙幻视觉气质为基础建立战斗空间，保持两人的空间连续与运动方向一致。'
    outputs={}; metrics={}
    for model in ('universal','seedance_2_5','minimax_h3'):
        lines=[common,identity,scene]; seq_usage={'family':{},'tactical':{},'components':{},'outcome':{}}
        from collections import Counter
        for key in seq_usage: seq_usage[key]=Counter()
        chosen_bundles=[]; semantic_trace=[]
        segment_plan=[]
        for sh in shot_ir['shots']:
            shot_usage={'family':Counter(),'tactical_tail':[],'components':Counter(),'outcome':Counter()}
            clauses=[]
            for eid in sh['event_ids']:
                c=contracts.get(eid)
                if c:
                    a=acts.get(c['knowledge_action_id'])
                    if a:
                        sentence,bundle=sde.compile_action(a,canon[c['actor_identity']]['name'],seq_usage,shot_usage,{
                          k:Counter({str(x):y for x,y in runtime.get('_semantic_freq',{}).get(k,{}).items()}) for k in []
                        },sh['story_function'],None)
                        clauses.append(sentence); chosen_bundles.append({'shot_id':sh['shot_id'],'event_id':eid,**bundle})
                        semantic_trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'action','sentence':sentence,'story_role':sh['story_function'],'bundle':bundle})
                        continue
                found=False
                for ac in abilities:
                    if eid in ac.get('ability_event_ids',[]):
                        txt=ability_sentence(ac,canon,eid)
                        if txt:clauses.append(txt); semantic_trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'ability'}); found=True;break
                if found:continue
                if eid=='ABILITY-FINAL-CLASH':
                    clauses.append('两人同时推动法相全力前压，巨大的龙形法相与青云法相沿各自真实武器攻击轴正面撞上，力量集中于接触点爆发。'); semantic_trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'joint_clash'});continue
                if eid=='ABILITY-FINAL-RESULT-LOCK':
                    clauses.append('碰撞结果被清楚锁定，云疏影的法相首先崩解，身体被冲击力推出，战局就此结束。'); semantic_trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'result'});continue
                if eid=='ENDING-RESULT-LOCK':
                    d=canon[runtime['ending']['defeated_actor']]['name'];v=canon[runtime['ending']['victor']]['name']
                    clauses.append(f'{d}转身化作冰蓝遁光逃离；{v}只向前追出半步便停住并收剑，不再追击。'); semantic_trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'ending'});continue
            # intra-shot duplicate suppression
            uniq=[]
            for cl in clauses:
                if not any(similarity(cl,u,0.86) for u in uniq):uniq.append(cl)
            txt=' '.join(uniq)
            segment_plan.append({'shot_id':sh['shot_id'],'story_role':sh['story_function'],'selected_component_types':sorted({k for b in chosen_bundles if b.get('shot_id')==sh['shot_id'] for k,_ in b.get('selected_components',[])}),'families':sorted({b.get('family') for b in chosen_bundles if b.get('shot_id')==sh['shot_id']}),'outcomes':sorted({b.get('outcome') for b in chosen_bundles if b.get('shot_id')==sh['shot_id']})})
            cam=story_camera(sh['story_function']); vfx=story_vfx(sh['story_function'])
            if model=='universal': lines.append(f'{sh["shot_id"]}（{sh["duration"]}秒）：{txt} 镜头：{cam} 特效：{vfx}')
            elif model=='seedance_2_5': lines.append(f'{sh["shot_id"]}：{txt} 镜头：{cam} 特效：{vfx}')
            else:
                phys={
                  'combat_open':'先形成攻击线，再发生剑枪接触与受力。','counter_exchange':'先改变攻击线，再出现闪避/反击结果，惯性持续到回收。','pressure_shift':'先发生兵器控制，再产生受力和身体位移。','high_intensity_exchange':'每次碰撞都遵循接触→受力→反应→恢复。','escalation':'能量升级服从人物动作轴和空间变化。','final_build':'法相先由本体蓄力激活，再与武器攻击轴同步。','final_clash_result':'先发生法相碰撞，再出现法相崩解、败退与停止追击。'}
                lines.append(f'【{sh["shot_id"]}】{txt} Camera：{cam} Physics：{phys.get(sh["story_function"],"接触后产生受力，再进入结果与恢复。")} VFX：{vfx}')
        prompt='\n'.join(lines)
        m=sde.dedup_component_metrics(chosen_bundles)
        # directness / diversity metrics
        sentences=[x for x in re.split(r'[。\n]',prompt) if x.strip()]
        exact=sum(1 for i,a in enumerate(sentences) for b in sentences[i+1:] if a==b)
        runtime_hits=[w for w in ['transition_contract','execution_contract','result_lock','INFERRED','FACT','NORMALIZED','knowledge_action_id','execution_model','opponent_response','state_contract','SHOT_IR','CANON','provenance','semantic_fingerprint'] if w in prompt]
        metrics[model]={**m,'runtime_term_leak_count':len(runtime_hits),'exact_duplicate_sentence_count':exact,'prompt_chars':len(prompt),'quality_gate':'PASS' if (not runtime_hits and not exact and m['semantic_bundle_collision_pairs']==0 and m['component_reuse_ratio']<=0.22) else 'FAIL'}
        locked={'actors':{k:v['name'] for k,v in canon.items()},'weapons':{k:v['weapon'] for k,v in canon.items()},'event_ids':shot_ir['all_event_ids'],'ending':runtime['ending'],'spatial_provenance':shot_ir['spatial_provenance']}
        outputs[model]={'prompt':prompt,'source':'SHOT_IR_V10.2.0','invariant_manifest':locked,'semantic_fingerprint':sha(locked),'shot_count':len(shot_ir['shots']),'event_coverage':shot_ir['all_event_ids'],'compiler_mode':'combat_semantic_compiler_v3_deep_diversity','semantic_trace':semantic_trace,'segment_plan':segment_plan,'diversity_metrics':metrics[model]}
    return outputs,metrics

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--shot-ir',required=True);ap.add_argument('--out',required=True);ap.add_argument('--quality-out',required=True);args=ap.parse_args()
    runtime=load(args.runtime); runtime['_actions_cache']=load(ROOT/'DATA/COMBAT_KNOWLEDGE/actions_10000.json')
    # component frequencies from index for future weighting (currently not required by engine heuristic)
    idx=load(ROOT/'DATA/COMBAT_KNOWLEDGE/SEMANTIC_COMPONENT_INDEX_V10.2.0.json'); runtime['_semantic_freq']=idx.get('component_frequencies',{})
    shot=load(args.shot_ir); out,metrics=compile(runtime,shot); 
    Path(args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); Path(args.quality_out).write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    ok=all(v['quality_gate']=='PASS' for v in metrics.values()); print('COMBAT_SEMANTIC_DIVERSITY_COMPILATION=PASS' if ok else 'COMBAT_SEMANTIC_DIVERSITY_COMPILATION=FAIL'); print('DEEP_PROMPT_SEMANTIC_QUALITY='+('PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
if __name__=='__main__':main()
