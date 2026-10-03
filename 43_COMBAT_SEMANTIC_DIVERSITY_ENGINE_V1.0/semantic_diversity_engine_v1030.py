#!/usr/bin/env python3
import json,re,math,hashlib
from collections import Counter,defaultdict

FAMILY_PHRASES={
'entry':['突入抢位','猛然切入','压步逼近'],
'probe':['试探防线','虚晃探路','探出防守线路'],
'guard_break':['迎着防线压开','顺着守势撕开缺口','把防守轴硬生生拨开'],
'direct_strike':['正面压上','沿中线强攻','直接追着空隙贯入'],
'angle_change':['斜切换角','横移脱线后回切','侧向抢角'],
'bind':['锁住兵器线','咬住兵器接触点','贴住对手枪剑'],
'redirect':['卸力转线','借接触把力带偏','顺着来力改线'],
'counter':['借空隙回切','等到线路打开再反打','吃住来力后反向抢线'],
'chase':['紧贴后撤线路压上','不给脱离距离','沿退路持续追压'],
'retreat_attack':['退一步卸力反打','后撤诱导后突然回切','退中抢反攻线'],
'aerial':['跃入空中换线','在高度差里改轴','凌空切断退路'],
'low_attack':['贴低位切入','压低攻击线抢下盘','从低线挑入'],
'finisher':['压出终结线','把最后缺口一次吃尽','以高承诺攻击封口'],
'fade':'probe'
}
TECH_MAP={
'retreat_step':'后撤步','l_step':'L形滑步','hop':'跃步','shuffle':'滑步','stance_switch':'换架','pivot':'枢轴转身','circle_step':'绕步','linear_step':'直线踏步','drop_recover':'下沉回收','air_land_recover':'空中落地回收','pivot_recover':'转轴回收','guard_recover':'护架回收','shoulder_recover':'肩胯复位','bind_release':'解除兵器绑定','retreat_reset':'后撤重置','pivot_reset':'转轴重置','step_reset':'补步重置','drop_base':'下沉重建支撑','state_derived':'状态决定'}
JOINT_PHRASE={
'hip_to_shoulder':'后脚蹬地带动髋部旋转，胸廓跟随，肩臂最后释放',
'ground_to_hip':'支撑脚定住地面，力量从下肢经髋部与躯干送入武器',
'brace_drive':'支撑脚锁定，核心张力带动肩胯同步前送',
'drop_rise':'屈膝下沉蓄力，支撑腿伸展带起髋躯，末端最后加速',
'foot_pelvis':'支撑脚先定位，骨盆平移带动躯干稳定，末端独立加速',
}
TRAJ_PHRASE={
'外侧斜线 → 外侧斜线末端收束':'从外侧斜线压入，末端突然收束',
'内侧斜线 → 内侧斜线末端收束':'贴内侧斜线切进，末端骤然收束',
'中线 → 中线末端收束':'沿中线贯入，最后一步压紧攻击线',
'环绕线 → 环绕线末端收束':'绕着对手外侧改线，回身时迅速收束',
'下盘线 → 下盘线末端收束':'压低线路切向下盘，再从近端收回',
'垂直落线 → 垂直落线末端收束':'从高处垂直下压，末端重重收束',
'':'',
}
CONTACT_PHRASE={
'point':'以小接触面集中力量','hook':'先挂住目标结构再带动位移','wrap':'绕住目标结构形成牵引','bind':'让两件武器短暂咬住','glancing':'擦过目标边缘，把力泄向侧方','soft':'以轻接触改变线路',
}
RECOVERY_PHRASE={
'guarded':'回到护架并重新建立支撑',
'angled':'沿新角度收身',
'balanced':'重建平衡支撑',
'bind_ready':'解除绑定后重新架枪/收剑',
'distance_reset':'后撤重置距离',
'contact_hold':'保持接触准备下一条攻击线',
'':'',
}
OUTCOME_PHRASE={
'hit':'命中后使对手的身体或武器线明显偏转','block':'被架住后双方短暂停住，随即换线','dodge':'逼得对手脱离攻击线，前冲动量继续释放','miss':'攻击擦空，原有动量带着身体继续向前','bind':'剑枪短暂锁住，下一步只能从绑定角度解开'}

def family_from_name(name):
    mapping=[('进身突入','entry'),('试探','probe'),('破防','guard_break'),('直接打击','direct_strike'),('换角','angle_change'),('缠压','bind'),('卸转','redirect'),('反击','counter'),('追击','chase'),('退击','retreat_attack'),('空中','aerial'),('低位','low_attack'),('摔投','throw'),('擒拿','grapple'),('终结','finisher')]
    return next((v for frag,v in mapping if frag in name),'probe')

def norm(s):
    if not s:return ''
    s=str(s)
    for a,b in TECH_MAP.items(): s=s.replace(a,b)
    s=s.replace('，避免中途轨迹漂移','').replace('避免中途轨迹漂移','')
    s=s.replace('脚—髋—脊柱—肩—肘/腕依次传递','后脚蹬地带动髋肩联动，力量连续送入武器')
    s=s.replace('地面→脚踝→膝→髋→躯干→肩→肘→末端','后脚蹬地带动下肢与躯干协同，把力量送入末端')
    s=re.sub(r'[；;]+','；',s); s=re.sub(r'[，,]{2,}','，',s)
    return s.strip('，；。 ')

def extract_components(action):
    ex=action.get('execution',{}) or {}; em=action.get('execution_model',{}) or {}; opp=action.get('opponent_response',{}) or {}; tc=action.get('transition_contract',{}) or {}
    name=action.get('name',''); parts=name.split('·'); tactical=parts[2] if len(parts)>2 else ''
    fam=family_from_name(name)
    wc=em.get('weapon_control',{}) or {}
    contact=em.get('contact_geometry',{}) or {}
    joint=em.get('joint_chain',{}) or {}; com=em.get('center_of_mass',{}) or {}
    reaction=opp.get('primary',{}) or {}
    remote_mode=str(wc.get('control_mode','')) in ('TELEKINETIC','SPIRIT_CONTROLLED','REMOTE_ATTACK','RETURN_CONTROL')
    # Remote execution already has a dedicated concise compiler sentence; do not feed the
    # long generic joint/COM descriptions into diversity selection, which would create
    # repetitive prompt n-grams across multiple remote events.
    joint_path='' if remote_mode else (joint.get('path','') if isinstance(joint,dict) else str(joint))
    com_desc='' if remote_mode else (com.get('description','') if isinstance(com,dict) else str(com))
    return {
      'family':fam,'tactical':tactical,'footwork':ex.get('footwork',''),'body':ex.get('body_kinematics',''),'startup':ex.get('startup',''),
      'trajectory':ex.get('trajectory',''),'contact_id':contact.get('id','') if isinstance(contact,dict) else str(contact),
      'contact_name':contact.get('name','') if isinstance(contact,dict) else str(contact), 'joint_id':joint.get('id','') if isinstance(joint,dict) else str(joint),
      'joint_path':joint_path, 'com_id':com.get('path_id','') if isinstance(com,dict) else str(com),
      'com_desc':com_desc, 'reaction_id':reaction.get('id','') if isinstance(reaction,dict) else str(reaction),
      'reaction_desc':reaction.get('description','') if isinstance(reaction,dict) else str(reaction), 'outcome':opp.get('outcome_class',''),
      'recovery':tc.get('result',{}).get('recovery_output_state') or ex.get('recovery_path',''), 'weapon':action.get('weapon','武器'),
      'weapon_control':wc,
    }

def phrase_for_component(comp, kind):
    c=comp.get(kind,'')
    if not c:return ''
    if kind=='footwork': return norm(c)
    if kind=='body': return norm(c)
    if kind=='startup': return norm(c)
    if kind=='joint_path':
        cid=str(comp.get('joint_id',''))
        return JOINT_PHRASE.get(cid,norm(c))
    if kind=='com_desc': return norm(c)
    if kind=='trajectory':
        base=c.replace('，避免中途轨迹漂移','')
        return TRAJ_PHRASE.get(base,norm(base))
    if kind=='contact_name':
        ids={'钩挂接触':'先挂住目标结构再带动位移','点接触':'以小接触面集中力量','包覆接触':'绕住目标结构形成牵引','擦碰接触':'擦过目标边缘，把力泄向侧方','绑定接触':'让两件武器短暂咬住'}
        return ids.get(c,c)
    if kind=='reaction_desc': return norm(c)
    if kind=='recovery': return RECOVERY_PHRASE.get(str(c),norm(c))
    return norm(c)

def short_tactical(t):
    repl={'距离过远但需要抢入':'抢距离','对手重心偏移':'抓重心','武器接触后形成控制':'利用接触控制','对手护住正面':'压正面','节奏破坏':'打乱节奏'}
    return repl.get(t,t)

def novelty_score(kind, value, usage, local_usage, freq):
    key=(kind,value)
    base=1.0/(1.0+usage[key])
    if local_usage[(kind,value)]>0: base-=1.2
    global_freq=max(1,freq.get(value,1))
    rarity=1.0/math.sqrt(global_freq)
    weights={'trajectory':1.3,'contact_name':1.25,'reaction_desc':1.2,'com_desc':1.15,'joint_path':1.05,'footwork':1.0,'body':0.95,'startup':0.85,'recovery':0.8}
    return base + rarity*weights.get(kind,1.0)

def sem_sim(a,b,threshold=0.74):
    a=norm(a); b=norm(b)
    if not a or not b:return False
    if a==b:return True
    A={a[i:i+2] for i in range(max(0,len(a)-1))}; B={b[i:i+2] for i in range(max(0,len(b)-1))}
    return bool(A and B and len(A&B)/len(A|B)>=threshold)

def sem_sim(a,b,threshold=0.74):
    a=norm(a); b=norm(b)
    if not a or not b:return False
    if a==b:return True
    A={a[i:i+2] for i in range(max(0,len(a)-1))}; B={b[i:i+2] for i in range(max(0,len(b)-1))}
    return bool(A and B and len(A&B)/len(A|B)>=threshold)

def choose_mechanics(comp, usage, local_usage, freq, desired_roles):
    candidate_kinds=['footwork','body','startup','joint_path','com_desc','trajectory','contact_name','recovery']
    scored=[]
    for k in candidate_kinds:
        v=comp.get(k,'')
        if not v:continue
        pref=1.0
        if 'entry' in desired_roles and k in ('footwork','trajectory','com_desc'):pref+=0.35
        if 'counter' in desired_roles and k in ('com_desc','trajectory'):pref+=0.4
        if 'bind' in desired_roles and k in ('contact_name','joint_path'):pref+=0.5
        if 'pressure' in desired_roles and k in ('body','footwork','trajectory'):pref+=0.35
        score=novelty_score(k,v,usage,local_usage,freq)*pref
        scored.append((score,k,v))
    scored.sort(reverse=True)
    chosen=[]; groups=set(); seen_text=[]
    group_map={'footwork':'movement','body':'movement','startup':'movement','joint_path':'movement','com_desc':'movement','trajectory':'line','contact_name':'line','recovery':'recovery'}
    for sc,k,v in scored:
        txt=phrase_for_component(comp,k)
        if not txt:continue
        g=group_map[k]
        if g in groups:continue
        if any(sem_sim(txt,x,0.72) for x in seen_text):continue
        chosen.append((k,v,txt)); groups.add(g); seen_text.append(txt)
        if len(chosen)>=2:break
    return chosen

def compile_action(action, actor_name, sequence_usage, shot_usage, freq, story_role, previous_family=None, semantic_override=None):
    comp=extract_components(action); fam=comp['family']
    # V10.18.4 single-source semantic closure: when SHOT_IR supplies a variant-authoritative
    # semantic core, do not reconstruct or overwrite that execution meaning from Action Components.
    authoritative = semantic_override or action.get('prompt_semantics') or {}
    authoritative_core = authoritative.get('core_sentence') if authoritative.get('variant_semantic_lock') else None
    variants=FAMILY_PHRASES.get(fam,FAMILY_PHRASES['probe'])
    idx=(sequence_usage['family'][fam] + shot_usage['family'][fam]) % len(variants)
    lead=f'{actor_name}{comp["weapon"]}{variants[idx]}'
    tactical=short_tactical(comp['tactical'])
    clauses=[authoritative_core if authoritative_core else lead]
    # Tactical cause is included only when it adds information not already encoded by the family.
    if tactical and not shot_usage['tactical_tail']:
        clauses.append(tactical)
    chosen=choose_mechanics(comp,sequence_usage['components'],shot_usage['components'],freq,[story_role])
    for k,v,txt in chosen:
        clauses.append(txt)
    # Remote-control wording is now owned by prompt_semantics.core_sentence.
    # Do not append a second reconstructed TELEKINETIC/SPIRIT_CONTROLLED clause.
    outcome=comp['outcome']; rd=phrase_for_component(comp,'reaction_desc')
    # Outcome is always visible; prefer the concrete reaction description when available.
    if outcome=='hit': clauses.append('命中后'+(rd or '对手身体或武器线被迫改变'))
    elif outcome=='block': clauses.append('被格挡后'+(rd or '双方短暂停顿并立即换线'))
    elif outcome=='dodge': clauses.append('对手闪出攻击线，'+(rd or '攻击者前冲动量继续释放'))
    elif outcome=='miss': clauses.append('落空后'+(rd or '攻击者带着原有惯性回收'))
    elif outcome=='bind': clauses.append('兵器短暂锁住，'+(rd or '双方借受力争夺下一条攻击线'))
    # Recovery is critical for non-hit outcomes, but is rendered as a visual action, never a state label.
    if outcome in ('block','dodge','miss','bind') and comp.get('recovery'):
        rv=phrase_for_component(comp,'recovery')
        if rv: clauses.append(rv)
    # Clean duplicated / near-duplicate clauses within the sentence.
    final=[]
    for c in clauses:
        # Preserve the authoritative variant core byte-for-byte; punctuation normalization must not
        # rewrite the single-source semantic payload before it reaches SHOT_IR/native output.
        if authoritative_core and c == authoritative_core:
            if c and c not in final: final.append(c)
            continue
        c=norm(c)
        if not c:continue
        if any(sem_sim(c,x,0.84) for x in final):continue
        final.append(c)
    sentence='；'.join(final)+'。'
    sequence_usage['family'][fam]+=1; shot_usage['family'][fam]+=1
    if tactical:
        sequence_usage['tactical'][tactical]+=1; shot_usage['tactical_tail'].append(tactical)
    for k,v,txt in chosen:
        sequence_usage['components'][(k,v)]+=1; shot_usage['components'][(k,v)]+=1
    sequence_usage['outcome'][outcome]+=1; shot_usage['outcome'][outcome]+=1
    # Reaction and recovery are tracked as distinct semantic signals even if not selected as primary mechanics.
    if comp.get('reaction_id'):
        sequence_usage['components'][('reaction',comp['reaction_id'])]+=1
        shot_usage['components'][('reaction',comp['reaction_id'])]+=1
    bundle={'family':fam,'tactical':tactical,'outcome':outcome,'selected_components':[(k,str(v)) for k,v,_ in chosen], 'reaction_id':comp.get('reaction_id',''),'recovery':str(comp.get('recovery',''))}
    return sentence,bundle

def dedup_component_metrics(bundles):
    total=0; repeated=0; max_each={}; seen=Counter()
    for b in bundles:
        for k,v in b['selected_components']:
            key=(k,v); seen[key]+=1; total+=1
    repeated=sum(n-1 for n in seen.values() if n>1)
    max_each=max(seen.values()) if seen else 0
    type_dups=0
    for i in range(len(bundles)):
        for j in range(i+1,len(bundles)):
            A=set(bundles[i]['selected_components']);B=set(bundles[j]['selected_components'])
            if not A or not B:continue
            jac=len(A&B)/len(A|B)
            if jac>=0.72:type_dups+=1
    return {'component_slots':total,'repeated_component_slots':repeated,'component_reuse_ratio':round(repeated/max(1,total),3),'max_component_usage':max_each,'semantic_bundle_collision_pairs':type_dups,'unique_component_slots':len(seen)}
