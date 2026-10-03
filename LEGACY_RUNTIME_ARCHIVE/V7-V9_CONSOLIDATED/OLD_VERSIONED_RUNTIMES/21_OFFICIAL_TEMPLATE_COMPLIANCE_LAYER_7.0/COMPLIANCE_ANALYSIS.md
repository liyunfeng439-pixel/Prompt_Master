# Official Template Compliance Layer 7.0

## Audit Result
Previous package already enforced five outputs:
- Universal
- Seedance 2.5 CN/EN
- MiniMax H3 CN/EN

Problem found:
The templates were labeled Official Style / Official Format, but the runtime did not contain a strict model-template contract layer. Generation could still fall back to generic cinematic output.

Upgrade:
- Hard route model outputs through template IDs.
- Reject missing bilingual native outputs.
- Separate internal combat reasoning from final model prompts.
- Preserve combat generation core.
