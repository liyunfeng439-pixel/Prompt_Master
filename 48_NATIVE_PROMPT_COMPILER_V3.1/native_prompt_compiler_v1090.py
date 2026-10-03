#!/usr/bin/env python3
import argparse,json,hashlib,re,sys,importlib.util
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
engine_path=ROOT/'43_COMBAT_SEMANTIC_DIVERSITY_ENGINE_V1.0/semantic_diversity_engine_v1030.py'
spec=importlib.util.spec_from_file_location('sde',engine_path); sde=importlib.util.module_from_spec(spec); spec.loader.exec_module(sde)

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]

def action_map(runtime):
    payloads=runtime.get('selected_action_payloads') or runtime.get('_actions_cache') or []
    if isinstance(payloads,dict): return payloads
    return {a['action_id']:a for a in payloads}

def actor_registry(canon, shot_ir):
    # Only explicit actor records are eligible; never treat arbitrary Canon metadata as a character.
    actors={}
    for aid,v in canon.items():
        if isinstance(v,dict) and ('name' in v or 'weapon' in v or v.get('id')==aid): actors[aid]=v
    for sh in shot_ir.get('shots',[]):
        for aid,v in (sh.get('actor_state') or {}).items():
            if aid not in actors and isinstance(v,dict) and ('name' in v or 'weapon' in v): actors[aid]=v
    return actors

def identity_text(canon, shot_ir):
    actors=actor_registry(canon,shot_ir); parts=[]
    for aid,v in actors.items():
        name=v.get('name',aid); weapon=v.get('weapon') or '其锁定武器'
        parts.append(f'{name}保持参考资产身份与外观连续，始终使用{weapon}。')
    return ''.join(parts) or '保持所有角色参考资产身份、外观与武器连续。'

def scene_text(shot_ir,runtime):
    spatial=shot_ir.get('spatial_provenance') or {}
    note=spatial.get('scene_description') or spatial.get('location') or '' if isinstance(spatial,dict) else ''
    if isinstance(note,dict): note=''
    note=str(note).strip()
    return '保持用户确认的战斗场景与空间关系连续；所有位置变化必须由动作、受力或明确位移产生。' + (f' 场景参考：{note}' if note else '')

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
    return {'combat_open':'近距离跟随首次有效接触，迅速建立双方间距。','counter_exchange':'横移跟随攻击线变化，保留闪避与反击方向。','pressure_shift':'绕侧跟拍，突出控制、换线与攻守转换。','high_intensity_exchange':'低机位快速跟进，连续接触与受击反应保持可读。','escalation':'先交代空间变化，再追入能量与环境反馈。','final_build':'压近蓄力动作后后撤，容纳完整终局形态。','final_clash_result':'完整观察最终接触、结果与结束后的稳定状态。','recovery_link':'跟随受力后的恢复与重新建立支撑。','impact_payoff':'贴近亮点动作的真实攻击轴跟拍，完整保留启动、加速、接触、受力、位移和环境结果；接触瞬间短促强化冲击视觉，随后立即回到结果。'}.get(role,'沿主要攻击线跟拍，接触时短促强调，恢复时回到人物重心。')
def fallback_vfx(role):
    return {'combat_open':'只强调首次接触产生的火花、气流或材质反馈。','counter_exchange':'残影服从变线与惯性，不遮挡武器接触。','pressure_shift':'受力方向推动气流、尘雾或能量反馈。','high_intensity_exchange':'冲击特效只在接触瞬间增强，保留身体与武器可读性。','escalation':'能量与环境反馈随动作轴同步升级。','final_build':'终局能量由本体蓄力产生并与真实动作同步。','final_clash_result':'最终冲击产生可见结果，随后特效衰减进入结果观察。','recovery_link':'只表现受力后的尘雾、衣物与能量余波。','impact_payoff':'冲击特效只作为真实接触、受力与环境反馈的视觉证据；不得用爆炸、闪光或震屏替代身体/武器的实际力量传递。'}.get(role,'特效只解释已经发生的接触、受力和环境响应。')

def event_sentence(event, runtime, canon):
    typ=event.get('type',''); actors=actor_registry(canon,{'shots':[]})
    if typ=='recovery':
        aid=event.get('actor_id'); name=actors.get(aid,{}).get('name',aid or '角色'); return f'{name}顺着前一动作的惯性完成恢复，重新建立支撑与下一条攻击线。'
    if typ=='result_lock': return '最终碰撞结果被锁定，身体、武器与环境进入稳定的结果状态，不再产生新的攻击事件。'
    if typ=='ending':
        mode=event.get('mode','open'); d=actors.get(event.get('defeated_actor'),{}).get('name',event.get('defeated_actor','')); v=actors.get(event.get('victor'),{}).get('name',event.get('victor',''))
        if mode=='victory' and v and d: return f'{v}保持已锁定的终局优势，{d}保持已锁定的失败状态。'
        if mode=='escape' and d and v: return f'{d}脱离战场，{v}停止追击并保持终局状态。'
        if mode=='draw': return '双方停在已锁定的终局状态，胜负不再推进，镜头只观察余波与彼此状态。'
        return event.get('observation') or '终局状态已经锁定，镜头只观察已发生结果、人物状态与环境余波，不新增战斗事件。'
    if typ=='ability_clash':
        ns=names_for_ids(event.get('actor_ids',[]),canon); return f'{"与".join(ns) if ns else "双方"}的终局能力沿各自真实攻击轴发生最终接触，力量集中于接触点释放。'
    return ''

def impact_payoff_sentence(event, action, actor_name):
    """Compile only explicit impact evidence; never invent anatomy, damage, or secondary collision."""
    if not event.get('highlight'): return ''
    ip=event.get('impact_profile') or {}; em=action.get('execution_model',{}) or {}; phy=action.get('physics',{}) or {}; opp=action.get('opponent_response',{}) or {}; env=action.get('environment',{}) or {}
    sf=ip.get('highlight_semantic_fidelity') or (ip.get('choreography') or {}).get('semantic_fidelity') or {}
    if sf.get('fidelity_required'):
        return '底层物理与因果仍受动作知识约束；当亮点指令明确指定接触部位、力量传递、身体反馈、位移或环境结果时，以该明确指令为最终表现语义，不重复输出会造成冲突的通用动作知识字段。'
    cg=ip.get('contact_geometry') or {}; ft=ip.get('force_transfer') or {}; parts=[]
    force_map={'weight_transfer':'重心转移','hip_drive':'髋部驱动','spiral_chain':'螺旋链传力','center_of_mass':'重心路径','linear_drive':'线性推进','ground_reaction':'地面反作用力'}
    target=action.get('target',{}).get('preferred') if isinstance(action.get('target',{}),dict) else None
    if target: parts.append(f'明确接触{target}')
    if cg.get('mechanics'): parts.append(f'接触几何：{cg["mechanics"]}')
    source=force_map.get(str(ft.get('force_source')),str(ft.get('force_source') or ''))
    if source: parts.append(f'力量来源：{source}')
    if ft.get('weight_transfer'): parts.append(f'重心传递：{ft["weight_transfer"]}')
    if ft.get('collision'): parts.append(f'碰撞结果：{ft["collision"]}')
    if opp.get('body_mechanics'): parts.append(f'身体反馈：{opp["body_mechanics"]}')
    if opp.get('primary',{}).get('description'): parts.append(f'受击结果：{opp["primary"]["description"]}')
    displacement=ip.get('displacement')
    if displacement and displacement not in {'state_derived','UNKNOWN','unknown'}: parts.append(f'位移结果：{displacement}')
    surface=env.get('surface',{}) if isinstance(env,dict) else {}
    if surface.get('response'): parts.append(f'环境反馈：{surface["response"]}')
    secondary=ip.get('secondary_collision')
    anchor=ip.get('environment_anchor')
    if secondary:
        parts.append(f'二次环境碰撞：{secondary}'+(f'，锚点为{anchor}' if anchor else ''))
    if not parts: return ''
    material='若参考资产存在衣物、护具、绑带或饰品，只随已发生接触同步出现合理的受力褶皱、绷紧、摆动或回弹，不新增结构事实。'
    return f'{actor_name}的亮点冲击动作完整呈现：'+'；'.join(parts)+'。'+material+' 接触后立即进入受击位移和结果状态，镜头只强化这一已经发生的力量传递，不新增攻击、伤害或碰撞。'

def highlight_semantic_fidelity_sentence(event):
    """Compile explicit Highlight Canon facts without inventing new combat events."""
    ip=event.get('impact_profile') or {}
    sf=ip.get('highlight_semantic_fidelity') or (ip.get('choreography') or {}).get('semantic_fidelity') or {}
    if not sf or not sf.get('fidelity_required'): return ''
    parts=[]; a=sf.get('action') or {}; cam=sf.get('camera') or {}; segs=sf.get('temporal_segments') or []; layers=sf.get('vfx_layers') or {}
    labels=[('approach','接近'),('entry','进入'),('rotation','旋转'),('rotation_count','旋转次数'),('limb_action','肢体动作'),('contact','接触动作'),('contact_target','接触目标'),('contact_point','接触点'),('force_transfer','力量传递'),('body_response','身体反馈'),('displacement','位移结果'),('environment_result','环境结果')]
    for k,lab in labels:
        if a.get(k) is not None: parts.append(f'{lab}：{a[k]}')
    if segs: parts.append('明确时间段：'+'；'.join('—'.join(f'{k}={v}' for k,v in x.items()) for x in segs))
    cam_labels=[('angle','机位'),('height','机位高度'),('orbit','环绕'),('focus','焦点'),('focus_lock','焦点锁定'),('contact_lock','接触锁定'),('impact_follow','冲击跟随'),('result_observe','结果观察')]
    for k,lab in cam_labels:
        if cam.get(k) is not None: parts.append(f'{lab}：{cam[k]}')
    layer_labels={'core':'核心冲击层','middle':'中层冲击层','outer':'外层冲击层'}
    for lk in ('core','middle','outer'):
        v=layers.get(lk)
        if not v: continue
        desc='；'.join(f'{k}={val}' for k,val in v.items()) if isinstance(v,dict) else str(v)
        parts.append(f'{layer_labels[lk]}：{desc}')
    if sf.get('result_chain'): parts.append('结果链：'+'→'.join(map(str,sf['result_chain'])))
    if sf.get('critical_facts'): parts.append('必须保留事实：'+'；'.join(map(str,sf['critical_facts'])))
    if sf.get('negative_constraints'): parts.append('亮点负约束：'+'；'.join(map(str,sf['negative_constraints'])))
    return ('亮点语义保真：'+'；'.join(parts)+'。上述内容属于同一既有战斗Event的明确指令，不得拆成新攻击，不得新增接触或二次碰撞。') if parts else ''

def highlight_choreography_sentence(event, shot):
    if not event.get('highlight'): return ''
    hc=(event.get('impact_profile') or {}).get('highlight_choreography') or shot.get('highlight_choreography') or {}
    if not hc: return ''
    phases=hc.get('tempo_phases') or []
    phase_map={
        'approach_normal':'正常速度逼近', 'entry_slow':'进入慢动作并展示动作蓄势',
        'contact_slow':'接触前后持续慢放并锁定接触点', 'impact_normal':'命中瞬间速度恢复正常',
        'result_fast':'立即高速跟随受击位移与环境结果', 'result_observe':'转入稳定结果观察'
    }
    tempo='→'.join(phase_map.get(x,x) for x in phases)
    cam=hc.get('camera') or {}; cam_parts=[]
    if cam.get('angle'): cam_parts.append(f"{cam['angle']}")
    if cam.get('orbit'): cam_parts.append('极慢速环绕')
    if cam.get('focus'): cam_parts.append(f"焦点锁定{cam['focus']}")
    if cam.get('result_follow',True): cam_parts.append('命中后高速跟随结果')
    stack={'core':'核心冲击层','middle':'中层环形冲击层','outer':'外层能量碎裂层'}
    layers='、'.join(stack.get(x,x) for x in hc.get('impact_stack',[]))
    result='→'.join(hc.get('result_chain',[]))
    parts=[]
    if tempo: parts.append('时间流速：'+tempo)
    if cam_parts: parts.append('摄影：'+'；'.join(cam_parts))
    if layers: parts.append('冲击层级：'+layers)
    if result: parts.append('结果链：'+result)
    if not parts: return ''
    return '亮点编舞（同一Event）：'+'；'.join(parts)+'。保持单次接触与单次结果，不新增攻击、命中或二次碰撞。'

def narrative_sentence(event):
    n=event.get("narrative") or {}
    if not n: return ""
    reason=(n.get("reason_for_action") or "").strip()
    intent=(n.get("combat_intent") or "").strip()
    source=n.get("reason_source") or ""
    nxt=(n.get("next_expected_state") or "").strip()
    if not reason and not intent: return ""
    if source=="explicit_intent": text=f"当前动作服务于{intent}"
    elif source=="explicit_tactical_problem": text=f"针对当前战术问题，选择该动作：{intent.replace('解决战术问题：','')}"
    elif source=="previous_result": text=f"上一动作的结果推动了下一步调整：{intent}"
    elif source=="phase_goal": text=f"为推进当前战斗阶段，采取这一动作：{intent.replace('推进当前战斗阶段目标：','')}"
    elif source=="spatial_state": text=f"依据当前交战空间，采用这一攻击线：{intent}"
    else: text=f"动作延续当前有效战斗因果：{intent}"
    if nxt and nxt not in text: text += f"，随后进入{nxt}"
    return text+'。'

def narrative_curve_summary(runtime):
    curve=runtime.get("narrative_curve") or {}; segs=curve.get("segments") or []
    if not segs: return "战斗叙事随实际事件因果推进，不使用固定剧情模板。"
    labels={"establish":"建立冲突","test":"力量与防线试探","tactical_shift":"战术转折","escalation":"强度升级","climax":"高潮碰撞","resolution":"结果收束"}
    return " → ".join(labels.get(s.get("role"),s.get("role","战斗推进")) for s in segs)

def narrative_intent_summary(runtime):
    events=[e for e in runtime.get("events",[]) if e.get("type")=="action_result"]
    intents=[]
    for e in events:
        n=e.get("narrative") or {}; intent=(n.get("combat_intent") or "").replace("解决战术问题：","").replace("推进当前战斗阶段目标：","").strip()
        if intent and intent not in intents: intents.append(intent)
    return " → ".join(intents[:6]) if intents else "按实际战斗状态与结果推进"

def render_action(a,actor_name,seq_usage,shot_usage,freq,role,semantic_override=None):
    sentence,bundle=sde.compile_action(a,actor_name,seq_usage,shot_usage,{k:Counter(v) for k,v in freq.items()},role,None,semantic_override=semantic_override)
    return sentence,bundle

def compile(runtime,shot_ir):
    canon=runtime.get('canon',{}); acts=action_map(runtime); contracts={c.get('event_id'):c for c in runtime.get('action_contracts',[]) if c.get('event_id')}; abilities=runtime.get('ability_contracts',[]); events={e.get('event_id'):e for e in runtime.get('events',[])}
    common='8K电影级3D CG写实，次世代PBR物理材质，UE5级电影渲染，16:9横画幅，60fps，HDR，真实全局光照与体积光，电影级景深与自然运动模糊，人物、衣物、毛发、武器材质保持高精度与真实重量、惯性、受力反馈。'
    identity=identity_text(canon,shot_ir); scene=scene_text(shot_ir,runtime); actors=actor_registry(canon,shot_ir)
    outputs={}; metrics={}
    idx=runtime.get('_semantic_freq',{})
    action_event_count=sum(1 for e in runtime.get('events',[]) if e.get('type')=='action_result')
    narrative_surface_allowed=action_event_count>=5
    for model in ('universal','seedance_2_5','minimax_h3'):
        seq_usage={'family':Counter(),'tactical':Counter(),'components':Counter(),'outcome':Counter()}; chosen=[]; trace=[]; shot_records=[]; last_narrative_role=None; last_narrative_intent=None
        shot_blocks=[]
        for sh in shot_ir.get('shots',[]):
            clauses=[]; local={'family':Counter(),'tactical_tail':[],'components':Counter(),'outcome':Counter()}
            for eid in sh.get('event_ids',[]):
                c=contracts.get(eid)
                if c and c.get('knowledge_action_id') in acts:
                    a=acts[c['knowledge_action_id']]; actor_id=c.get('actor_identity'); actor=actor_registry(canon,shot_ir).get(actor_id,{})
                    semantic_override={}
                    for chain_item in sh.get('action_chain',[]):
                        if chain_item.get('event_id')==eid:
                            semantic_override=chain_item.get('prompt_semantics') or {}
                            break
                    sentence,bundle=render_action(a,actor.get('name',actor_id or '角色'),seq_usage,local,idx,sh.get('story_function','combat_execution'),semantic_override=semantic_override)
                    ultimate_core=(semantic_override.get('signature_ultimate_core_sentence') or '').strip()
                    if semantic_override.get('signature_ultimate') and ultimate_core:
                        sentence += ' '+ultimate_core
                    sf=(events.get(eid,{}).get('impact_profile') or {}).get('highlight_semantic_fidelity') or {}
                    if events.get(eid,{}).get('highlight') and sf.get('fidelity_required') and sf.get('action'):
                        ha=sf.get('action') or {}
                        actor_name=actor.get('name',actor_id or '角色')
                        sentence=f'{actor_name}严格执行亮点指令动作：'+ '；'.join(str(ha[k]) for k in ('approach','entry','rotation','limb_action','contact','contact_target','force_transfer','body_response','displacement','environment_result') if ha.get(k) is not None) + '。'
                    impact=impact_payoff_sentence(events.get(eid,{}),a,actor.get('name',actor_id or '角色'))
                    if impact: sentence=sentence+' '+impact
                    choreography=highlight_choreography_sentence(events.get(eid,{}),sh)
                    if choreography: sentence=sentence+' '+choreography
                    fidelity=highlight_semantic_fidelity_sentence(events.get(eid,{}))
                    if fidelity: sentence=sentence+' '+fidelity
                    evn=events.get(eid,{})
                    nn=evn.get('narrative') or {}
                    current_role=nn.get('phase_role')
                    current_intent=nn.get('combat_intent')
                    surface_narrative=narrative_surface_allowed and ((current_intent and current_intent!=last_narrative_intent) or (bool(evn.get('highlight')) and current_intent!=last_narrative_intent))
                    narrative=narrative_sentence(evn) if surface_narrative else ''
                    if narrative: sentence=sentence+' '+narrative
                    if current_role: last_narrative_role=current_role
                    if current_intent and surface_narrative: last_narrative_intent=current_intent
                    clauses.append(sentence); chosen.append({'shot_id':sh['shot_id'],'event_id':eid,**bundle}); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'action','sentence':sentence,'story_role':sh.get('story_function'),'bundle':bundle,'highlight':bool(events.get(eid,{}).get('highlight')),'signature_ultimate':bool(semantic_override.get('signature_ultimate')),'signature_ultimate_name':semantic_override.get('signature_ultimate_name'),'signature_ultimate_core_sentence':semantic_override.get('signature_ultimate_core_sentence',''),'semantic_source':'SHOT_IR.prompt_semantics' if semantic_override.get('signature_ultimate') or semantic_override.get('variant_semantic_lock') else 'Action_Components'}); continue
                found=False
                for ac in abilities:
                    if eid in ac.get('ability_event_ids',[]):
                        txt=ability_sentence(ac,canon,eid)
                        if txt: clauses.append(txt); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':'ability'}); found=True; break
                if found: continue
                txt=event_sentence(events.get(eid,{'event_id':eid}),runtime,canon)
                if txt: clauses.append(txt); trace.append({'shot_id':sh['shot_id'],'event_id':eid,'type':events.get(eid,{}).get('type','event'),
                                  'semantic_source':'SHOT_IR.prompt_semantics' if semantic_override.get('variant_semantic_lock') else 'Action_Components',
                                  'variant_semantic_core':semantic_override.get('core_sentence','') if semantic_override.get('variant_semantic_lock') else ''})
            uniq=[]
            for cl in clauses:
                if not any(sde.sem_sim(cl,u,0.86) for u in uniq): uniq.append(cl)
            txt=' '.join(uniq)
            camera=sh.get('camera') or fallback_camera(sh.get('story_function',''))
            physics=sh.get('physics') or '遵循准备→启动→加速→接触/避让→受力→结果→恢复的连续物理链。'
            vfx=sh.get('vfx') or fallback_vfx(sh.get('story_function',''))
            continuity=(sh.get('continuity') or '保持角色身份、武器、空间方向、战损与前后状态连续。').replace('inferred provenance','空间连续性').replace('provenance','空间连续性')
            damage=sh.get('damage_state') or {}
            sp=sh.get('spatial_state') or {}
            actor_sp=sp.get('actor_states_after') or sp.get('actor_states') or {}
            spatial_parts=[]
            for aid,av in actor_sp.items():
                spatial_parts.append(f'{actors.get(aid,{}).get("name",aid)}当前位于{av.get("layer","未知空间层")}、空间锚点{av.get("anchor","未知")}、支撑状态{av.get("support","未知")}')
            rel=(sp.get('relative_height_before') or '未知高度关系')+'→'+(sp.get('relative_height_after') or '未知高度关系')
            spatial_text=('空间关系：'+'；'.join(spatial_parts)+f'；相对高度变化为{rel}；相对距离{sp.get("relative_distance_before","UNKNOWN")}→{sp.get("relative_distance_after","UNKNOWN")}；攻击轴{sp.get("attack_axis_before","UNKNOWN")}→{sp.get("attack_axis_after","UNKNOWN")}；移动向量{sp.get("movement_vector_before","UNKNOWN")}→{sp.get("movement_vector_after","UNKNOWN")}。' if spatial_parts else '空间关系保持连续，未知位置不得虚构。')
            shot_records.append({'shot_id':sh['shot_id'],'duration':sh.get('duration',0),'story_function':sh.get('story_function',''),'text':txt,'camera':camera,'camera_resolver':sh.get('camera_resolver'),'physics':physics,'vfx':vfx,'vfx_resolver':sh.get('vfx_resolver'),'continuity':continuity,'damage':damage,'ending':sh.get('ending_state',{}),'spatial':spatial_text,'highlight_events':[e for e in sh.get('event_ids',[]) if events.get(e,{}).get('highlight')],'highlight_payoff':[(events.get(e,{}).get('impact_profile') or {}) for e in sh.get('event_ids',[]) if events.get(e,{}).get('highlight')],'highlight_choreography':sh.get('highlight_choreography'),'highlight_semantic_fidelity':[events.get(e,{}).get('impact_profile',{}).get('highlight_semantic_fidelity',{}) for e in sh.get('event_ids',[]) if events.get(e,{}).get('highlight')],'camera_vfx_provenance':{'camera_resolver':sh.get('camera_resolver'),'vfx_resolver':sh.get('vfx_resolver')},'spatial_state':sp,'narrative':{'events':[events.get(e,{}).get('narrative',{}) for e in sh.get('event_ids',[]) if events.get(e,{}).get('narrative')],'curve_role':next((events.get(e,{}).get('narrative',{}).get('phase_role') for e in sh.get('event_ids',[]) if events.get(e,{}).get('narrative')),None)}})
        final=runtime.get('ending',{})
        actors=actor_registry(canon,shot_ir); actor_lines=[]
        for aid,v in actors.items(): actor_lines.append(f'- {v.get("name",aid)}：保持参考资产身份与{v.get("weapon") or "锁定武器"}一致')
        shot_lines=[]
        for s in shot_records:
            action_text=s['text'] or '延续上一状态并进入下一有效战斗因果。'
            shot_lines.append((s,action_text))
        mode=final.get('mode','open') if final else 'open'
        if mode=='victory' and final.get('victor') and final.get('defeated_actor'):
            ending_text=f"{actors.get(final.get('victor'),{}).get('name',str(final.get('victor')))}保持已锁定的终局优势，{actors.get(final.get('defeated_actor'),{}).get('name',str(final.get('defeated_actor')))}保持已锁定的失败状态。"
        elif mode=='escape' and final.get('victor') and final.get('defeated_actor'):
            ending_text=f"{actors.get(final.get('defeated_actor'),{}).get('name',str(final.get('defeated_actor')))}脱离战场，{actors.get(final.get('victor'),{}).get('name',str(final.get('victor')))}停止追击并保持终局状态。"
        elif mode=='draw':
            ending_text=final.get('observation') or '双方未分胜负，保持已锁定终局状态，只观察人物与环境余波。'
        else:
            ending_text=final.get('observation') or '终局状态已经锁定，只观察已发生结果与环境余波，不新增战斗事件。'
        if model=='universal':
            lines=['Generation Goal: 以战斗因果为主体；30秒核心分镜段Beat不超过7个，每个Beat根据可读性使用1–3个连续镜头Shot，连续事件优先于展示。叙事曲线：'+narrative_curve_summary(runtime)+'；战术推进：'+narrative_intent_summary(runtime),'Global Visual Direction: '+common,'Asset Lock: '+identity,'Scene / Spatial Continuity: '+scene,'Time / Shot Sequence:']
            for s,t in shot_lines: lines.append(f'{s["shot_id"]}（{s["duration"]}秒）[{s["story_function"]}]：{t} 空间：{s["spatial"]} 镜头：{s["camera"]} 物理：{s["physics"]} 特效：{s["vfx"]} 连续性：{s["continuity"]}')
            lines += ['Continuity / Damage: '+json.dumps({s['shot_id']:s['damage'] for s in shot_records},ensure_ascii=False,separators=(',',':')),'Ending State: '+ending_text,'Negative Constraints: 不站桩、不摆POSE、不瞬移、不无因果换位、不复制或替换武器、不延迟无因果破坏、不用镜头切换掩盖非法动作。']
        elif model=='seedance_2_5':
            lines=['Reference / Asset Lock:\n'+identity,'Creative Brief:\n战斗优先；首个有效战斗事件尽快发生；叙事按实际战术原因、结果与阶段变化推进，不使用固定剧情模板。叙事曲线：'+narrative_curve_summary(runtime)+'；战术推进：'+narrative_intent_summary(runtime)+'；每个Shot保持单一连续可执行的因果单元；子Beat留在所属Shot内，不自动拆Shot。','Global Visual Direction:\n'+common+' '+scene,'Timeline / Shot Sequence:']
            for s,t in shot_lines: lines.append(f'{s["shot_id"]} | {s["duration"]}s | {s["story_function"]}\nMotion Continuity: {t}\nSpatial Continuity: {s["spatial"]}\nCamera Motivation: {s["camera"]}\nPhysics and VFX: {s["physics"]} {s["vfx"]}\nContinuity: {s["continuity"]}')
            lines += ['Ending State:\n'+ending_text,'Negative Constraints:\nNo identity drift, no weapon duplication/replacement, no teleportation, no causality-free destruction, no post-result-lock combat.']
        else:
            lines=['Scene:\n'+scene,'Characters / Asset Lock:\n'+'\n'.join(actor_lines),'Combat Objective:\n以战术因果解决当前问题并逐步升级；叙事曲线：'+narrative_curve_summary(runtime)+'；战术推进：'+narrative_intent_summary(runtime)+'；不以单纯爆炸规模代替战斗强度。','Action Sequence by Time:']
            for s,t in shot_lines: lines.append(f'【{s["shot_id"]} {s["duration"]}s】\nAction: {t}\nSpatial Position: {s["spatial"]}\nCamera: {s["camera"]}\nPhysics: {s["physics"]}\nEnvironment/VFX: {s["vfx"]}\nConsistency: {s["continuity"]}')
            lines += ['Ending State:\n'+ending_text,'Negative Constraints:\nNo static showcase opening, no impossible transitions, no weapon changes, no identity drift, no delayed impact without cause, no new attack after result lock.']
        prompt='\n'.join(lines)
        m=sde.dedup_component_metrics(chosen)
        trace_sentences=[x.get('sentence','').strip() for x in trace if x.get('type') in {'action','ability','ability_clash','result_lock','ending'} and x.get('sentence')]; exact=sum(1 for i,a in enumerate(trace_sentences) for b in trace_sentences[i+1:] if a==b)
        runtime_hits=[w for w in ['transition_contract','execution_contract','result_lock','INFERRED','FACT','NORMALIZED','knowledge_action_id','execution_model','opponent_response','state_contract','SHOT_IR','CANON','provenance','semantic_fingerprint'] if w in prompt]
        trace_actions=[x for x in trace if x.get('type')=='action']; fams={x.get('bundle',{}).get('family') for x in trace_actions if x.get('bundle')}; outs={x.get('bundle',{}).get('outcome') for x in trace_actions if x.get('bundle')}; bundles={tuple(x.get('bundle',{}).get('selected_components',[])) for x in trace_actions}
        budget_pressure=bool((runtime.get('planning_metrics') or {}).get('budget_pressure',False)); reuse_limit=0.55 if budget_pressure else 0.22; metrics[model]={**m,'runtime_term_leak_count':len(runtime_hits),'exact_duplicate_sentence_count':exact,'prompt_chars':len(prompt),'distinct_families':len(fams),'distinct_outcomes':len(outs),'distinct_component_bundles':len(bundles),'budget_pressure':budget_pressure,'component_reuse_limit':reuse_limit,'quality_gate':'PASS' if (not runtime_hits and exact==0 and m['semantic_bundle_collision_pairs']==0 and m['component_reuse_ratio']<=reuse_limit) else 'FAIL'}
        locked={'actors':{k:v.get('name',k) for k,v in actors.items()},'weapons':{k:v.get('weapon') for k,v in actors.items()},'event_ids':shot_ir.get('all_event_ids',[]),'ending':final,'spatial_provenance':shot_ir.get('spatial_provenance',{})}
        outputs[model]={'prompt':prompt,'source':'SHOT_IR_V10.18.6','invariant_manifest':locked,'semantic_fingerprint':sha(locked),'shot_count':len(shot_ir.get('shots',[])),'event_coverage':shot_ir.get('all_event_ids',[]),'compiler_mode':'combat_semantic_compiler_v4_zero_copy_model_native','semantic_trace':trace,'segment_plan':shot_records,'diversity_metrics':metrics[model]}
    return outputs,metrics

def compile_native_api(runtime_path,shot_path): return compile(load(runtime_path),load(shot_path))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime',required=True); ap.add_argument('--shot-ir',required=True); ap.add_argument('--out',required=True); ap.add_argument('--quality-out',required=True); args=ap.parse_args()
    runtime=load(args.runtime)
    if not runtime.get('selected_action_payloads') and not runtime.get('_actions_cache'): runtime['_actions_cache']=load(ROOT/'DATA/COMBAT_KNOWLEDGE/actions_10000.json')
    idx=ROOT/'DATA/COMBAT_KNOWLEDGE/SEMANTIC_COMPONENT_INDEX_V10.9.0.json'; runtime['_semantic_freq']=load(idx).get('component_frequencies',{}) if idx.exists() else {}
    out,metrics=compile(runtime,load(args.shot_ir)); Path(args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); Path(args.quality_out).write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    ok=all(v['quality_gate']=='PASS' for v in metrics.values()); print('COMBAT_SEMANTIC_COMPILATION='+('PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
if __name__=='__main__': main()
