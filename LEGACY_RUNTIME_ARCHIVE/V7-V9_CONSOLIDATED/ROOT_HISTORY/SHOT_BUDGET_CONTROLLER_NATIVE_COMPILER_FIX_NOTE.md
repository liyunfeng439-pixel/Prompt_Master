# Shot Budget Controller Native Compiler Integration Fix

This patch restores the missing runtime connection between the V7.9.5.3 Shot Budget Controller and the existing Seedance 2.5 / MiniMax H3 Native Model Output pipeline.

No existing features are replaced.

Changed:
- Added Shot Budget -> Shot IR bridge
- Added compiler field mapping
- Preserved official model templates

Not changed:
- Combat Intelligence
- Character System
- Action Library
- VFX System
- Physics System
- Camera System
- Seedance 2.5 Template
- MiniMax H3 Template
