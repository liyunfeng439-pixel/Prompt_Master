#!/usr/bin/env python3
import argparse, json, hashlib, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load_json(p):
    with open(p,encoding='utf-8') as f:return json.load(f)
def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:16]

def normalize_actor_state(canon):
    parts=[]
    for aid,v in canon.items():
        parts.append(f"{v.get('name','角色')}保持参考资产外观，唯一武器为{v.get('weapon','未知武器')}")
    return '；'.join(parts)

def clean_runtime_terms(text):
    repl={'linear_step':'直线踏步','shuffle':'滑步','l_step':'L形步','stance_switch':'换架步','hop':'跳步','retreat_step':'后撤步','drop_recover':'下沉回收','air_land_recover':'空中落地回收','pivot_recover':'转轴回收','guard_recover':'护架回收','shoulder_recover':'肩胯复位','bind_release':'解除绑定回收','retreat_reset':'后撤重置','pivot_reset':'转轴重置','step_reset':'补步重置','drop_base':'下沉重建支撑','state_derived':'状态决定','far':'远距','close':'近距','mid':'中距'}
    for k,v in repl.items(): text=text.replace(k,v)
    return text.replace('重心重心','重心').replace('接触后不完全僵直，接触后不完全僵直','接触后保持可恢复的弹性回收')

def action_clause(contract, action=None):
    actor=contract['actor_identity']; weapon=contract['weapon_identity']; ex=contract.get('execution_native',{}); em=contract.get('execution',{}); opp=contract.get('result',{}).get('opponent_response',{}); tc=contract.get('transition_contract',{})
    label=contract.get('action_name','动作')
    parts=label.split('·')
    visual_action=parts[1] if len(parts)>=2 else label
    startup=ex.get('startup','完成起手')
    body=ex.get('body_kinematics', em.get('joint_chain',{}).get('path','连续身体链'))
    foot=ex.get('footwork','根据当前距离调整脚步')
    traj=ex.get('trajectory', em.get('center_of_mass',{}).get('description','保持攻击线'))
    contact=em.get('contact_geometry',{}).get('name','明确接触')
    outcome=opp.get('outcome_class','result')
    reaction=opp.get('primary',{}).get('description','保持战斗姿态') if isinstance(opp.get('primary',{}),dict) else str(opp.get('primary','保持战斗姿态'))
    recovery_map={'guard_recover':'护架回收','shoulder_recover':'肩胯复位','air_land':'空中落地并重新建立支撑','bind_release':'解除兵器绑定并重建攻击线','retreat_reset':'后撤重置并重新建立距离','pivot_reset':'转轴回收并重新建立攻击线','drop_base':'下沉重建支撑','step_reset':'补步重置'}
    rec=recovery_map.get(tc.get('result',{}).get('recovery_required',''), '重新建立支撑')
    result_text={'hit':f"形成有效命中，对手{reaction}",'block':f"被防守线格挡，对手{reaction}",'dodge':f"对手脱离原攻击线，{reaction}",'miss':f"攻击落空，对手{reaction}",'bind':f"兵器与对手短暂绑定，{reaction}"}.get(outcome,f"形成{outcome}结果，对手{reaction}")
    return clean_runtime_terms(f"{actor}使用{weapon}进行{visual_action}；{startup}，{body}，{foot}，轨迹为{traj}；以{contact}{result_text}；随后{rec}，保持动作连续。")

def compile_prompts(runtime, shot_ir):
    canon=runtime['canon']; contracts={c['event_id']:c for c in runtime['action_contracts']}
    common=("8K电影级3D CG写实，次世代PBR物理材质，UE5级电影渲染，16:9横画幅，60fps，HDR，真实全局光照与体积光，电影级景深、真实运动模糊，细腻皮肤、毛发、衣物与金属材质，真实重量、惯性与受力反馈。")
    abilities={a['ability_contract_id']:a for a in runtime.get('ability_contracts',[])}
    def ability_clause(ac,event_id):
        display=canon.get(ac['actor_identity'],{}).get('name',ac['actor_identity'])
        sem=ac.get('execution_contract_v2') or {}
        visual=ac.get('manifestation_state',{}).get('visual_profile','法相')
        if event_id.endswith('ACTIVATION'):
            return f"{display}周身能量骤然聚集，进入法相激活状态，衣袍与长发被强气流掀起。"
        if event_id.endswith('MANIFEST'):
            return f"{display}身后升起{visual}，巨型法相沿本体动作方向成形，持续保持与人物同步。"
        if event_id.endswith('WEAPON-SYNC'):
            return f"{display}抬起{canon.get(ac['actor_identity'],{}).get('weapon','武器')}，法相同步完成同一武器轨迹与身体转轴。"
        if event_id.endswith('CLASH'):
            return f"{display}的法相沿本体攻击线高速压入，以{sem.get('primary_interaction','正面交锋')}，{sem.get('clash_resolution','产生明确受力与结果')}。"
        return f"{display}维持法相执行状态。"

    compiled={}
    for model in ['universal','seedance_2_5','minimax_h3']:
        lines=[common, normalize_actor_state(canon)]
        spatial=shot_ir.get('spatial_provenance',{})
        if isinstance(spatial,dict) and spatial.get('status') in ('INFERRED','FACT'):
            lines.append('高空云海仙山空域，云层具有纵深与流动感，人物高速移动时产生连续卷云与气流变化。')
        elif spatial:
            lines.append(str(spatial))
        if model=='universal': lines.append('只呈现连续可见的战斗事件：动作、接触/规避、受力、对手反应、恢复、法相升级与最终状态。')
        elif model=='seedance_2_5': lines.append('连续执行单元：主体→动作→方向→接触/规避→物理结果→下一状态；减少解释性语言，保持同一角色与武器身份。')
        else: lines.append('按Scene、Asset Lock、Chronological Action、Camera、Physics/VFX、Continuity、Ending顺序直接执行。')
        shot_records=[]
        for sh in shot_ir['shots']:
            clauses=[]
            for eid in sh['event_ids']:
                c=contracts.get(eid)
                if c:
                    display=canon.get(c['actor_identity'],{}).get('name',c['actor_identity'])
                    c2=dict(c); c2['actor_identity']=display
                    clauses.append(action_clause(c2,c))
                elif eid in ('ABILITY-FINAL-CLASH','ABILITY-FINAL-RESULT-LOCK'):
                    if eid=='ABILITY-FINAL-CLASH':
                        acs=list(abilities.values())
                        if len(acs)>=2:
                            a1,a2=acs[0],acs[1]
                            n1=canon.get(a1['actor_identity'],{}).get('name',a1['actor_identity']); n2=canon.get(a2['actor_identity'],{}).get('name',a2['actor_identity'])
                            s1=(a1.get('execution_contract_v2') or {}).get('clash_resolution','完成正面法相碰撞')
                            s2=(a2.get('execution_contract_v2') or {}).get('clash_resolution','完成正面法相碰撞')
                            clauses.append(f"{n1}与{n2}同时向前爆发，两尊法相沿各自本体武器攻击线正面碰撞；{s1}；{s2}。")
                    else:
                        clauses.append('双方最终法相结果锁定：胜负已经确定，后续只允许执行结束、逃离或显式停止追击，不得新增攻击改变结果。')
                else:
                    e=next((x for x in runtime.get('events',[]) if x['event_id']==eid),None)
                    if e and e.get('type')=='recovery':
                        recovery_map={'guard_recover':'护架回收','shoulder_recover':'肩胯复位','air_land':'空中落地并重新建立支撑','bind_release':'解除兵器绑定并重建攻击线','retreat_reset':'后撤重置并重新建立距离','pivot_reset':'转轴回收并重新建立攻击线','drop_base':'下沉重建支撑','step_reset':'补步重置'}
                        rid=e.get('recovery_id','恢复')
                        clauses.append(f"{canon.get(e.get('actor_id'),{}).get('name',e.get('actor_id'))}{recovery_map.get(rid,rid)}，重新建立可执行支撑状态。")
                    elif e and e.get('type')=='ability' and e.get('ability_contract_id') in abilities:
                        clauses.append(ability_clause(abilities[e['ability_contract_id']],eid))
                if eid=='ENDING-RESULT-LOCK':
                    defeated=canon.get(runtime['ending']['defeated_actor'],{}).get('name',runtime['ending']['defeated_actor'])
                    victor=canon.get(runtime['ending']['victor'],{}).get('name',runtime['ending']['victor'])
                    clauses.append(f"结束状态：{defeated}在结果锁定后败退逃离；{victor}具备追击条件但主动停止追击，不新增攻击事件。")
            shot_records.append({'shot_id':sh['shot_id'],'beat_ids':sh['beat_ids'],'event_ids':sh['event_ids'],'text':' '.join(clauses)})
        if model=='universal':
            for r in shot_records:
                d=next((x['duration'] for x in shot_ir['shots'] if x['shot_id']==r['shot_id']),0)
                lines.append(f"{r['shot_id']}（{d}秒）：{r['text']}")
        elif model=='seedance_2_5':
            for r in shot_records: lines.append(f"{r['shot_id']}：{r['text']}")
        else:
            for r in shot_records: lines.append(f"【{r['shot_id']}】Chronological Action：{r['text']} Camera：跟随主体速度并保留关键接触、反应、恢复；Physics/VFX：只表现已有物理结果，不用特效制造事件。")
        locked={'actors':{k:v.get('name') for k,v in canon.items()},'weapons':{k:v.get('weapon') for k,v in canon.items()},'event_ids':shot_ir['all_event_ids'],'ending':runtime['ending'],'spatial_provenance':shot_ir['spatial_provenance']}
        compiled[model]={'prompt':'\n'.join(lines),'source':'SHOT_IR_V10.1.8','invariant_manifest':locked,'semantic_fingerprint':sha(locked),'shot_count':len(shot_records),'event_coverage':event_tokens_from_shots(shot_records)}
    return compiled

def event_tokens_from_shots(shots):
    return [e for s in shots for e in s['event_ids']]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime',required=True); ap.add_argument('--shot-ir',required=True); ap.add_argument('--out',required=True)
    args=ap.parse_args(); runtime=load_json(args.runtime); shot_ir=load_json(args.shot_ir)
    # cache action data for compiler
    actions=load_json(ROOT/'DATA/COMBAT_KNOWLEDGE/actions_10000.json'); runtime['_actions_cache']=actions
    result=compile_prompts(runtime,shot_ir)
    json.dump(result,open(args.out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print('NATIVE_PROMPT_COMPILATION=PASS')
if __name__=='__main__': main()
