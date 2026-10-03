#!/usr/bin/env python3
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

PHASE_ORDER=["establish","test","tactical_shift","escalation","climax","resolution"]

@dataclass
class NarrativeEvent:
    current_state: str
    combat_intent: str
    reason_for_action: str
    state_transition: str
    escalation_level: int
    next_expected_state: str
    provenance: str
    reason_source: str
    phase_role: str

    def to_dict(self): return asdict(self)

def _prev(history): return history[-1] if history else None

def infer_intent(item, phase, prev, outcome, action):
    explicit=(item.get("combat_intent") or item.get("intent") or "").strip()
    if explicit: return explicit, "explicit_intent"
    tactical=(item.get("tactical_problem") or "").strip()
    if tactical: return f"解决战术问题：{tactical}", "explicit_tactical_problem"
    if prev:
        po=prev.get("outcome","")
        if po in {"block","dodge","miss"}: return "根据上一动作未突破防线，调整攻击方式", "previous_result"
        if po in {"hit","counter","throw","disarm"}: return "利用上一动作产生的结果继续施压或转换战术", "previous_result"
    goal=getattr(phase,"phase_goal","") if phase else ""
    if goal: return f"推进当前战斗阶段目标：{goal}", "phase_goal"
    dist=item.get("distance")
    if dist: return f"根据当前交战距离选择可执行攻击线（{dist}）", "spatial_state"
    return "延续当前有效战斗因果并寻找下一次战术窗口", "bounded_inference"

def infer_phase_role(index,total,prev,outcome,phase_id=""):
    p=str(phase_id or "").lower()
    if "final" in p or "resolution" in p: return "resolution"
    if index==0: return "establish"
    if outcome in {"block","dodge","miss","bind"}: return "test" if index<max(2,total//3) else "tactical_shift"
    if prev and prev.get("outcome") in {"block","dodge","miss"} and outcome in {"hit","counter","throw","disarm"}: return "tactical_shift"
    if outcome in {"ability","ability_clash"}: return "escalation"
    if index>=max(0,total-2): return "climax"
    return "escalation" if index>=max(1,total//2) else "test"

def escalation_level(index,total,outcome,prev):
    base=1 if total<=1 else 1+int((index/(total-1))*3)
    if outcome in {"ability","ability_clash","throw","disarm"}: base+=1
    if prev and prev.get("outcome") in {"block","dodge","miss"} and outcome in {"hit","counter","throw","disarm"}: base+=1
    return max(1,min(5,base))

def semantic_next_state(outcome, role):
    if outcome in {"block","dodge","miss"}: return "重新建立攻击线并寻找新的战术窗口"
    if outcome in {"bind"}: return "利用控制结果调整距离并准备下一步动作"
    if outcome in {"hit","counter"}: return "利用当前命中结果继续施压或转换攻击轴"
    if outcome in {"throw","disarm"}: return "利用失衡或失械结果进入新的控制阶段"
    if outcome in {"ability","ability_clash"}: return "进入更高强度的能力对抗或结果观察"
    if role=="climax": return "进入最终结果确认"
    return "延续当前有效战斗因果"

def build_event(item, action, phase, previous, outcome, current_state, next_state, index, total):
    intent,source=infer_intent(item,phase,previous,outcome,action)
    role=infer_phase_role(index,total,previous,outcome,getattr(phase,"phase_id","") if phase else "")
    level=escalation_level(index,total,outcome,previous)
    reason=f"{intent}。"
    transition=f"{current_state} → {next_state}"
    return NarrativeEvent(current_state or "current_combat_state",intent,reason,transition,level,next_state or "next_combat_state", "runtime_derived", source, role).to_dict()

def build_curve(events,duration):
    n=len(events)
    if n==0: return {"version":"10.18.0","duration_s":duration,"segments":[],"adaptive":True}
    roles=[e.get("narrative",{}).get("phase_role","test") for e in events if e.get("type")=="action_result"]
    # Compress consecutive roles into semantic segments; no fixed stage requirement.
    segments=[]; start=0
    for i,r in enumerate(roles+[None]):
        if i==0: continue
        if i==len(roles) or r!=roles[start]:
            frac=(i-start)/max(1,n); segments.append({"role":roles[start],"event_start":start,"event_end":i-1,"duration_s":round(duration*frac,2)})
            start=i
    if segments:
        delta=round(duration-sum(s["duration_s"] for s in segments),2); segments[-1]["duration_s"]+=delta
    return {"version":"10.18.0","duration_s":duration,"adaptive":True,"segments":segments,"phase_roles":roles,"no_fixed_stage_template":True}

def validate(runtime):
    errors=[]; evs=[e for e in runtime.get("events",[]) if e.get("type")=="action_result"]
    for e in evs:
        n=e.get("narrative") or {}
        for k in ("current_state","combat_intent","reason_for_action","state_transition","escalation_level","next_expected_state"):
            if not n.get(k): errors.append(f"NARRATIVE_FIELD_MISSING:{e.get('event_id')}:{k}")
    ids=[e.get("event_id") for e in evs]
    lock_index=next((i for i,e in enumerate(runtime.get("events",[])) if e.get("type")=="result_lock"),None)
    if lock_index is not None:
        if any(e.get("type")=="action_result" for e in runtime.get("events",[])[lock_index+1:]): errors.append("NARRATIVE_POST_RESULT_LOCK")
    curve=runtime.get("narrative_curve") or {}
    if round(sum(float(s.get("duration_s",0)) for s in curve.get("segments",[])),2)!=round(float(curve.get("duration_s",0)),2): errors.append("NARRATIVE_CURVE_DURATION_MISMATCH")
    return errors
