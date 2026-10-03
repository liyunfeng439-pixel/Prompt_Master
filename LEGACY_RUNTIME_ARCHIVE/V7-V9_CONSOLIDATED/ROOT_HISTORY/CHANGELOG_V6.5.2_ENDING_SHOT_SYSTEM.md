# V6.5.2 Ending Shot System

## Added
- Ending Shot Selector Runtime
- 12 result-matched ending templates
- Ending Shot Selection Contract
- Explicit template mismatch guards
- Ending-shot regression coverage

## Pipeline
Final Combat Sequence → Result Lock → Ending State → Ending Shot Selection → Ending Shot Runtime → Semantic IR

## Design rule
The selector chooses how to observe an already-locked result. It never changes the result or creates a new physical event.
