#!/usr/bin/env python3
import argparse, json, hashlib, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

FAMILY_PHRASE={
 'entry':'迅速抢入','probe':'试探牵制','guard_break':'压开防线','direct_strike':'正面强攻','angle_change':'侧向换角','bind':'兵器纠缠','redirect':'卸力转线','counter':'抓住空隙反击','chase':'紧追压迫','retreat_attack':'后撤反打','aerial':'凌空变线','low_attack':'低位切入','throw':'借势摔落','grapple':'贴身缠拿','finisher':'终结压迫'}
OUTCOME={
 'hit':'命中后使对手身体或武器线发生明确位移',
 'block':'被格挡后双方短暂受力停顿并重新换线',
 'dodge':'对手脱离攻击线，攻击者顺势释放前冲动量',
 'miss':'攻击落空，攻击者带着原有惯性完成回收',
 'bind':'兵器短暂锁住，双方借受力争夺下一条攻击线'}
RUNTIME_WORDS=['transition_contract','execution_contract','result_lock','INFERRED','FACT','NORMALIZED','knowledge_action_id','execution_model','opponent_response','state_contract','SHOT_IR','CANON','provenance','semantic_fingerprint']
GENERIC=['保持动作连续','重新建立可执行支撑状态','避免中途轨迹漂移','保持同一角色与武器身份','脚—髋—脊柱—肩—肘/腕依次传递','地面→脚踝→膝→髋→躯干→肩→肘→末端']
TECH={'retreat_step':'后撤步','l_step':'L形滑步','stance_switch':'换架','hop':'跃步','shuffle':'滑步','pivot':'枢轴转身','circle_step':'绕步','linear_step':'直线踏步','drop_recover':'下沉回收','air_land_recover':'空中落地回收','pivot_recover':'转轴回收','guard_recover':'护架回收','shoulder_recover':'肩胯复位','bind_release':'解除兵器绑定','retreat_reset':'后撤重置','pivot_reset':'转轴重置','step_reset':'补步重置','drop_base':'下沉重建支撑','state_derived':'状态决定'}

def load(p):
    with open(p,encoding='utf-8') as f:return json.load(f)

def sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]

def family_from_name(name):
    for f,k in [('进身突入','entry'),('试探','probe'),('破防','guard_break'),('直接打击','direct_strike'),('换角','angle_change'),('缠压','bind'),('卸转','redirect'),('反击','counter'),('追击','chase'),('退击','retreat_attack'),('空中','aerial'),('低位','low_attack'),('摔投','throw'),('擒拿','grapple'),('终结','finisher')]:
        if f in name:return k
    return 'probe'

def similar(a,b,threshold=0.78):
    if not a or not b:return False
    if a==b:return True
    def bg(s):return {s[i:i+2] for i in range(max(0,len(s)-1))}
    A=bg(a);B=bg(b)
    if not A or not B:return False
    return len(A&B)/len(A|B)>=threshold

def text_clean(s):
    if not s:return ''
    s=str(s).strip()
    for w in RUNTIME_WORDS:s=s.replace(w,'')
    for k,v in TECH.items(): s=s.replace(k,v)

    for raw,visual in {'地面→脚踝→膝→髋→躯干→肩→肘→末端':'后脚蹬地带动髋部，躯干与肩臂顺势把力量送入武器','脚—髋—脊柱—肩—肘/腕依次传递':'后脚蹬地，髋部与肩线连续联动','后脚蹬地→髋旋→胸廓跟转→肩胛释放→肘端加速':'后脚蹬地带动髋肩联动，力量连续送入武器'}.items(): s=s.replace(raw,visual)
    s=re.sub(r'[；;]+','；',s); s=re.sub(r'[，,]{2,}','，',s)
    s=re.sub(r'(.{4,24})，\1',r'\1',s)
    s=re.sub(r'(.{4,24})\1',r'\1',s)
    return s.strip('；,，。 ')

def compact_trajectory(s):
    s=text_clean(s)
    s=s.replace('外侧斜线 → 外侧斜线末端收束','外侧斜线压入并在末端收束')
    s=s.replace('内侧斜线 → 内侧斜线末端收束','内侧斜线切入并在末端收束')
    s=s.replace('中线 → 中线末端收束','中线压入并在末端收束')
    s=s.replace('环绕线 → 环绕线末端收束','沿环绕线换角并在末端收束')
    s=s.replace('下盘线 → 下盘线末端收束','沿下盘线切入并在末端收束')
    s=s.replace('垂直落线 → 垂直落线末端收束','沿垂直落线下压并在末端收束')
    s=s.replace('，避免中途轨迹漂移','')
    s=s.replace('沿沿','沿')
    s=s.replace('沿环绕线','沿环绕线').replace('沿下盘线','沿下盘线').replace('沿垂直落线','沿垂直落线')
    return s or '既定攻击线'

def action_sentence(c,action,seen_global):
    actor_name=action.get('_actor_name') or c.get('actor_identity','角色')
    weapon=c['weapon_identity']; name=action.get('name','')
    fam=family_from_name(name); frags=name.split('·')
    tactical=frags[2] if len(frags)>2 else ''
    ex=action.get('execution',{}); em=action.get('execution_model',{}); opp=action.get('opponent_response',{}); tc=action.get('transition_contract',{}); trig=action.get('decision_trigger',{})
    startup=text_clean(ex.get('startup','')); joint=text_clean(ex.get('body_kinematics','')); foot=text_clean(ex.get('footwork',''))
    startup=re.sub(r'以(.+?)建立攻击角，先让.+?改变位置，再启动', r'以\1换角，', startup)
    startup=startup.replace('，先让后撤步改变位置，再启动','，').replace('，先让L形滑步改变位置，再启动','，').replace('，先让跃步改变位置，再启动','，')
    traj=text_clean(ex.get('trajectory','')); contact=text_clean(em.get('contact_geometry',{}).get('name',''))
    outcome=opp.get('outcome_class',''); reaction=text_clean(opp.get('primary',{}).get('description','') if isinstance(opp.get('primary'),dict) else opp.get('primary',''))
    recovery=text_clean(ex.get('recovery_path','') or tc.get('result',{}).get('recovery_required',''))
    # Reduce runtime-schema detail to 4 visually useful elements: entry, one body cue, contact/result, recovery.
    parts=[f"{actor_name}以{weapon}{FAMILY_PHRASE.get(fam,'发动攻击')}"]
    tactical_short=tactical.replace('距离过远但需要抢入','远距抢入').replace('对手重心偏移','抓住重心偏移').replace('武器接触后形成控制','利用武器接触控制').replace('节奏破坏','打乱节奏').replace('对手护住正面','压开正面防线')
    if tactical and tactical_short and not any(f'针对{tactical_short}' in x for x in seen_global[-3:]):
        parts.append(f"针对{tactical_short}")
    if startup:
        parts.append(startup.rstrip('。'))
    if joint and joint not in startup and startup not in joint and not similar(joint,startup,0.72) and len(joint)<=36:
        parts.append(joint.rstrip('。'))
    if traj and len(traj)<48:
        parts.append(compact_trajectory(traj))
    if contact:
        parts.append(f"{contact}")
    if outcome=='hit':
        parts.append(f"命中后{reaction or '对手身体被迫改变攻击线'}")
    elif outcome=='block':
        parts.append(f"被格挡后{reaction or '双方短暂受力并重新换线'}")
    elif outcome=='dodge':
        parts.append(f"对手闪出攻击线，{reaction or '攻击者带着前冲惯性顺势回收'}")
    elif outcome=='miss':
        parts.append(f"落空后{reaction or '攻击者保留前冲惯性并立即回收'}")
    elif outcome=='bind':
        parts.append(f"兵器短暂锁住，{reaction or '双方借反作用力争夺下一条攻击线'}")
    else:
        if reaction: parts.append(reaction)
    if recovery:
        parts.append(f"随即{recovery}")
    clean=[]
    for q in parts:
        q=text_clean(q)
        if not q: continue
        if any(similar(q,x,0.85) for x in clean): continue
        clean.append(q)
    sentence='；'.join(clean)+'。'
    # Shot-level dedup: if overly similar to recent sentence, keep only the most discriminating tactical/result portion.
    if any(similar(sentence,s,0.90) for s in seen_global[-5:]):
        short=[f"{actor_name}用{weapon}{FAMILY_PHRASE.get(fam,'发动攻击')}"]
        if outcome=='hit': short.append('命中后迫使对手失去原攻击线')
        elif outcome=='block': short.append('被架住后立刻换线')
        elif outcome=='dodge': short.append('逼得对手脱线，顺势回收')
        elif outcome=='miss': short.append('落空后带惯性回收')
        elif outcome=='bind': short.append('兵器短暂锁住，双方争夺下一线')
        elif recovery: short.append(f"随即{recovery}")
        sentence='；'.join(short)+'。'
    seen_global.append(sentence)
    trace={'family':fam,'tactical_signal':tactical,'motion_kept':bool(startup or joint),'trajectory_kept':bool(traj),'contact_kept':bool(contact),'outcome':outcome,'recovery_kept':bool(recovery)}
    return sentence,trace

def ability_sentence(ac,canon,event_id):
    actor=canon.get(ac['actor_identity'],{}).get('name',ac['actor_identity'])
    weapon=canon.get(ac['actor_identity'],{}).get('weapon','武器')
    sem=ac.get('execution_contract_v2') or {}
    visual=ac.get('visual_profile') or '法相'
    if event_id.endswith('ACTIVATION'):
        return f"{actor}骤然提气，周身能量沿身体主轴收拢，法相进入激活。"
    if event_id.endswith('MANIFEST'):
        return f"{actor}身后的{visual}顺着本体动作轴成形，体量扩张但与本体保持同步。"
    if event_id.endswith('WEAPON-SYNC'):
        return f"{actor}抬起{weapon}，法相沿同一武器攻击线同步蓄力。"
    if event_id.endswith('CLASH'):
        return f"{actor}的法相沿本体攻击线压入，{sem.get('primary_interaction','正面交锋')}，{sem.get('clash_resolution','冲击结果清晰可见')}。"
    return f"{actor}维持法相执行。"

def choose_camera(sh,contracts):
    cams=[]
    for c in contracts:
        cam=(c.get('presentation') or {}).get('camera') or {}
        if isinstance(cam,dict):
            p=cam.get('primary',{}) or {}
            txt=p.get('prompt_camera_sentence') or p.get('name')
            if txt:cams.append(text_clean(txt))
    unique=[]
    for x in cams:
        if x and not any(similar(x,y,0.80) for y in unique):unique.append(x)
    return unique[0] if unique else '镜头跟随主要人物的位移与武器攻击线，接触时短促强调，回收时跟回身体重心。'

def choose_vfx(contracts,story):
    names=[]
    for c in contracts:
        v=(c.get('presentation') or {}).get('vfx') or {}
        if isinstance(v,dict):
            p=v.get('primary',{}) or {}; n=p.get('name')
            if n and n not in names:names.append(n)
    if story=='combat_open': return '剑枪初次交击溅起短促冰蓝火花，攻击轨迹保持清晰。'
    if story=='counter_exchange': return '高速变线只留下短促武器残影，接触点保持清楚。'
    if story=='pressure_shift': return '受力瞬间云雾向两侧卷开，冲击方向与身体位移一致。'
    if story=='high_intensity_exchange': return '连续兵器碰撞产生密集火星，特效只强调接触瞬间。'
    if story=='escalation': return '银白与青蓝能量逐层扩散，围绕两人的攻击轴形成高压气流。'
    if story=='final_build': return '龙气与青云灵光快速聚拢，法相轮廓随本体动作同步放大。'
    if story=='final_clash_result': return '法相碰撞掀开整片云海，银白与冰蓝碎光沿冲击方向向外扩散。'
    if not names:return ''
    n=names[0]
    if '轨迹' in n or '残影' in n:return '只保留短促武器轨迹残影，主体轮廓与接触点始终清晰。'
    if '冲击' in n or '动能' in n:return '冲击只沿真实受力方向扩散，强化接触瞬间。'
    return f"{n}只用于强化已经发生的物理结果，不提前生成事件。"

def compile(runtime,shot_ir):
    canon=runtime['canon']; contracts={c['event_id']:c for c in runtime['action_contracts']}; actions={a['action_id']:a for a in runtime.get('_actions_cache',[])}; abilities=runtime.get('ability_contracts',[])
    common='8K电影级3D CG写实，次世代PBR物理材质，UE5级电影渲染，16:9横画幅，60fps，HDR，真实全局光照与体积光，电影级景深、真实运动模糊，细腻皮肤、毛发、衣物与金属材质，真实重量、惯性与受力反馈。'
    scene='高空云海仙山空域，云层具有纵深与流动感，人物高速交错时卷起连续气流。'
    outputs={}; metrics={}
    for model in ['universal','seedance_2_5','minimax_h3']:
        lines=[common, f"{canon['xiao_bailong']['name']}保持参考资产外观，始终使用龙鳞剑；{canon['yun_shuying']['name']}保持参考资产外观，始终使用凌云长枪。", scene]
        seen=[]; trace=[]
        for sh in shot_ir['shots']:
            clauses=[]; shot_contracts=[]
            for eid in sh['event_ids']:
                c=contracts.get(eid)
                if c:
                    a=actions.get(c['knowledge_action_id'])
                    if a:
                        a=dict(a); a['_actor_name']=canon.get(c['actor_identity'],{}).get('name',c['actor_identity'])
                        s,t=action_sentence(c,a,seen); clauses.append(s); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'action',**t}); shot_contracts.append(c)
                    continue
                if eid.startswith('RECOVERY-'): continue
                found=False
                for ac in abilities:
                    if eid in ac.get('ability_event_ids',[]):
                        clauses.append(ability_sentence(ac,canon,eid)); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'ability'}); found=True; break
                if eid=='ABILITY-FINAL-CLASH':
                    clauses.append('小白龙与云疏影同时爆发，两尊法相沿龙鳞剑与凌云长枪的真实攻击线正面撞上，力量在接触点瞬间集中并形成决定性冲击。'); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'joint_clash'}); found=True
                elif eid=='ABILITY-FINAL-RESULT-LOCK':
                    clauses.append('最终碰撞后，云疏影的法相结构首先崩解，身体被冲击力震退，胜负在此刻确定。'); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'result'}); found=True
                elif eid=='ENDING-RESULT-LOCK':
                    d=canon[runtime['ending']['defeated_actor']]['name']; v=canon[runtime['ending']['victor']]['name']
                    clauses.append(f"{d}转身化作冰蓝遁光逃离；{v}向前追出半步后主动收剑停住，不再追击，任由她消失在远处云海。") ; trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'ending'}); found=True
            uniq=[]
            for cl in clauses:
                if cl and not any(similar(cl,u,0.82) for u in uniq):uniq.append(cl)
            shot_text=' '.join(uniq)
            camera_by_story={
                'combat_open':'三分之四跟拍，先交代双方距离，随后贴住武器攻击线。',
                'counter_exchange':'低机位侧向跟拍，连续保留闪避、反制和兵器接触。',
                'pressure_shift':'绕侧跟拍，围绕攻击者与目标的轴线移动，突出攻守转换。',
                'high_intensity_exchange':'低机位高速推进，接触瞬间短促加速，立即跟住受击反应。',
                'escalation':'镜头拉宽再快速推进，显出两人能量升级和空间变化。',
                'final_build':'由中景缓慢推近到双人对峙，再拉开容纳完整法相。',
                'final_clash_result':'先用大远景完整呈现双法相碰撞，再跟住败者逃离并停在胜者身后。'}
            cam=camera_by_story.get(sh['story_function'], choose_camera(sh,shot_contracts) if shot_contracts else '跟随主体位移与武器攻击线。')
            vfx=choose_vfx(shot_contracts,sh['story_function'])
            if model=='universal':
                lines.append(f"{sh['shot_id']}（{sh['duration']}秒）：{shot_text} 镜头：{cam}" + (f" 特效：{vfx}" if vfx else ''))
            elif model=='seedance_2_5':
                lines.append(f"{sh['shot_id']}：{shot_text} 镜头：{cam}" + (f" 特效：{vfx}" if vfx else ''))
            else:
                physics_by_story={
                    'combat_open':'先有兵器接触，再出现受力与身体位移。',
                    'counter_exchange':'闪避或反制先改变攻击线，再由惯性推动下一动作。',
                    'pressure_shift':'接触点决定受力方向，身体重心随后改变。',
                    'high_intensity_exchange':'连续碰撞按接触→受力→反应顺序发生。',
                    'escalation':'能量升级服从人物动作轴与空间变化。',
                    'final_build':'法相先由本体能量激活，再与武器攻击轴同步。',
                    'final_clash_result':'先发生法相碰撞，再出现崩解、败退与停止追击。'}
                lines.append(f"【{sh['shot_id']}】{shot_text} Camera：{cam} Physics：{physics_by_story.get(sh['story_function'],'先接触、再受力、再出现结果。')}" + (f" VFX：{vfx}" if vfx else ''))
        locked={'actors':{k:v.get('name') for k,v in canon.items()},'weapons':{k:v.get('weapon') for k,v in canon.items()},'event_ids':shot_ir['all_event_ids'],'ending':runtime['ending'],'spatial_provenance':shot_ir['spatial_provenance']}
        prompt='\n'.join(lines)
        outputs[model]={'prompt':prompt,'source':'SHOT_IR_V10.1.9','invariant_manifest':locked,'semantic_fingerprint':sha(locked),'shot_count':len(shot_ir['shots']),'event_coverage':shot_ir['all_event_ids'],'compiler_mode':'combat_semantic_compiler_v2','semantic_trace':trace}
        metrics[model]=semantic_metrics(prompt,trace)
    return outputs,metrics

def semantic_metrics(prompt,trace):
    runtime_hits=[w for w in RUNTIME_WORDS if w in prompt]
    sentences=[x.strip() for x in re.split(r'[。\n]',prompt) if x.strip()]
    exact_dups=sum(1 for i,a in enumerate(sentences) for b in sentences[i+1:] if a==b)
    repetitive=[g for g in GENERIC if prompt.count(g)>1]
    mean=sum(map(len,sentences))/max(1,len(sentences))
    return {'runtime_term_leak_count':len(runtime_hits),'exact_duplicate_sentence_count':exact_dups,'repeated_generic_phrase_types':repetitive,'average_sentence_chars':round(mean,1),'trace_items':len(trace),'quality_gate':'PASS' if not runtime_hits and exact_dups==0 and len(repetitive)<=1 else 'FAIL'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime',required=True); ap.add_argument('--shot-ir',required=True); ap.add_argument('--out',required=True); ap.add_argument('--quality-out')
    a=ap.parse_args(); runtime=load(a.runtime); shot=load(a.shot_ir); runtime['_actions_cache']=load(ROOT/'DATA/COMBAT_KNOWLEDGE/actions_10000.json')
    res,metrics=compile(runtime,shot); json.dump(res,open(a.out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    if a.quality_out: json.dump(metrics,open(a.quality_out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    ok=all(x['quality_gate']=='PASS' for x in metrics.values())
    print('COMBAT_SEMANTIC_COMPILATION=PASS'); print('PROMPT_SEMANTIC_QUALITY='+('PASS' if ok else 'FAIL'))
    if not ok:sys.exit(1)
if __name__=='__main__':main()
