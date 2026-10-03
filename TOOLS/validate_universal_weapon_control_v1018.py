#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]

def read(rel):
    return (ROOT/rel).read_text(encoding='utf-8')

def main():
    control=read('25_WEAPON_INTELLIGENCE_LAYER_2.1_WEAPON_CONTROL_MORPH_RUNTIME/WEAPON_CONTROL_RUNTIME.yaml')
    registry=read('25_WEAPON_INTELLIGENCE_LAYER_2.0/weapon_registry.yaml')
    graph=read('25_WEAPON_INTELLIGENCE_LAYER_2.2_WEAPON_COMBAT_BEHAVIOR_GRAPH/WEAPON_BEHAVIOR_GRAPH.yaml')
    tactical=read('25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/WEAPON_TACTICAL_RUNTIME.yaml')
    qa=read('25_WEAPON_INTELLIGENCE_LAYER_2.1_WEAPON_CONTROL_MORPH_RUNTIME/WEAPON_CONTROL_QA_CONTRACT.md')
    checks={
      'universal_control_enabled':'enabled: true' in control and 'applies_to: all_canonical_weapons' in control,
      'telekinetic_allowed':'- TELEKINETIC' in control,
      'spirit_allowed':'- SPIRIT_CONTROLLED' in control,
      'remote_attack_allowed':'- REMOTE_ATTACK' in control,
      'return_control_allowed':'- RETURN_CONTROL' in control,
      'universal_registry':'default_control_profile: universal_weapon' in registry,
      'category_independent_graph':'remote_control_category_gate: false' in graph,
      'universal_graph':'universal_remote_flow:' in graph,
      'tactical_universal':'remote_control_is_category_independent' in tactical,
      'fan_registry':'- fan' in registry,
      'qa_universal':'every canonical weapon is remote-control capable' in qa,
      'no_identity_break':'preserve_weapon_identity: true' in control and 'preserve_weapon_count: true' in control,
      'adaptive_module_exists':(ROOT/'25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py').exists(),
      'adaptive_threshold':'autonomous_threshold: 68' in tactical,
      'adaptive_patterns':all(x in tactical for x in ['orbit','angle_change','multi_angle','environment_redirect']),
    }
    bad=[k for k,v in checks.items() if not v]
    print('UNIVERSAL_WEAPON_CONTROL_CHECKS='+str(len(checks)))
    print('UNIVERSAL_WEAPON_CONTROL_FAILED='+str(len(bad)))
    if bad:
        print('FAILED='+','.join(bad)); return 1
    print('UNIVERSAL_WEAPON_CONTROL_V10.18.1=PASS')
    return 0
if __name__=='__main__': sys.exit(main())
