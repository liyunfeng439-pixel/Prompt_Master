# V4 Action Knowledge Runtime Bridge V1.1

The V4 action layer is executable knowledge only after three gates pass:

`Weapon Integrity → V4 Schema Resolution → ACTION_EXECUTION_CONTRACT`

V10.9.0 adds a mandatory Weapon Execution Integrity Gate, action-level transition contracts and an Ability Execution Contract bridge for persistent/escalation abilities.

Trace chain:
`knowledge_action_id → execution_contract_id → event_id → beat_id → shot_id`
plus `ability_contract_id` when an ability event is used.
