# Model Output Router — Compatibility Facade

This file is not a competing output authority.

All current model output routing MUST delegate to:
`../NATIVE_OUTPUT_ROUTER_V10.1/router.yaml`

Current flow:

SHOT_IR V10.1.1
-> NATIVE_OUTPUT_ROUTER_V10.1
-> Universal / Seedance 2.5 / MiniMax H3 adapter
-> QA / Repair

The legacy adapter documentation in this directory remains reusable knowledge only. It must not bypass the current router or introduce a second output contract.
