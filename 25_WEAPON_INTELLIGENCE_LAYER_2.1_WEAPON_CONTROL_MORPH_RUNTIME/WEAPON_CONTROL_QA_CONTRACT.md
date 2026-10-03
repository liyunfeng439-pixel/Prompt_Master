# Universal Weapon Control Fidelity QA V1.1

Checks:
- every canonical weapon is remote-control capable
- weapon category must never block TELEKINETIC / SPIRIT_CONTROLLED / REMOTE_ATTACK / RETURN_CONTROL
- remote weapon actions must have a control source
- remote weapon actions must declare a state transition from hand to airborne/target_space/returning as applicable
- trajectory changes require an explicit control cause
- returning weapons require return control or an explicit recovery event
- morph changes require explicit transition
- weapon identity cannot change
- weapon count cannot change
- weapon mass/inertia cannot be removed by remote control
- remote control cannot become teleportation
- all existing HAND_HELD behavior remains valid
