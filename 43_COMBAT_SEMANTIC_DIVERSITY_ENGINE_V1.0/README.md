# Combat Semantic Diversity Engine V1.0 (V10.9.0)

Prevents the final combat prompt from collapsing many action records into the same movement vocabulary. The engine selects semantically different execution components while keeping every action causally executable.

Selection groups:
- movement: footwork/body/joint/center-of-mass (at most one per action from this group)
- line: trajectory/contact geometry (at most one per action from this group)
- recovery: rendered only when the action outcome requires it
- reaction: retained as the concrete post-result consequence

Tactical rationale is surfaced once per shot when repeated, instead of being echoed on every action sentence.
