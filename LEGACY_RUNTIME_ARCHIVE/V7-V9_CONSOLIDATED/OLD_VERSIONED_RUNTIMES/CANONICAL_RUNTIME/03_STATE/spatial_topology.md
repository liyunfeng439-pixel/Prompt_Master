# Spatial Topology Runtime

Maintain a lightweight 3D battlefield graph across the whole sequence.

## Required state
- actor position and facing
- relative distance and attack side
- elevation and support surface
- occupied / forbidden zones
- obstacles and destructibles
- weapon reach envelope
- camera position and viewing axis
- last known action origin and destination

## Continuity rules
- No unexplained teleportation.
- Preserve left/right screen relationships unless a motivated axis transition is declared.
- A movement must have an origin, trajectory and destination.
- A collision must reference the contacted object and contact direction.
- Destruction changes the topology for later beats; destroyed objects cannot silently return to intact state.
