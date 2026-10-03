"""Adaptive Weapon Control Intelligence V1.2 — Semantic Variant Compiler.

Turns Universal Weapon Control from a capability flag into a bounded tactical decision layer.
It does not create new combat Events or alter weapon identity; it selects whether an existing
weapon action should be presented/executed as HAND_HELD or a remote-control mode.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any

REMOTE_MODES = {"TELEKINETIC", "SPIRIT_CONTROLLED", "REMOTE_ATTACK", "RETURN_CONTROL"}
REMOTE_PATTERNS = {
    "release": ["release", "airborne", "attack", "return"],
    "tracking": ["release", "airborne", "tracking", "attack", "return"],
    "orbit": ["release", "airborne", "orbit", "tracking", "attack", "return"],
    "angle_change": ["release", "airborne", "tracking", "trajectory_change", "attack", "return"],
    "multi_angle": ["release", "airborne", "orbit", "tracking", "multi_angle_attack", "trajectory_change", "attack", "return"],
    "environment_redirect": ["release", "airborne", "tracking", "environment_redirect", "trajectory_change", "attack", "return"],
}

PATTERN_BASE_COST = {"release": 12.0, "tracking": 16.0, "orbit": 22.0, "angle_change": 20.0, "multi_angle": 34.0, "environment_redirect": 29.0}
PATTERN_GAIN = {"release": 8.0, "tracking": 18.0, "orbit": 22.0, "angle_change": 28.0, "multi_angle": 34.0, "environment_redirect": 31.0}


def _text(*values: Any) -> str:
    return " ".join(str(v).lower() for v in values if v is not None)


def _last_outcome(history: list[dict[str, Any]]) -> str:
    return str(history[-1].get("outcome", "")) if history else ""


def evaluate_weapon_control(
    weapon: str,
    state: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
    action: dict[str, Any] | None = None,
    explicit_intent: Any = None,
    ending_locked: bool = False,
) -> dict[str, Any]:
    """Return a bounded control decision. Capability is universal; activation is contextual."""
    state = state or {}
    history = history or []
    wc = ((action or {}).get("execution_model") or {}).get("weapon_control") or {}
    mode = str(wc.get("control_mode", "HAND_HELD"))
    remote_existing = mode in REMOTE_MODES
    if not weapon or weapon in {"徒手", "unarmed", "none"}:
        return {"capable": False, "activate": False, "score": 0, "mode": "HAND_HELD", "pattern": "release", "reason": "unarmed"}
    if ending_locked:
        return {"capable": True, "activate": False, "score": 0, "mode": "HAND_HELD", "pattern": "release", "reason": "result_lock_barrier"}

    explicit = bool(explicit_intent) and str(explicit_intent).lower() not in {"false", "0", "none", "null", ""}
    distance = str(state.get("distance", state.get("relative_distance", ""))).lower()
    defense = _text(state.get("defense_state"), state.get("opponent_defense"))
    opening = _text(state.get("opening_window"), state.get("opening"))
    terrain = _text(state.get("battlefield_position"), state.get("terrain_pressure"), state.get("environment_anchor"))
    mobility = _text(state.get("enemy_mobility"), state.get("target_mobility"))
    outcome = _last_outcome(history)
    score = 0.0
    reasons: list[str] = []

    if explicit:
        score += 70; reasons.append("explicit_remote_intent")
    if distance in {"far", "long", "very_far", "远", "远距", "长距离"}:
        score += 22; reasons.append("distance_pressure")
    if outcome in {"block", "bind", "miss", "dodge"}:
        score += 14; reasons.append(f"previous_{outcome}_needs_new_line")
    if any(k in defense for k in ("front", "strong", "high", "正面", "正面防御", "强防")):
        score += 12; reasons.append("front_defense_pressure")
    if any(k in opening for k in ("side", "rear", "angle", "侧", "背", "换线", "外侧")):
        score += 15; reasons.append("new_attack_axis")
    if any(k in terrain for k in ("obstacle", "pillar", "wall", "column", "桥", "柱", "墙", "障碍")):
        score += 8; reasons.append("environment_redirect_available")
    if any(k in mobility for k in ("high", "fast", "mobile", "高速", "灵活", "快速")):
        score += 6; reasons.append("tracking_value")
    if distance in {"close", "contact", "近", "贴身"}:
        score -= 12; reasons.append("close_range_prefers_handheld")
    if mode in REMOTE_MODES:
        score += 20; reasons.append("action_already_remote")

    score = max(0.0, min(100.0, score))
    # Explicit remote intent is authoritative; autonomous activation requires positive tactical utility.
    activate = explicit or (score >= 68 and (score + PATTERN_GAIN.get("orbit", 0) - PATTERN_BASE_COST["orbit"]) >= 18)
    if not activate:
        return {"capable": True, "activate": False, "score": round(score, 2), "mode": "HAND_HELD", "pattern": "release", "reason": "insufficient_tactical_value", "reasons": reasons}

    # Explicit control source wins; otherwise use the most generic confirmed control source.
    source = "qi"
    if isinstance(explicit_intent, dict):
        source = str(explicit_intent.get("control_source") or source)
    requested_mode = explicit_intent.get("control_mode") if isinstance(explicit_intent, dict) else None
    selected_mode = str(requested_mode or (mode if remote_existing else "TELEKINETIC"))
    if selected_mode not in REMOTE_MODES:
        selected_mode = "TELEKINETIC"

    explicit_pattern = explicit_intent.get("pattern") if isinstance(explicit_intent, dict) else None
    if explicit_pattern in REMOTE_PATTERNS:
        pattern = explicit_pattern
    elif any(k in opening for k in ("side", "rear", "angle", "侧", "背", "换线", "外侧")):
        pattern = "angle_change"
    elif any(k in terrain for k in ("obstacle", "pillar", "wall", "column", "桥", "柱", "墙", "障碍")):
        pattern = "environment_redirect"
    elif outcome in {"block", "bind"} or any(k in defense for k in ("front", "正面", "强防")):
        pattern = "multi_angle"
    elif any(k in mobility for k in ("high", "fast", "mobile", "高速", "灵活", "快速")):
        pattern = "tracking"
    else:
        pattern = "orbit"
    tactical_gain = float(score)
    control_cost = PATTERN_BASE_COST.get(pattern, 18.0)
    if pattern in {"multi_angle", "environment_redirect"}: control_cost += 8.0
    resource_pressure = _text(state.get("resource_pressure"))
    if any(k in resource_pressure for k in ("high", "critical", "高", "极高", "不足")): control_cost += 10.0
    if distance in {"close", "contact", "近", "贴身"}: control_cost += 8.0
    tactical_utility = tactical_gain + PATTERN_GAIN.get(pattern, 0.0) - control_cost

    return {
        "capable": True,
        "activate": True,
        "score": round(score, 2),
        "tactical_gain": round(tactical_gain, 2),
        "control_cost": round(control_cost, 2),
        "tactical_utility": round(tactical_utility, 2),
        "mode": selected_mode,
        "control_source": source,
        "pattern": pattern,
        "state_chain": REMOTE_PATTERNS[pattern],
        "reason": "tactical_remote_control_selected",
        "reasons": reasons,
        "category_independent": True,
        "identity_preserved": True,
        "mass_inertia_preserved": True,
        "no_new_event": True,
    }



def compile_execution_variant_semantics(weapon: str, mode: str, pattern: str, control_source: str = "qi") -> dict[str, str]:
    """Compile the semantic core for the selected execution variant.

    This is intentionally inside the existing adaptive weapon-control layer: it does not
    create a new runtime module or Event. It replaces hand-held wording whenever a remote
    execution variant is committed, preventing execution/prompt semantic divergence.
    """
    pattern_text = {
        "orbit": "脱手后沿环绕轨迹追踪目标",
        "tracking": "脱手后持续追踪目标并保持攻击线",
        "angle_change": "脱手后变线切入新的攻击轴",
        "multi_angle": "脱手后连续改变攻击轴形成多角度压力",
        "environment_redirect": "脱手后借明确环境锚点改变攻击轨迹",
        "release": "脱手后沿受控攻击轨迹完成攻击并回收",
    }.get(pattern, "脱手后沿受控攻击轨迹完成攻击并回收")
    core = (
        f"{weapon}进入{mode}御器执行变体：角色先建立{control_source}控制源并完成释放，"
        f"武器脱离手部动力链后独立保持质量与惯性，{pattern_text}，明确接触目标后依据结果连续回收；"
        "脱手状态不得继续描述手握驱动、瞬移或瞬间回手。"
    )
    return {
        "core_sentence": core,
        "weapon_execution_sentence": core,
        "execution_variant": "remote_execution_variant",
        "semantic_mode": mode,
        "semantic_pattern": pattern,
        "semantic_control_source": control_source,
        "semantic_source": "adaptive_weapon_control_v1.2",
    }

def build_execution_variant(action: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    """Build a physically coherent execution variant without mutating the source action knowledge."""
    out = deepcopy(action)
    if not decision.get("activate"):
        out["execution_variant"] = {"id": "HAND_HELD_NATIVE", "mode": "HAND_HELD", "source": "knowledge_native"}
        return out
    em = out.setdefault("execution_model", {})
    wc = em.setdefault("weapon_control", {})
    weapon = out.get("weapon")
    mode = decision.get("mode", "TELEKINETIC")
    pattern = decision.get("pattern", "orbit")
    chain = list(decision.get("state_chain", []))
    # The remote variant explicitly severs the hand-to-weapon coupling after release.
    em["joint_chain"] = {
        "id": f"remote_{pattern}",
        "path": "身体重心稳定→控制源建立→武器脱手→受控加速→轨迹调整→接触→结果反应→回收",
        "variant_source": "adaptive_weapon_control_v1.2",
    }
    em["center_of_mass"] = {
        **(em.get("center_of_mass") or {}),
        "weapon_separation": "武器脱手后独立保持质量与惯性，角色重心不再直接驱动武器轨迹",
        "remote_control_point": f"{decision.get('control_source','qi')}:weapon_control_point",
    }
    em["weapon_control"] = {
        "weapon": weapon, "weapon_identity": weapon,
        "control_mode": mode, "control_source": decision.get("control_source", "qi"),
        "grip": "脱手后取消手握约束；仅在释放前保持握持，释放后由控制源持续控制",
        "body_weapon_coupling": "身体重心与控制源分离；角色负责站架、施控与回收，武器保持独立惯性轨迹",
        "trajectory_lock": "脱手后沿受控轨迹连续运行，轨迹改变必须有控制原因",
        "contact_mode": "武器自身完成明确接触，接触角度与目标区服从受控攻击轴",
        "release_rule": "达到释放条件后由手部传递初始动量，随后控制源接管轨迹；不得瞬移",
        "forbidden": "不得在脱手状态继续描述手握驱动；不得复制武器；不得无因瞬移或瞬间回手",
        "remote_pattern": pattern, "remote_state_chain": chain,
        "mass_inertia_preserved": True, "category_independent": True,
    }
    em["temporal_phases"] = [
        {"phase":"setup","must_show":"站架、距离、控制源准备"},
        {"phase":"release","must_show":"握持解除与武器获得初始动量"},
        {"phase":"flight","must_show":"武器保持质量与惯性进入受控飞行"},
        {"phase":"tracking","must_show":"武器沿受控轨迹追踪或变线"},
        {"phase":"contact","must_show":"武器与目标明确接触并传递冲量"},
        {"phase":"reaction","must_show":"目标产生由接触方向和受力大小决定的反应"},
        {"phase":"return","must_show":"结果允许时沿连续轨迹回收，不瞬移"},
    ]
    ex = out.setdefault("execution", {})
    ex["startup"] = "先稳定站架并建立控制源，再完成脱手；不得把脱手阶段写成持续握持"
    ex["body_kinematics"] = "角色通过站架、重心稳定与控制手势/意念建立施控，不再由手臂连续驱动已脱手武器"
    ex["trajectory"] = f"释放→{pattern}→受控攻击轴→接触→结果→回收"
    ex["contact_point"] = "由武器实际接触部位完成接触，保持原武器几何身份"
    ex["recovery_path"] = "角色保持自身平衡，武器沿受控回收轨迹返回或停留在结果允许的位置"
    ex["tempo"] = "释放清晰、飞行连续、接触明确、结果后再回收"
    physics = out.setdefault("physics", {})
    physics["force_source"] = "weapon_mass_inertia + controlled_trajectory"
    physics["weight_transfer"] = "角色重心仅负责释放前动量与自身站架；脱手后武器保持独立质量与惯性"
    physics["momentum"] = "武器脱手后保持真实质量与惯性，控制源改变速度/方向但不消除惯性"
    physics["collision"] = "接触由武器本体产生冲量，目标反应必须与接触方向、速度和质量一致"
    physics["failure_physics"] = "未接触时继续沿受控轨迹运动或按回收规则减速，不允许瞬间静止"
    ps = out.setdefault("prompt_semantics", {})
    native_core = ps.get("core_sentence") or ps.get("weapon_execution_sentence") or ""
    if native_core and "native_core_sentence" not in ps:
        ps["native_core_sentence"] = native_core
    semantic_variant = compile_execution_variant_semantics(weapon, mode, pattern, decision.get("control_source", "qi"))
    # The selected execution variant becomes the authoritative prompt semantic core.
    # Native hand-held wording remains archived only as provenance and is never the active core.
    ps.update(semantic_variant)
    ps["causal_chain"] = "state → control_setup → release → independent_weapon_motion → trajectory_control → contact_geometry → opponent_outcome → recovery → transition"
    ps["weapon_control_variant"] = "remote_execution_variant"
    ps["variant_semantic_lock"] = True
    out["execution_variant"] = {
        "id": f"{weapon or 'weapon'}_{mode}_{pattern}", "mode": mode, "pattern": pattern,
        "source": "adaptive_weapon_control_v1.2", "base_action_id": action.get("action_id"),
        "mass_inertia_preserved": True, "hand_coupling_after_release": False,
    }
    out["weapon_control_runtime"] = {
        "mode": mode, "control_source": decision.get("control_source", "qi"), "pattern": pattern,
        "state_chain": chain, "score": decision.get("score", 0),
        "tactical_gain": decision.get("tactical_gain", 0), "control_cost": decision.get("control_cost", 0),
        "tactical_utility": decision.get("tactical_utility", 0),
        "reason": decision.get("reason", ""), "reasons": list(decision.get("reasons", [])),
        "fact_bound": True, "no_new_event": True, "execution_variant": "remote_execution_variant",
    }
    return out

def apply_control_overlay(action: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible entry point; now builds a real execution variant."""
    return build_execution_variant(action, decision)
