# Move VFX Binding Runtime Hook

调用位置:
Action Graph -> VFX System

Mapping:

Move ID
+
Weapon
+
Impact Type
+
Combat Phase

=

VFX Node Selection

Example:
Sword Domain:
- sword intent
- spatial cuts
- floating blade trails
- pressure field

### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
