# V10.9.0 Zero-Copy Runtime Execution Harness

The current harness runs Validator, Action Resolution, Combat Director planning, SHOT_IR generation, Native Compiler and Deep Semantic QA in-process.

Key guarantees:
- no character/weapon/ending hardcode;
- dynamic phase strategy and opponent prediction;
- bounded transition replanning and A→B→C lookahead;
- dynamic shot allocation with 30s hard maximum of 7;
- open/draw/escape/victory endings without invented facts;
- Zero-Copy knowledge access;
- Universal / Seedance 2.5 / MiniMax H3 compiled from one SHOT_IR.
