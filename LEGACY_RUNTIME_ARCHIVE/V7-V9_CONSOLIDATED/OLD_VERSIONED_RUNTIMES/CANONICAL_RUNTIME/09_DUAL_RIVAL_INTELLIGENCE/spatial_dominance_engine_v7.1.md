# Spatial Dominance Engine V7.1

## Purpose

Replace fixed character screen-side locking with dynamic combat spatial continuity.

The system must never define:
- Fighter A always left
- Fighter B always right

Instead it tracks:
- camera axis
- combat position
- pressure direction
- center ownership
- terrain advantage
- spatial control changes

## Core Rules

### Initial Axis

Establish readable combat geography during opening beats.

### Dynamic Reposition

Characters may cross screen positions only when caused by:
- dash
- dodge
- knockback
- pursuit
- aerial movement
- terrain interaction
- domain expansion

Every reposition must preserve:
- movement path
- facing logic
- attack direction
- camera continuity

## Spatial Dominance States

Each beat evaluates:

- ADVANCING
- RETREATING
- ENCIRCLED
- CORNERED
- CENTER_CONTROL
- TERRITORY_OVERRIDE
- RECOVERING

## Domain Combat Rule

Characters with field/domain abilities do not merely occupy a side of frame.
Their ability can transform the battlefield center.

Example:

Before domain:
Fighter A controls approach.

After domain:
Fighter B controls space volume.

Camera center should follow the active spatial authority.

## QA

Reject:
- unexplained side swaps
- teleport-like repositioning
- permanent left/right bias
- camera direction contradicting combat advantage
