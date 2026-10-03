#!/usr/bin/env python3
"""V10.18.6 Weapon Signature Ultimate Switch.

Explicit trigger only: the user's input must contain the exact phrase “专属大招”.
The module overlays one weapon-specific ultimate technique onto an existing combat
Event. It never creates a new combat Event and never changes the top-level model
output structures.
"""
from copy import deepcopy

TRIGGER_PHRASE = "专属大招"
VERSION = "1.1"

NEGATION_PATTERNS = (
    "不要专属大招", "不需要专属大招", "关闭专属大招", "取消专属大招",
    "禁止专属大招", "禁用专属大招", "不要启用专属大招", "不启用专属大招",
)

# Outcome classes are knowledge-grounded in the current 10k action database.
# Signature Ultimate prefers a true offensive result and rejects recovery/defense-only events.
ULTIMATE_COMPATIBLE_OUTCOMES = {
    "徒手": {"hit"}, "剑": {"hit"}, "刀": {"hit"}, "枪": {"hit"}, "棍": {"hit"},
    "戟": {"hit"}, "双刃": {"hit"}, "链刃": {"hit", "bind"}, "弓": {"hit"},
    "法器": {"hit", "bind"}, "扇": {"hit"}, "鞭": {"hit", "bind"},
}
INCOMPATIBLE_OUTCOMES = {"dodge", "miss", "block"}

PROFILES = {
    "徒手": {
        "name": "天罡震界",
        "core": "以徒手近身爆发为核心，力量从脚底支撑经髋肩联动汇入拳掌，在极短距离内完成高度压缩后瞬间释放",
        "buildup": "重心下沉、呼吸收束、肩胯同步蓄力，周围尘雾与空气压力先被牵引向身体中心",
        "manifestation": "冲击力以环形压缩波从接触点向外扩散，形成清晰的内核冲击、环形中层压力和远端空气扰动",
        "trajectory": "沿角色真实身体轴完成贴身突进与单次决定性接触，不产生瞬移或无因位移",
        "contact": "接触瞬间短促锁定力量传递，目标出现明确受力、后撤或倒飞结果",
        "environment": "冲击波立即推动地面尘土、碎石和附近已存在的结构产生同步响应，破坏只发生在实际受力路径上",
        "vfx": "银白与角色既有能力色彩融合的高密度冲击环、空气压缩纹理、碎尘高速卷起，核心接触点最亮但绝不遮挡人物",
        "camera": "低机位贴身跟进→接触瞬间极短hit-stop→环形冲击波扩张时快速拉远→完整展示受力结果与环境反馈",
    },
    "剑": {
        "name": "九霄裂天剑",
        "core": "剑身沿单一主斩线完成极限蓄势与高速释放，剑气、实体剑刃和角色身体惯性保持同一攻击轴",
        "buildup": "剑尖压低后骤然回收，能量沿剑脊高速聚集，空气中的尘雾和光粒被斩线牵引成细长轨迹",
        "manifestation": "主剑气在剑刃前方形成高密度弧形斩线，随后扩展为多层同轴剑压与空间切割纹理",
        "trajectory": "一次决定性高速斩切，主轨迹清晰、切线明确，后续视觉层只放大同一攻击事件",
        "contact": "剑刃与目标或目标防线接触瞬间出现强烈切割阻力、剑身回弹和目标受力反馈",
        "environment": "斩线经过的既有地面、墙体或石柱立即沿真实攻击方向裂开，碎片按受力方向飞散",
        "vfx": "青白或角色既有能力色彩的超高密度剑气、墨色飞白、细碎金属火花与空间裂纹，形成清晰主剑线",
        "camera": "剑尖跟焦→极短侧向慢速环绕→接触锁定→沿剑气切线高速追出→拉远展示连续切割结果",
    },
    "刀": {
        "name": "赤霄断岳斩",
        "core": "刀势以重量和全身惯性为核心，后脚蹬地带动髋肩旋转，将全部动量集中到一次纵深重斩",
        "buildup": "刀锋回收贴近身体，重心压低，刀身周围气流被压缩成厚重弧面",
        "manifestation": "巨大而凝实的刀罡沿斩击方向爆发，外层形成扇形冲击面而非无因爆炸",
        "trajectory": "一次沉重、完整、不可逆的弧形重斩，刀路和身体旋转方向严格一致",
        "contact": "接触瞬间呈现刀锋阻力、武器回震、身体反作用和目标明显位移",
        "environment": "地面或已有岩石结构沿刀罡传播方向立即断裂，碎屑被冲击面卷起",
        "vfx": "赤金、暗红与角色既有能力色彩组成厚重刀罡、墨烟、火星和高速碎片，强调重量而不是纯光效",
        "camera": "低机位压迫构图→刀身近距离跟随→接触瞬间锁定→随刀罡向外拉远→展示扇形毁伤范围",
    },
    "枪": {
        "name": "苍龙贯界枪",
        "core": "枪势将身体重心、后腿蹬地、髋肩旋转和枪杆弹性压缩成一条高速贯穿轴",
        "buildup": "枪尖后收蓄力，枪杆产生明显弹性张力，能量沿枪身向枪尖连续汇聚",
        "manifestation": "枪尖释放出高密度螺旋枪芒，形成层层压缩的贯穿轨迹与长距离气流尾迹",
        "trajectory": "沿单一贯穿轴高速突进，轨迹清晰、方向稳定、接触点明确",
        "contact": "枪尖接触瞬间产生强烈轴向冲击、枪杆回弹与目标受力位移",
        "environment": "枪芒穿过的既有结构沿贯穿线立即产生穿透裂纹和碎片喷散",
        "vfx": "青苍、银白或角色既有能力色彩的螺旋枪芒、云气环、墨色飞白和高速粒子尾迹",
        "camera": "枪尖超近距离锁焦→沿枪身高速推进→接触瞬间短暂慢放→枪芒穿透方向高速拉远→展示最终结果",
    },
    "棍": {
        "name": "天崩镇岳棍",
        "core": "以棍体质量、旋转半径和全身惯性形成极限钝击，所有力量集中到一次决定性棍势释放",
        "buildup": "角色重心骤沉，棍身进入大幅蓄势轨道，周围空气和尘雾被旋转棍势卷成环状流场",
        "manifestation": "棍势释放时形成巨大的同轴冲击环与地面压力波，视觉重点是重量、惯性和范围扩散",
        "trajectory": "完整横扫或纵砸轨迹只对应一次真实攻击，不增加额外虚假棍击",
        "contact": "棍体接触瞬间出现强烈钝击回震、目标身体位移与棍身惯性延续",
        "environment": "地面、台阶、石柱等实际受力结构立即开裂、掀起碎片并向冲击方向扩散",
        "vfx": "金红、青金或角色既有能力色彩的巨型环形冲击波、尘浪、碎石流和墨色飞白，核心棍体始终清晰可见",
        "camera": "低机位环绕蓄势→棍身跟拍→接触瞬间超短hit-stop→沿冲击环快速拉远→展示大范围环境崩裂",
    },
    "戟": {
        "name": "霸极裂阵戟",
        "core": "戟刃以大幅横扫和身体旋转形成宽阔攻击面，将锋刃切线与惯性压力统一到一次破阵式终结",
        "buildup": "戟杆贴身回旋，角色重心快速转移，刃口周围能量沿弧线积聚",
        "manifestation": "宽阔弧形戟罡展开，形成前后连续但属于同一次攻击的多层切割压力",
        "trajectory": "单次大范围弧形扫击，保持完整身体旋转与脚下支撑关系",
        "contact": "戟刃接触目标防线时产生切割阻力、武器回震和明显横向位移",
        "environment": "攻击扇面内已经存在的障碍物被立即切开或掀翻，碎片沿横扫方向扩散",
        "vfx": "深金、赤金或角色既有能力色彩的弧形戟罡、金属火星、墨色飞白与高速碎屑",
        "camera": "侧后方低机位建立旋转轴→跟随戟刃弧线→接触锁定→随扇形冲击快速横移拉远→结果观察",
    },
    "双刃": {
        "name": "阴阳双极轮杀",
        "core": "双刃分别占据左右攻击轴，身体旋转将两把武器的相反轨迹汇聚成一次交叉终结",
        "buildup": "双刃分置身体两侧，重心快速换轴，能量分别沿两条轨迹积聚",
        "manifestation": "两条不同方向的刃光最终形成清晰交叉核心，视觉上表现双轴汇聚而非复制武器",
        "trajectory": "双刃各自完成一次真实运动并在同一终结窗口形成交叉攻击几何",
        "contact": "双刃接触目标或防线时产生连续但同一事件内的双向受力与中心回震",
        "environment": "交叉攻击区域内的既有结构沿两条真实刃线同步裂解",
        "vfx": "冷暖双相或角色既有能力色彩的交叉刃光、旋转残影、墨色飞白与碎片轨迹",
        "camera": "双刃分别跟焦→旋转过程中快速收束到交叉中心→接触锁定→从中心拉远展示X形结果",
    },
    "链刃": {
        "name": "九转天锁回刃",
        "core": "链刃进入受控脱手御器状态，保持真实质量与惯性，在九转环绕轨迹中完成锁定、变线、攻击与回收",
        "buildup": "角色先建立控制源并完成释放，链刃脱离手部动力链后沿外环加速，链节保持连续物理约束",
        "manifestation": "链刃绕目标形成高密度环形轨迹，随后从侧后方改变攻击轴，形成一次决定性收束攻击",
        "trajectory": "释放→环绕→变线→接触→结果→回收，所有轨迹连续可追踪，不允许瞬移",
        "contact": "链刃接触目标时展示链节拉伸、惯性传递、目标受力与回收张力",
        "environment": "链刃擦过的既有结构沿真实接触点产生断裂、碎屑与牵引响应",
        "vfx": "高密度流光链迹、墨色飞白、能量环、链节火星与高速碎片，视觉中心始终锁定真实链刃轨迹",
        "camera": "脱手瞬间近景→绕目标高速跟拍→变线时短暂环绕→接触锁定→跟随链刃回收并拉远展示结果",
    },
    "弓": {
        "name": "天穹贯日箭",
        "core": "弓弦张力、角色背部与肩胛稳定和箭矢质量共同形成极限远射，将全部储能集中到单箭释放",
        "buildup": "弓弦持续拉满，箭矢周围空间气流被压缩，远端环境光线开始被箭尖牵引",
        "manifestation": "箭矢释放后形成清晰贯日轨迹，高密度能量沿箭轴压缩成单一远射核心",
        "trajectory": "一箭完成高速远距离飞行、目标锁定与单次贯穿结果，不生成额外箭矢",
        "contact": "箭尖接触瞬间形成极短的接触锁定、穿透阻力与目标位移反馈",
        "environment": "远端既有目标结构在箭矢真实接触点立即产生贯穿裂纹和碎片扩散",
        "vfx": "角色既有能力色彩的极亮箭矢核心、长距离光轨、云层切开、细密粒子和墨色飞白，但避免纯白过曝",
        "camera": "拉弓近景→箭尖微距蓄能→释放后高速追箭→接触瞬间短促慢放→大幅拉远展示远端结果",
    },
    "法器": {
        "name": "万象镇域天轮",
        "core": "法器悬浮并建立角色控制源，以法器自身质量与既有能力形成旋转阵域，将攻击、限制和环境响应统一到一个终结事件",
        "buildup": "法器离手悬浮，符文逐层点亮，周围空间形成同心阵环，能量向阵心压缩",
        "manifestation": "多层阵环同时展开但共享同一中心，形成巨大领域式压迫结构，法器本体始终可辨识",
        "trajectory": "阵域扩张→目标受限→法器核心收束→决定性接触/压制结果→能量回收",
        "contact": "阵域与目标接触时呈现明确压力传递、身体反应与空间位移，不使用无因瞬移",
        "environment": "阵域覆盖范围内的既有地面、石柱、碎片和尘雾同步响应，结构破坏服从真实受力区域",
        "vfx": "巨型符文阵、流动金线、角色既有元素、墨色飞白、粒子流、空间波纹和多层能量环，视觉密度拉满但主体清晰",
        "camera": "法器微距→环绕阵心快速升高→拉远揭示完整领域→压回目标接触点→最终俯视结果构图",
    },
    "扇": {
        "name": "九霄风雷扇",
        "core": "扇面展开后以真实摆臂与扇体惯性形成单次极限风压释放，风场沿扇面方向连续扩张",
        "buildup": "扇面收拢、身体转髋蓄势，周围空气与尘雾被持续吸向扇锋",
        "manifestation": "一次大范围扇形风压与既有元素能量同步释放，形成清晰推进波前",
        "trajectory": "扇面完成一次决定性展开，风压沿真实扇面法线推进",
        "contact": "风压接触目标时产生明确的整体受力、后撤与环境气流反馈",
        "environment": "既有尘土、碎石、旗幡或轻质结构沿风压方向立即响应，重型结构仅在实际冲击足够时破坏",
        "vfx": "高密度风纹、云气、墨色飞白、粒子流和角色既有元素色彩，形成巨型扇形视觉波面",
        "camera": "扇面微距→低机位展开→跟随风压波前快速推进→拉远展示扇形影响范围",
    },
    "鞭": {
        "name": "九霄雷链破界",
        "core": "鞭体沿真实柔性链条传播速度与角色手臂、肩胯动力链同步，完成一次极限抽击与回收",
        "buildup": "鞭体先收束蓄势，波动从握持端沿鞭身连续传递至鞭梢",
        "manifestation": "鞭梢形成高速弧形能量尾迹，在接触窗口集中释放全部柔性动量",
        "trajectory": "完整展示鞭身波传播、鞭梢加速、接触和回收，不允许无因瞬移或硬直穿透",
        "contact": "鞭梢接触目标时出现明确局部受力、身体反应与回弹",
        "environment": "真实鞭梢接触到的既有结构产生即时裂纹、碎片或表面冲击痕迹",
        "vfx": "高密度弧形流光、墨色飞白、空气切割纹理和细碎火星，强调柔性高速轨迹",
        "camera": "鞭身近景跟随波传播→鞭梢超近景→接触锁定→沿回弹轨迹跟回角色→拉远观察结果",
    },
}

ALIASES = {
    "徒手": "徒手", "拳": "徒手", "掌": "徒手",
    "剑": "剑", "刀": "刀", "枪": "枪", "矛": "枪", "棍": "棍", "棒": "棍",
    "戟": "戟", "双刃": "双刃", "双刀": "双刃", "双剑": "双刃",
    "链刃": "链刃", "链": "链刃", "弓": "弓", "法器": "法器", "扇": "扇", "鞭": "鞭",
}

def find_input_text(value):
    """Collect user-facing prompt strings without reading internal diagnostics as trigger input."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out=[]
        for k,v in value.items():
            if k in {'user_prompt','prompt','input_prompt','request','user_request','instruction','instructions','text','description','objective','requirements'}:
                out.extend(find_input_text(v))
        return out
    if isinstance(value, list):
        return [s for x in value for s in find_input_text(x)]
    return []

def detect_switch(scenario):
    texts=find_input_text(scenario)
    positive=any(TRIGGER_PHRASE in t for t in texts)
    negated=any(any(p in t for p in NEGATION_PATTERNS) for t in texts)
    enabled=bool(positive and not negated)
    return {
        'enabled':enabled,
        'trigger_phrase':TRIGGER_PHRASE if enabled else None,
        'negated':negated,
        'positive_phrase_present':positive,
        'source_fields':[k for k in ('user_prompt','prompt','input_prompt','request','user_request','instruction','instructions','text','description','requirements') if k in scenario]
    }

def normalize_weapon(weapon):
    w=str(weapon or '')
    for alias,cat in sorted(ALIASES.items(), key=lambda kv: len(kv[0]), reverse=True):
        if alias in w:
            return cat
    return w if w in PROFILES else None

def choose_profile(weapon):
    cat=normalize_weapon(weapon)
    if cat in PROFILES:
        return cat, deepcopy(PROFILES[cat])
    return None, None

def ultimate_candidate_score(event, action, weapon_category, index, total, requested_actor=None):
    """Score an existing Event for Signature Ultimate overlay without creating a new Event."""
    if not action or not weapon_category:
        return (-999.0, ['missing_action_or_weapon'])
    outcome=str(event.get('outcome') or action.get('opponent_response',{}).get('outcome_class') or '').lower()
    allowed=ULTIMATE_COMPATIBLE_OUTCOMES.get(weapon_category, {'hit'})
    if outcome in INCOMPATIBLE_OUTCOMES:
        return (-999.0, [f'incompatible_outcome:{outcome}'])
    if outcome not in allowed:
        return (-100.0, [f'unsupported_outcome:{outcome}'])
    score=0.0; reasons=[]
    if outcome=='hit': score+=70; reasons.append('direct_offensive_result')
    elif outcome=='bind': score+=45; reasons.append('weapon_compatible_control_result')
    impact=float((event.get('impact_profile') or {}).get('score',0) or 0)
    score += min(20.0, impact*0.2); reasons.append('impact_payoff') if impact else None
    if event.get('highlight'): score+=6; reasons.append('highlight_candidate')
    # Later events are a tie-breaker only, never the primary selector.
    score += min(4.0, max(0,total-index)*0.25)
    if requested_actor and event.get('actor_id')==requested_actor: score+=3; reasons.append('requested_actor')
    return (score,reasons)

def select_signature_ultimate_event(action_events, selected_payloads, actors, requested_actor=None, requested_weapon_actor=None):
    """Return (event, action, diagnostics) for the highest-value compatible existing Event."""
    candidates=[]
    total=len(action_events)
    for idx,event in enumerate(action_events):
        aid=event.get('actor_id')
        if requested_actor and aid!=requested_actor:
            continue
        if requested_weapon_actor and aid!=requested_weapon_actor:
            continue
        actor=actors.get(aid,{}) or {}
        weapon_category=normalize_weapon(actor.get('weapon'))
        action=selected_payloads.get(event.get('action_id'))
        score,reasons=ultimate_candidate_score(event,action,weapon_category,idx,total,requested_actor)
        if score>-90:
            candidates.append((score,idx,event,action,weapon_category,reasons))
    if not candidates:
        return None,None,{'status':'NO_COMPATIBLE_EVENT','candidate_count':0}
    candidates.sort(key=lambda x:(x[0],x[1]),reverse=True)
    score,idx,event,action,cat,reasons=candidates[0]
    return event,action,{'status':'SELECTED','candidate_count':len(candidates),'score':score,'index':idx,'weapon_category':cat,'reasons':reasons,'candidate_event_ids':[x[2].get('event_id') for x in candidates[:8]]}

def apply_signature_ultimate(action, actor_name, weapon, trigger):
    """Overlay the signature ultimate onto an existing selected action; no Event is created."""
    if not trigger.get('enabled'):
        return action, None
    cat, profile=choose_profile(weapon)
    if not profile:
        return action, None
    a=deepcopy(action)
    ps=deepcopy(a.get('prompt_semantics') or {})
    text=(
        f"{actor_name}释放{profile['name']}：{profile['core']}。"
        f"起手蓄势：{profile['buildup']}。"
        f"招式显现：{profile['manifestation']}。"
        f"攻击轨迹：{profile['trajectory']}。"
        f"核心接触：{profile['contact']}。"
        f"环境结果：{profile['environment']}。"
        f"视觉特效：{profile['vfx']}。"
        f"终极摄影：{profile['camera']}。"
        "视觉强度为终极级，高密度但保持人物、武器、接触点和攻击轨迹清晰；所有炫酷效果必须服务于同一真实战斗事件。"
    )
    ps['signature_ultimate'] = True
    ps['signature_ultimate_version'] = VERSION
    ps['signature_ultimate_trigger'] = TRIGGER_PHRASE
    ps['signature_ultimate_weapon_category'] = cat
    ps['signature_ultimate_name'] = profile['name']
    ps['signature_ultimate_core_sentence'] = text
    ps['signature_ultimate_visual_profile'] = profile
    ps['signature_ultimate_single_event_lock'] = True
    ps['signature_ultimate_contact_result_lock'] = True
    ps['signature_ultimate_continues_combat'] = True
    a['prompt_semantics']=ps
    a['signature_ultimate']={
        'enabled':True,'weapon_category':cat,'name':profile['name'],'trigger':TRIGGER_PHRASE,
        'core_sentence':text,'visual_profile':profile,'source':'WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0',
        'no_new_event':True,'single_event_lock':True,'contact_result_lock':True,'continues_combat':True,
    }
    return a, a['signature_ultimate']
