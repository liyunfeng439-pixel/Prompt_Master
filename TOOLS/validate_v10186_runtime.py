#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json
ROOT=Path(__file__).resolve().parents[1]
def loadmod(name, rel):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def validate_current_runtime():
    mod=loadmod('ultimate','25_WEAPON_INTELLIGENCE_LAYER_2.4_WEAPON_ABILITY_FUSION_RUNTIME/WEAPON_SIGNATURE_ULTIMATE_LIBRARY_V1.0.py')
    harness=(ROOT/'47_RUNTIME_EXECUTION_HARNESS_V3.1/runtime_harness_v1090.py').read_text(encoding='utf8')
    return (mod.VERSION=='1.1' and 'validate_v10186_runtime.py' in harness and 'signature_ultimate_action_compatibility' in harness)
if __name__=='__main__':
    print('V10.18.6_CURRENT_RUNTIME_PREFLIGHT_PASS' if validate_current_runtime() else 'V10.18.6_CURRENT_RUNTIME_PREFLIGHT_FAIL')
    raise SystemExit(0 if validate_current_runtime() else 1)
