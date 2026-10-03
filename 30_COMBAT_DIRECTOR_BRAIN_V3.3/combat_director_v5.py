"""Combat Director V4.0: autonomous candidate planning, persistent phases, prediction-driven selection, lookahead and bounded replanning.
The module is deliberately deterministic and data-driven; it never mutates Canon.
"""
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

@dataclass
class PhaseState:
    phase_id: str
    phase_goal: str
    dominant_problem: str = ""
    resource_pressure: str = ""
    positional_goal: str = ""
    opponent_prediction: list[str] = field(default_factory=list)
    allowed_escalation: list[str] = field(default_factory=list)
    phase_exit_condition: str = ""
    shot_budget_pressure: bool = False
    phase_reason: str = ""
    transition_pressure: str = ""
    spatial_problem: str = ""
    spatial_goal: str = ""


def infer_phase_goal(outcome: str, current_problem: str = "") -> str:
    return {
        "block": "改变防线结构并制造新攻击线",
        "dodge": "封闭闪避后的可用空间",
        "miss": "重新建立攻击线并修正距离",
        "bind": "赢得武器控制并迫使对手换线",
        "hit": "把局部优势转换为位置或节奏优势",
        "counter": "将对手的反制转化为下一次战术优势",
        "throw": "利用失衡完成位置转换",
        "disarm": "解除对手武器优势",
    }.get(outcome, current_problem or "建立下一次有效攻击条件")


def predict_opponent(personality: dict[str, Any], state: dict[str, Any], history: list[dict[str, Any]], constraints: dict[str, Any]) -> list[str]:
    """Generate qualitative candidates. Prediction is never authoritative."""
    candidates: list[str] = []
    for key in ("counter_preference", "defensive_response", "preferred_counter", "reposition_preference"):
        value = personality.get(key)
        if isinstance(value, str): value = [value]
        if isinstance(value, (list, tuple)):
            candidates.extend(str(x) for x in value)
    outcome = history[-1].get("outcome") if history else None
    distance = state.get("distance")
    if outcome in {"block", "bind"}: candidates += ["change_attack_line", "redirect_or_release"]
    elif outcome in {"dodge", "miss"}: candidates += ["reenter_on_new_angle", "reposition_or_counter"]
    elif outcome in {"hit", "counter"}: candidates += ["recover_and_recenter", "retreat_or_counter"]
    if distance in {"close", "contact"}: candidates.append("reposition_or_redirect")
    if state.get("terrain_pressure"): candidates.append("use_terrain_to_change_space")
    if constraints.get("ending_locked"): candidates = [x for x in candidates if x not in {"new_unlocked_ability", "forced_new_finisher"}]
    # Never infer a prediction from a missing fact.
    return list(dict.fromkeys(candidates))[:5]


def build_phase_state(phase_index: int, objective: str, problem: str, personality: dict[str, Any], state: dict[str, Any], history: list[dict[str, Any]], constraints: dict[str, Any], shot_budget_pressure: bool = False, spatial_state: dict[str, Any] | None = None) -> PhaseState:
    preds = predict_opponent(personality, state, history, constraints)
    outcome = history[-1].get("outcome", "") if history else ""
    goal = infer_phase_goal(outcome, problem)
    return PhaseState(
        phase_id=f"PHASE-{phase_index:02d}",
        phase_goal=goal,
        dominant_problem=problem or objective,
        resource_pressure=str(state.get("resource_pressure", "")),
        positional_goal=str(state.get("positional_goal", "")),
        opponent_prediction=preds,
        allowed_escalation=["tactical_difficulty", "position", "tempo", "range", "terrain", "ability_interaction"],
        phase_exit_condition="observable tactical result changes the dominant problem or ending state",
        shot_budget_pressure=shot_budget_pressure,
        phase_reason="phase goal derived from current state and most recent result; not a fixed story template",
        spatial_problem=str((spatial_state or {}).get("spatial_problem", "")),
        spatial_goal=str((spatial_state or {}).get("spatial_goal", "")),
    )




SPATIAL_LAYERS = {"ground": 0, "low_air": 1, "mid_air": 2, "high_air": 3, "extreme": 4}
SPATIAL_LAYER_NAMES = {v:k for k,v in SPATIAL_LAYERS.items()}

def infer_spatial_intent(action: dict[str, Any]) -> dict[str, Any]:
    """Infer only explicit spatial semantics from the knowledge action. Never invent a layer."""
    name=str(action.get("name", "")); ps=action.get("prompt_semantics", {}) or {}; core=str(ps.get("core_sentence", ""))
    text=" ".join([name, core, str(ps.get("must_show", ""))])
    if "目标离地" in text:
        return {"intent":"target_lift", "target_layer":"low_air", "actor_layer":None, "confidence":"explicit"}
    if "空中" in text:
        return {"intent":"aerial_transition", "target_layer":"mid_air", "actor_layer":"mid_air", "confidence":"explicit"}
    if "高空" in text or "云海上方" in text:
        return {"intent":"high_air_transition", "target_layer":"high_air", "actor_layer":"high_air", "confidence":"explicit"}
    if "坠落" in text:
        return {"intent":"fall", "target_layer":"ground", "actor_layer":None, "confidence":"explicit"}
    if "落地回收" in text:
        return {"intent":"return_to_ground", "target_layer":"ground", "actor_layer":"ground", "confidence":"explicit"}
    if "换角" in name or "侧移" in core or "移出原攻击线" in core or "环绕步" in core:
        return {"intent":"horizontal_reposition", "target_layer":None, "actor_layer":None, "confidence":"explicit"}
    return {"intent":"ground_continuity", "target_layer":None, "actor_layer":None, "confidence":"implicit"}

def spatial_transition_allowed(spatial_state: dict[str, Any], action: dict[str, Any], mode: str = "adaptive") -> bool:
    if mode == "grounded": return False
    intent=infer_spatial_intent(action)
    if intent["intent"] in {"ground_continuity", "horizontal_reposition"}: return True
    if mode in {"vertical","adaptive"} and intent["confidence"] == "explicit":
        return bool(spatial_state.get("vertical_space_supported", False))
    return False

def spatial_candidate_score(action: dict[str, Any], spatial_state: dict[str, Any], phase_index: int = 0, history: list[dict[str, Any]] | None = None, mode: str = "adaptive") -> tuple[float, list[str]]:
    """Score spatial actions against current 3D state and tactical need."""
    history=history or []; score=0.0; reasons=[]; intent=infer_spatial_intent(action)
    if not spatial_transition_allowed(spatial_state, action, mode): return (-8.0, ["spatial_transition_not_allowed"])
    layer=spatial_state.get("layer", "ground"); last_intent=spatial_state.get("last_transition", "")
    relative=spatial_state.get("relative_height", "same_level")
    if intent["intent"] == "target_lift":
        if layer == "ground": score += 6 if phase_index >= 2 else 2; reasons.append("target_ground_to_low_air")
        elif layer == "low_air": score -= 1; reasons.append("target_already_low_air")
    elif intent["intent"] == "aerial_transition":
        if layer == "ground": score += 4 if phase_index >= 2 else 0.5; reasons.append("actor_ground_to_mid_air")
        elif layer == "low_air": score += 3; reasons.append("actor_low_to_mid_air")
        elif layer in {"mid_air","high_air"}: score += 0.5; reasons.append("air_continuity")
        if last_intent in {"aerial_transition","high_air_transition"}: score -= 2.5; reasons.append("vertical_repeat_penalty")
    elif intent["intent"] == "high_air_transition":
        if layer in {"mid_air","high_air"}: score += 4; reasons.append("mid_to_high_air")
        else: score -= 1; reasons.append("high_air_requires_existing_vertical_state")
    elif intent["intent"] == "return_to_ground":
        if layer != "ground": score += 4; reasons.append("air_to_ground")
    elif intent["intent"] == "fall":
        if layer != "ground": score += 3; reasons.append("fall_to_ground")
    elif intent["intent"] == "horizontal_reposition":
        score += 2 if spatial_state.get("horizontal_reposition_supported", False) else -4; reasons.append("horizontal_space_change")
    else:
        score += 1 if layer == "ground" else -1
    if relative in {"above","below"}: score += 1.5; reasons.append("relative_height_can_change_tactics")
    return score, reasons

def _layer_for_actor(spatial_state, actor_id):
    actors=spatial_state.get("actors", {})
    return (actors.get(actor_id) or {}).get("layer", spatial_state.get("layer", "ground"))

def advance_spatial_state(spatial_state: dict[str, Any], action: dict[str, Any], outcome: str = "", actor_id: str | None = None, target_actor_id: str | None = None) -> dict[str, Any]:
    """Advance a dual-actor 3D spatial state. Target-lift changes the target, aerial changes the actor."""
    state=dict(spatial_state or {}); intent=infer_spatial_intent(action)
    actors={k:dict(v) for k,v in (state.get("actors") or {}).items()}
    aid=actor_id or action.get("actor_id") or "ACTOR_A"
    tid=target_actor_id or action.get("target_actor_id")
    actors.setdefault(aid, {"layer":"ground","anchor":"UNKNOWN","support":"grounded"})
    if tid: actors.setdefault(tid, {"layer":"ground","anchor":"UNKNOWN","support":"grounded"})
    before={k:v.get("layer","ground") for k,v in actors.items()}
    if intent["intent"] == "target_lift" and tid:
        actors[tid]["layer"]="low_air"; actors[tid]["support"]="airborne"
    elif intent["intent"] == "aerial_transition":
        actors[aid]["layer"]="mid_air"; actors[aid]["support"]="airborne"
    elif intent["intent"] == "high_air_transition":
        actors[aid]["layer"]="high_air"; actors[aid]["support"]="airborne"
    elif intent["intent"] in {"return_to_ground","fall"}:
        actors[aid]["layer"]="ground"; actors[aid]["support"]="grounded"
    elif intent["intent"] == "horizontal_reposition":
        # Horizontal movement is persistent state, not a one-shot label. Resolve a known
        # anchor from action metadata when available; otherwise preserve the current anchor
        # and mark the transition as pending instead of inventing a location.
        anchor_hint=(action.get("environment_anchor") or action.get("anchor") or
                     (action.get("execution_model",{}) or {}).get("anchor"))
        if anchor_hint:
            actors[aid]["anchor"]=anchor_hint
            actors[aid]["anchor_pending_change"]=False
        else:
            actors[aid]["anchor_pending_change"]=True
    # If the target was explicitly lifted and this event's result is a recovery/landing, do not keep it airborne.
    if outcome in {"throw","hit","counter"} and intent["intent"] == "fall" and tid:
        actors[tid]["layer"]="ground"; actors[tid]["support"]="grounded"
    la=actors[aid].get("layer","ground"); tl=actors.get(tid,{}).get("layer",la) if tid else la
    # Persist horizontal/tactical spatial semantics so later Beats/Shots do not infer them from text alone.
    em=action.get("execution_model",{}) or {}; dist=(em.get("distance") or {}).get("id") or action.get("distance") or state.get("relative_distance") or "UNKNOWN"
    com=(em.get("center_of_mass") or {}).get("description") or "UNKNOWN"
    movement="vertical" if intent["intent"] in {"aerial_transition","high_air_transition","fall","return_to_ground","target_lift"} else ("horizontal_reposition" if intent["intent"]=="horizontal_reposition" else state.get("movement_vector","UNKNOWN"))
    axis=(em.get("center_of_mass") or {}).get("path_id") or (em.get("contact_geometry") or {}).get("id") or state.get("attack_axis","UNKNOWN")
    facing=action.get("facing") or action.get("attack_direction") or state.get("facing","UNKNOWN")
    rel="same_level"
    if tid:
        za=SPATIAL_LAYERS.get(la,0); zt=SPATIAL_LAYERS.get(tl,0)
        rel="above" if za>zt else "below" if za<zt else "same_level"
    state.update({"actors":actors,"layer":la,"previous_layer":before.get(aid,la),"last_transition":intent["intent"],"last_action_id":action.get("action_id"),"last_outcome":outcome,"relative_height":rel,"relative_height_by_pair":rel,"relative_distance":dist,"movement_vector":movement,"movement_detail":com,"facing":facing,"attack_axis":axis,"active_anchor":actors[aid].get("anchor","UNKNOWN"),"target_anchor":actors.get(tid,{}).get("anchor","UNKNOWN") if tid else None,"transition_reason":"action_supported_spatial_motion" if intent["confidence"]=="explicit" else "continuity"})
    state["active_actor_id"]=aid; state["target_actor_id"]=tid
    return state

def build_spatial_state(actor_ids, config, source):
    cfg=config or {}; src=source or {}; supported=cfg.get("vertical_space_supported", src.get("vertical_space_supported", False))
    anchors=cfg.get("anchors", src.get("anchors", []))
    base_anchor=src.get("anchor", "UNKNOWN") or "UNKNOWN"
    actors_cfg=cfg.get("actors", src.get("actors", {})) or {}
    actors={}
    for aid in actor_ids:
        ac=actors_cfg.get(aid,{}) if isinstance(actors_cfg,dict) else {}
        actors[aid]={"layer":ac.get("layer",cfg.get("initial_layer",src.get("layer","ground"))),"anchor":ac.get("anchor",base_anchor),"support":ac.get("support","grounded")}
    return {"actors":actors,"layer":cfg.get("initial_layer",src.get("layer","ground")),"vertical_space_supported":bool(supported),"horizontal_reposition_supported":cfg.get("horizontal_reposition_supported", True),"anchors":anchors,"anchor":base_anchor,"relative_height":"same_level","relative_distance":src.get("relative_distance","UNKNOWN"),"movement_vector":src.get("movement_vector","UNKNOWN"),"facing":src.get("facing","UNKNOWN"),"attack_axis":src.get("attack_axis","UNKNOWN"),"last_transition":"","last_action_id":None,"last_outcome":""}

def _valid(candidate: Any, validator: Callable[[Any], bool]) -> bool:
    try: return bool(validator(candidate))
    except Exception: return False


def replan_after_invalid(candidates: Iterable[Any], validator: Callable[[Any], bool], max_alternates: int = 3, recovery: Any = None):
    """Bounded replan: alternate candidates first, then one legal recovery link."""
    for index, candidate in enumerate(list(candidates)[:max_alternates], 1):
        if _valid(candidate, validator): return candidate, {"status": "ALTERNATE_PASS", "attempt": index}
    if recovery is not None and _valid(recovery, validator):
        return recovery, {"status": "RECOVERY_LINK_PASS", "attempt": max_alternates + 1}
    return None, {"status": "REPLAN_REQUIRED", "attempt": max_alternates + 1}


def lookahead_viable(candidate_b: Any, candidate_cs: Iterable[Any], transition_validator: Callable[[Any, Any], bool]) -> tuple[bool, list[Any]]:
    viable=[]
    for candidate_c in candidate_cs:
        if _valid((candidate_b, candidate_c), lambda pair: transition_validator(pair[0], pair[1])):
            viable.append(candidate_c)
    return bool(viable), viable


def budget_feedback(event_count: int, shot_count: int, hard_max: int = 7) -> dict[str, Any]:
    pressure = shot_count > hard_max
    return {
        "pressure": pressure,
        "event_count": event_count,
        "proposed_shots": shot_count,
        "hard_max": hard_max,
        "actions": ["merge_compatible_micro_beats", "fold_recovery_into_parent_event", "reselect_more_compressible_candidate"] if pressure else [],
        "forbidden": ["delete_unique_causal_result", "change_canon", "change_locked_ending"],
    }


# V3.0 planning primitives -------------------------------------------------
def _norm(value):
    if value is None: return ""
    return str(value).strip().lower()



# V10.6 Highlight / Impact Direction -----------------------------------------
# This is intentionally embedded in Combat Director rather than introduced as a
# separate runtime module. It selects existing knowledge actions that already
# contain strong contact/force/result/environment semantics; it never invents
# a new action, target, body location, or damage fact.
HIGHLIGHT_OUTCOMES = {"hit", "counter", "throw", "disarm"}
HIGHLIGHT_FAMILIES = ("反击", "追击", "破防", "摔投", "擒拿", "直接打击", "低位", "换角", "进身")

HIGHLIGHT_CHOREOGRAPHY_VERSION = "2.0"
HIGHLIGHT_TEMPO_PHASES = ("approach_normal", "entry_slow", "contact_slow", "impact_normal", "result_fast")
HIGHLIGHT_CAMERA_PHASES = ("establish_low_angle", "slow_orbit", "leg_or_weapon_track", "contact_lock", "impact_follow", "result_observe")
HIGHLIGHT_IMPACT_LAYERS = ("core", "middle", "outer")
HIGHLIGHT_SEMANTIC_FIDELITY_VERSION = "1.0"


def normalize_highlight_directive(directive: dict[str, Any] | None = None) -> dict[str, Any]:
    """Promote explicit user highlight facts into an immutable, serializable Highlight Canon.

    This layer does not invent combat facts. Values are copied only from the explicit directive;
    missing values remain absent. The Canon is later propagated into SHOT_IR and all native adapters.
    """
    d = directive or {}
    time_segments = d.get("time_segments") or d.get("temporal_segments") or []
    segments=[]
    for seg in time_segments:
        if not isinstance(seg,dict): continue
        item={}
        for k in ("start_s","end_s","phase","speed","note"):
            if k in seg and seg[k] is not None: item[k]=seg[k]
        if item: segments.append(item)
    vfx_layers={}
    raw_layers=d.get("vfx_layers") or d.get("impact_vfx") or {}
    if isinstance(raw_layers,dict):
        for layer in HIGHLIGHT_IMPACT_LAYERS:
            v=raw_layers.get(layer)
            if isinstance(v,dict):
                vfx_layers[layer]={k:v[k] for k in ("material","color","shape","motion","expansion","direction","timing","origin","fragment","velocity","environment_response") if k in v}
            elif isinstance(v,str) and v.strip():
                vfx_layers[layer]={"description":v.strip()}
    action={}
    raw_action=d.get("action_structure") or d.get("highlight_action") or {}
    if isinstance(raw_action,dict):
        for k in ("approach","entry","rotation","rotation_count","limb_action","contact","contact_target","contact_point","force_transfer","body_response","displacement","environment_result"):
            if raw_action.get(k) is not None: action[k]=raw_action[k]
    camera=dict(d.get("camera") or {})
    for k in ("angle","height","orbit","focus","focus_lock","contact_lock","impact_follow","result_observe"):
        if d.get(k) is not None and k not in camera: camera[k]=d[k]
    return {
        "version": HIGHLIGHT_SEMANTIC_FIDELITY_VERSION,
        "explicit_only": True,
        "name": d.get("name") or d.get("highlight_name"),
        "action": action,
        "temporal_segments": segments,
        "camera": camera,
        "vfx_layers": vfx_layers,
        "result_chain": list(d.get("result_chain") or []),
        "critical_facts": list(d.get("critical_facts") or []),
        "negative_constraints": list(d.get("negative_constraints") or []),
    }


def highlight_semantic_fidelity(candidate: dict[str, Any], directive: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build semantic fidelity data from explicit directive + existing action knowledge.

    Explicit user facts are authoritative for presentation/semantic detail; action knowledge still
    supplies the underlying runtime event contract and is never replaced by invented facts.
    """
    canon=normalize_highlight_directive(directive)
    em=candidate.get("execution_model",{}) or {}; ex=candidate.get("execution",{}) or {}
    opp=candidate.get("opponent_response",{}) or {}; env=candidate.get("environment",{}) or {}
    derived={
        "knowledge_contact": ex.get("contact_point"),
        "knowledge_force": (candidate.get("physics",{}) or {}).get("force_source"),
        "knowledge_body_response": opp.get("body_mechanics"),
        "knowledge_environment": (env.get("surface",{}) or {}).get("response") if isinstance(env,dict) else None,
    }
    explicit_count=sum(bool(v) for v in (canon.get("action"),canon.get("temporal_segments"),canon.get("camera"),canon.get("vfx_layers"),canon.get("result_chain"),canon.get("critical_facts")))
    canon["explicit_field_count"]=explicit_count
    canon["knowledge_support"]={k:v for k,v in derived.items() if v}
    canon["fidelity_required"]=explicit_count>0
    canon["no_new_event"]=True
    return canon

def build_highlight_choreography(candidate: dict[str, Any], directive: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a fact-bound temporal/camera/impact choreography profile.

    This is presentation metadata for one existing Event. It never creates another
    attack, hit, result, target, anatomy fact, or secondary collision. Explicit
    scenario directives override only presentation fields; action knowledge remains
    the source of combat semantics.
    """
    directive = directive or {}
    ex=candidate.get("execution",{}) or {}; em=candidate.get("execution_model",{}) or {}
    cin=candidate.get("cinematic",{}) or {}; vfx=candidate.get("vfx",{}) or {}
    opp=candidate.get("opponent_response",{}) or {}; env=candidate.get("environment",{}) or {}
    requested_duration=directive.get("duration_s") or directive.get("preferred_duration_s")
    try: requested_duration=round(float(requested_duration),2) if requested_duration is not None else None
    except Exception: requested_duration=None
    slow_entry=bool(directive.get("slow_entry", directive.get("slow_motion_entry", False)))
    slow_contact=bool(directive.get("slow_contact", directive.get("slow_motion_contact", True)))
    restore_on_impact=bool(directive.get("restore_on_impact", True))
    phases=list(directive.get("tempo_phases") or [])
    if not phases:
        phases=["approach_normal", "entry_slow" if slow_entry else "approach_normal", "contact_slow" if slow_contact else "impact_normal", "impact_normal" if restore_on_impact else "contact_slow", "result_fast"]
    phases=list(dict.fromkeys(phases))
    camera=dict(directive.get("camera") or {})
    if not camera:
        camera={"angle":directive.get("angle") or "cause_follow", "orbit":bool(directive.get("slow_orbit",False)), "focus":directive.get("focus") or "contact_axis", "result_follow":True}
    impact_stack=directive.get("impact_stack")
    if impact_stack is None:
        impact_stack=[]
        if vfx.get("primary") or vfx.get("timing"): impact_stack.append("core")
        if vfx.get("secondary") or vfx.get("direction"): impact_stack.append("middle")
        if env.get("surface",{}).get("response") or directive.get("outer_effect"): impact_stack.append("outer")
    impact_stack=[x for x in impact_stack if x in HIGHLIGHT_IMPACT_LAYERS]
    if directive.get("impact_stack") and len(impact_stack)>=3:
        impact_stack=list(dict.fromkeys(impact_stack))
    result_chain=directive.get("result_chain") or []
    if not result_chain:
        result_chain=["body_response"]
        if opp.get("primary"): result_chain.append("displacement")
        if env.get("surface",{}).get("response") or directive.get("secondary_collision"): result_chain.append("environment_response")
    allowed=set(["approach_normal","entry_slow","contact_slow","impact_normal","result_fast","result_observe"])
    phases=[x for x in phases if x in allowed] or ["approach_normal","contact_slow","impact_normal","result_fast"]
    semantic=highlight_semantic_fidelity(candidate, directive)
    return {
        "version":HIGHLIGHT_CHOREOGRAPHY_VERSION,
        "single_event":bool(directive.get("single_event",True)),
        "preferred_duration_s":requested_duration,
        "tempo_phases":phases,
        "speed_curve":directive.get("speed_curve") or "normal→slow→contact_slow→instant_normal→fast_result",
        "camera":camera,
        "camera_phases":list(directive.get("camera_phases") or ["establish_low_angle","slow_orbit","contact_lock","impact_follow","result_observe"]),
        "impact_stack":impact_stack,
        "result_chain":list(dict.fromkeys(result_chain)),
        "contact_lock":bool(directive.get("contact_lock",True)),
        "restore_on_impact":restore_on_impact,
        "fact_bound":True,
        "no_new_event":True,
        "semantic_fidelity":semantic,
    }

def _highlight_text(candidate: dict[str, Any]) -> str:
    em=candidate.get("execution_model",{}) or {}; ex=candidate.get("execution",{}) or {}
    phy=candidate.get("physics",{}) or {}; opp=candidate.get("opponent_response",{}) or {}
    cin=candidate.get("cinematic",{}) or {}; env=candidate.get("environment",{}) or {}
    var=candidate.get("variant",{}) or {}; intent=candidate.get("intent",{}) or {}
    return " ".join(str(x) for x in [candidate.get("name",""), intent.get("name",""), intent.get("logic",""), ex.get("footwork",""), ex.get("body_kinematics",""), ex.get("contact_point",""), ex.get("impact_timing",""), phy.get("force_source",""), phy.get("weight_transfer",""), phy.get("momentum",""), phy.get("collision",""), opp.get("primary",{}).get("description","") if isinstance(opp.get("primary"),dict) else "", opp.get("body_mechanics",""), opp.get("tactical_change",""), cin.get("contact",{}).get("execution","") if isinstance(cin.get("contact"),dict) else "", str(cin.get("shot_sequence","")), env.get("surface",{}).get("response","") if isinstance(env.get("surface"),dict) else "", var.get("semantic_change","")])


def highlight_impact_score(candidate: dict[str, Any]) -> tuple[float, list[str], dict[str, Any]]:
    """Calibrated Impact Payoff + Highlight Choreography score.
    The knowledge base is uniformly execution-grade, so schema completeness is deliberately
    low-weight. Signature status requires payoff-specific evidence, not merely complete fields.
    """
    em=candidate.get("execution_model",{}) or {}; ex=candidate.get("execution",{}) or {}
    phy=candidate.get("physics",{}) or {}; opp=candidate.get("opponent_response",{}) or {}
    cin=candidate.get("cinematic",{}) or {}; env=candidate.get("environment",{}) or {}
    var=candidate.get("variant",{}) or {}; intent=candidate.get("intent",{}) or {}
    outcome=opp.get("outcome_class"); name=str(candidate.get("name", ""));
    primary=opp.get("primary") if isinstance(opp.get("primary"),dict) else {}
    primary_text=str(primary.get("description", "")); tactical=str(opp.get("tactical_change", "") or "")
    mech=" ".join(str(x) for x in [intent.get("name",""),intent.get("logic",""),ex.get("startup",""),ex.get("body_kinematics",""),ex.get("footwork",""),ex.get("contact_point","")])
    score=12.0; reasons=[]; amplifiers=[]
    if outcome in {"hit","counter","throw","disarm"}: score+=8; reasons.append("high_value_outcome")
    if em.get("contact_geometry") and ex.get("contact_point"): score+=7; reasons.append("contact_clarity"); amplifiers.append("contact")
    force_count=sum(bool(phy.get(k)) for k in ("force_source","weight_transfer","momentum","collision"))
    if force_count>=2: score+=7; reasons.append("force_transfer_chain"); amplifiers.append("force_transfer")
    elif force_count==1: score+=2
    if opp.get("body_mechanics"): score+=5; reasons.append("body_response"); amplifiers.append("body_response")
    if tactical: score+=4; reasons.append("tactical_payoff"); amplifiers.append("tactical_payoff")
    # Only payoff-specific movement terms count; generic "后退半步/改变支撑" language is not enough.
    strong_motion=("旋身","旋转","枢轴","借力","卸力","绞","压腕","摔投","摔落","蹬","踹","飞撞","撞击","击飞","离地","翻滚","破防","终结","扫腿","扫击","牵引","转髋")
    motion_hits=sum(1 for t in strong_motion if t in mech or t in name)
    if motion_hits:
        score+=min(10,motion_hits*3); reasons.append(f"distinctive_motion:{min(motion_hits,3)}"); amplifiers.append("distinctive_motion")
    strong_reaction=("击飞","飞出","撞","离地","翻滚","摔落","武器脱手","凹陷","断裂","破碎","倒地","大幅")
    reaction_hits=sum(1 for t in strong_reaction if t in primary_text or t in str(var.get("semantic_change","")) or t in str(var.get("name","")))
    if reaction_hits:
        score+=min(10,reaction_hits*3); reasons.append("strong_reaction"); amplifiers.append("visible_reaction")
    env_str=" ".join(str(x) for x in [env.get("trigger",""),env.get("causality",""),env.get("persistence","")])
    env_surface=str((env.get("surface") or {}).get("response","") if isinstance(env.get("surface"),dict) else env.get("surface",""))
    strong_env=("护栏","墙","石柱","桥","屋檐","柱","开裂","凹陷","碎裂","破碎","崩裂","撞入")
    if any(t in env_str+env_surface+name for t in strong_env) and not ("脚步" in env_surface and not any(t in env_surface for t in strong_env)):
        score+=7; reasons.append("environment_payoff"); amplifiers.append("environment_payoff")
    if cin.get("contact") or cin.get("shot_sequence"): score+=3; reasons.append("camera_readability")
    if var.get("semantic_change"): score+=2; reasons.append("variant_specificity")
    if any(t in name for t in ("终结","破防","摔投","反击","追击")): score+=3; amplifiers.append("impact_family"); reasons.append("impact_family")
    # Generic schema fields are intentionally not scored. A uniform knowledge row therefore
    # stays in high/support rather than automatically becoming a signature highlight.
    if not (reaction_hits or any(t in name for t in strong_env) or any(t in mech for t in strong_motion)):
        score-=3; reasons.append("generic_action_penalty")
    score=min(100.0,max(0.0,round(score,2)))
    amp=set(amplifiers)
    signature_ok=(score>=68 and len(amp)>=4 and ("visible_reaction" in amp or "environment_payoff" in amp) and ("distinctive_motion" in amp or "impact_family" in amp))
    high_ok=(score>=52 and len(amp)>=3)
    support_ok=(score>=38 and len(amp)>=2)
    tier="signature" if signature_ok else "high" if high_ok else "support" if support_ok else "standard"
    choreography={"trigger":bool(intent.get("logic") or candidate.get("decision_trigger")),"entry":bool(ex.get("startup") or ex.get("footwork")),"contact":bool(em.get("contact_geometry") or ex.get("contact_point")),"force_transfer":force_count>=2,"body_response":bool(opp.get("body_mechanics") or primary_text),"displacement":bool(reaction_hits),"environment_payoff":"environment_payoff" in amp,"camera_payoff":bool(cin.get("contact") or cin.get("shot_sequence")),"temporal":False,"impact_stack":0,"speed_restore":False}
    profile={"score":score,"tier":tier,"reasons":reasons,"outcome":outcome,"choreography":choreography,"amplifiers":list(dict.fromkeys(amplifiers)),"genericity_penalty":3 if "generic_action_penalty" in reasons else 0,"contact_defined":bool(em.get("contact_geometry")),"force_defined":force_count>=2,"body_response_defined":bool(opp.get("body_mechanics")),"environment_defined":bool(env)}
    return score,reasons,profile


def apply_highlight_context(score: float, meta: dict[str, Any], item: dict[str, Any] | None = None, candidate: dict[str, Any] | None = None) -> tuple[float, dict[str, Any], list[str]]:
    """Add only scenario-provided payoff context (e.g. an explicitly authorized secondary collision)."""
    item=item or {}; candidate=candidate or {}; reasons=[]
    if item.get("secondary_collision") and candidate.get("opponent_response",{}).get("outcome_class") in HIGHLIGHT_OUTCOMES:
        score=max(score,70.0); reasons.append("authorized_secondary_collision")
        meta=dict(meta); meta["tier"]="signature" if score>=70 else meta.get("tier","high")
        amps=list(meta.get("amplifiers",[])); amps.extend(["environment_payoff","secondary_collision"]); meta["amplifiers"]=list(dict.fromkeys(amps))
        ch=dict(meta.get("choreography",{})); ch["environment_payoff"]=True; ch["displacement"]=True; meta["choreography"]=ch
    return score,meta,reasons


def highlight_target(duration_s: float, action_count: int, requested_target: int | None = None) -> int:
    if requested_target is not None: return max(0,min(4,int(requested_target)))
    if duration_s >= 45 and action_count >= 10: return 3
    if duration_s >= 25 and action_count >= 6: return 2
    if duration_s >= 12 and action_count >= 4: return 1
    return 0

def highlight_due(duration_s: float, action_index: int, action_count: int, selected_count: int, target: int) -> bool:
    if target<=0 or selected_count>=target or action_count<=0: return False
    # Milestones keep visual peaks distributed: no early spam, no empty final stretch.
    thresholds=[0.24,0.58,0.80,0.90]
    threshold=thresholds[min(selected_count,len(thresholds)-1)]
    progress=(action_index+1)/max(1,action_count)
    return progress>=threshold or (action_count-action_index-1)<=max(1,target-selected_count)

def candidate_score(candidate: dict[str, Any], actor: dict[str, Any], state: dict[str, Any],
                    phase: PhaseState | None, predicted_responses: list[str], requested_id: str | None = None, observed_outcomes: list[str] | None = None, observed_signatures: list[str] | None = None, spatial_state: dict[str, Any] | None = None, phase_index: int = 0, spatial_mode: str = "adaptive", highlight_due_now: bool = False, highlight_selected: int = 0, highlight_target_count: int = 0) -> tuple[float, list[str]]:
    """Score a knowledge action without mutating Canon. The requested action is only a preference."""
    score = 0.0; reasons=[]
    observed_signatures=observed_signatures or []
    weapon = actor.get("weapon")
    if candidate.get("weapon") == weapon:
        score += 5; reasons.append("weapon_lock")
    em = candidate.get("execution_model", {})
    dist = em.get("distance", {}).get("id")
    if state.get("distance") and dist == state.get("distance"):
        score += 3; reasons.append("distance_fit")
    if requested_id and candidate.get("action_id") == requested_id:
        score += 1.5; reasons.append("requested_preference")
    outcome=candidate.get("opponent_response",{}).get("outcome_class")
    if observed_outcomes is not None:
        if outcome and outcome not in observed_outcomes:
            score += 2.5; reasons.append("outcome_diversity")
        elif outcome and observed_outcomes.count(outcome) >= 2:
            score -= 2; reasons.append("outcome_overuse_penalty")
    fam = _norm(candidate.get("name", ""))
    pred_map = {
        "change_attack_line": ("换角", "破防", "probe"),
        "redirect_or_release": ("卸转", "换角"),
        "reenter_on_new_angle": ("换角", "追击", "进身"),
        "reposition_or_counter": ("反击", "换角", "退击"),
        "recover_and_recenter": ("卸转", "退击", "试探"),
        "retreat_or_counter": ("退击", "反击"),
        "reposition_or_redirect": ("换角", "卸转"),
        "use_terrain_to_change_space": ("换角", "追击", "进身"),
    }
    for pred in predicted_responses:
        for frag in pred_map.get(pred, ()):
            if frag in fam:
                score += 4; reasons.append(f"prediction_fit:{pred}"); break
    if phase:
        goal = phase.phase_goal
        if "防线" in goal and any(x in fam for x in ("破防", "换角", "试探")):
            score += 2; reasons.append("phase_goal_fit")
        if "位置" in goal and any(x in fam for x in ("追击", "换角", "进身", "退击")):
            score += 2; reasons.append("phase_position_fit")
    signature='|'.join([str(candidate.get('execution_model',{}).get('joint_chain',{}).get('id','')), str(candidate.get('execution_model',{}).get('center_of_mass',{}).get('path_id','')), str(candidate.get('execution_model',{}).get('contact_geometry',{}).get('id',''))])
    if candidate.get('action_id') in observed_signatures:
        score -= 8.0; reasons.append('action_id_reuse_penalty')
    if signature in observed_signatures:
        score -= 1.5; reasons.append('motion_signature_reuse_penalty')
    if spatial_state is not None:
        ss,sr=spatial_candidate_score(candidate, spatial_state, phase_index, [], spatial_mode); score += ss; reasons.extend(sr)
    hscore,hreasons,hmeta=highlight_impact_score(candidate)
    if highlight_due_now:
        if hscore>=52 and hmeta.get("tier") in {"high","signature","support"}:
            score += 4.0 + (hscore-52)*0.08; reasons.append(f"highlight_due:{hmeta['tier']}")
        elif hscore<42:
            score -= 1.0; reasons.append("highlight_quality_too_low")
    elif hscore>=82 and hmeta.get("tier")=="signature" and highlight_selected < highlight_target_count:
        score += 1.2; reasons.append("signature_highlight_reserve")
    # Prefer executable actions over actions whose preconditions clearly disagree with current state.
    pre = candidate.get("preconditions_normalized", {})
    if state.get("distance") and pre.get("distance_id") not in (None, state.get("distance")):
        score -= 4; reasons.append("distance_mismatch")
    return score, reasons


def select_action_candidate(candidates: Iterable[dict[str, Any]], actor: dict[str, Any], state: dict[str, Any],
                            phase: PhaseState | None, predicted_responses: list[str], requested_id: str | None = None, observed_outcomes: list[str] | None = None, observed_signatures: list[str] | None = None, spatial_state: dict[str, Any] | None = None, phase_index: int = 0, spatial_mode: str = "adaptive", highlight_due_now: bool = False, highlight_selected: int = 0, highlight_target_count: int = 0):
    ranked=[]
    for c in candidates:
        score,reasons=candidate_score(c,actor,state,phase,predicted_responses,requested_id,observed_outcomes,observed_signatures,spatial_state,phase_index,spatial_mode,highlight_due_now,highlight_selected,highlight_target_count)
        ranked.append((score,c,reasons))
    ranked.sort(key=lambda x:(x[0], x[1].get("action_id", "")), reverse=True)
    if not ranked: return None, []
    return ranked[0][1], [{"action_id":x[1].get("action_id"),"score":x[0],"reasons":x[2]} for x in ranked[:5]]


def autonomous_candidate_pool(actions: Iterable[dict[str, Any]], actor: dict[str, Any], state: dict[str, Any], limit: int = 32):
    weapon=actor.get("weapon")
    domain=actor.get("actor_domain")
    pool=[]
    for a in actions:
        if a.get("weapon") != weapon: continue
        if domain and a.get("actor_domain") not in (None, domain): continue
        pre=a.get("preconditions_normalized", {})
        if state.get("distance") and pre.get("distance_id") not in (None,state.get("distance")): continue
        pool.append(a)
        if len(pool)>=limit: break
    return pool


def advance_phase(previous: PhaseState | None, objective: str, problem: str, personality: dict[str, Any],
                  state: dict[str, Any], history: list[dict[str, Any]], constraints: dict[str, Any],
                  shot_budget_pressure: bool = False, spatial_state: dict[str, Any] | None = None) -> PhaseState:
    """Keep a phase alive across compatible events; create a new phase only on a tactical shift."""
    preds=predict_opponent(personality,state,history,constraints)
    outcome=history[-1].get("outcome","") if history else ""
    goal=infer_phase_goal(outcome,problem)
    if previous is not None:
        major_problem = problem and problem != previous.dominant_problem
        major_outcome = outcome in {"counter","disarm","throw"} or (outcome=="hit" and previous.phase_goal != goal)
        pressure_change = shot_budget_pressure != previous.shot_budget_pressure
        if not (major_problem or major_outcome or pressure_change):
            previous.opponent_prediction=list(dict.fromkeys(preds))[:5]
            previous.shot_budget_pressure=shot_budget_pressure
            previous.transition_pressure="stable"
            return previous
    idx=1 if previous is None else int(previous.phase_id.split("-")[-1])+1
    ps=build_phase_state(idx,objective,problem,personality,state,history,constraints,shot_budget_pressure)
    ps.transition_pressure="phase_shift" if previous is not None else "initial"
    return ps


def lookahead_replan(candidate_b: dict[str, Any], candidate_b_alternates: Iterable[dict[str, Any]], candidate_cs: Iterable[dict[str, Any]],
                     graph_by_action: dict[str, dict[str, Any]], allowed_families_fn: Callable[[dict[str, Any], str], set[str]],
                     family_fn: Callable[[dict[str, Any]], str], max_alternates: int = 6) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """True B→C lookahead. Test the committed B against future C candidates; if invalid,
    search alternative B candidates and commit the first B that preserves at least one viable C.
    """
    cs=list(candidate_cs); alts=list(candidate_b_alternates); tested=[]
    def viable(b,c):
        g=graph_by_action.get(b.get('action_id'),{}) or {}
        outcome=b.get('outcome') or (b.get('opponent_response') or {}).get('outcome_class','')
        allowed=allowed_families_fn(g,outcome)
        return (not allowed) or family_fn(c) in allowed
    if not cs:
        return candidate_b, {'status':'NO_FUTURE_CANDIDATES','replanned':False,'tested':tested}
    if any(viable(candidate_b,c) for c in cs):
        return candidate_b, {'status':'PASS','replanned':False,'tested':[candidate_b.get('action_id')]}
    for alt in alts[:max_alternates]:
        tested.append(alt.get('action_id'))
        if any(viable(alt,c) for c in cs):
            return alt, {'status':'REPLANNED','replanned':True,'from_action':candidate_b.get('action_id'),'to_action':alt.get('action_id'),'tested':tested}
    return None, {'status':'PRESSURE','replanned':False,'tested':tested}


def budget_aware_replan(event_count: int, current_target: int, hard_max: int = 7, max_events_per_beat: float = 2.2) -> dict[str, Any]:
    """Beat-budget pressure is measured before camera allocation; shots are not capped at seven."""
    required=math.ceil(event_count / max_events_per_beat)
    pressure=required>hard_max
    return {
        "pressure": pressure,
        "required_beats_at_density": required,
        "current_target": current_target,
        "hard_max_beats": hard_max,
        "actions": (["reselect_more_compressible_candidates","merge_compatible_micro_beats","fold_nonessential_recovery_wording"] if pressure else []),
        "forbidden":["delete_unique_causal_result","change_canon","change_locked_ending","invent_new_event","cap_shots_to_seven"],
        "feedback_target":"combat_director" if pressure else None,
        "closed_loop_required": bool(pressure),
        "presentation_remerge_required": bool(pressure),
    }
