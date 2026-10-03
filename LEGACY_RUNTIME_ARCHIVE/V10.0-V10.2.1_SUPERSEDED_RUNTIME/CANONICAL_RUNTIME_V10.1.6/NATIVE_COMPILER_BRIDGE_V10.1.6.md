# Native Compiler Bridge V10.1.6

Authoritative compilation order:

Combat Director Brain
↓
Knowledge Retrieval / Candidate Filtering / Tactical Action Selection
↓
Weapon Integrity Gate
↓
V4 Action Knowledge Resolution / ACTION_EXECUTION_CONTRACT
↓
Action Transition Graph Validation
↓
Action / Ability Runtime + Actor Reaction
↓
Beat Graph
↓
Shot Compression Engine
↓
Shot Budget V10.1.6
↓
SHOT_IR V10.1.6
↓
NATIVE_OUTPUT_ROUTER_V10.1.6
↓
Universal / Seedance 2.5 / MiniMax H3 Adapter
↓
QA / Repair / Regression

The bridge owns no model-specific semantics. Adapters own model-facing wording only; SHOT_IR remains the invariant semantic source.

Hard ordering rule:
Combat Director MUST precede Beat Graph. Action Transition Validation MUST precede Beat Graph. Shot Compression MUST precede final SHOT_IR compilation. Shot Budget MUST validate the final shot allocation before model adaptation.
