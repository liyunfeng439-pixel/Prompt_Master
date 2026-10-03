# Deep Prompt Semantic QA V2.0

Hard PASS gates:
1. no Runtime terminology leakage
2. no exact duplicate sentences
3. no semantic bundle collision at Jaccard >= 0.72
4. component reuse ratio <= 0.22 on the standard 30s fixture
5. at least 4 combat families and 4 outcome classes in the regression fixture
6. at least 6 distinct component bundles for the 10-action fixture
7. trajectory phrase occurrences <= 2
8. body-mechanics phrase occurrences <= 1
9. ending/result/no-chase preserved

Telemetry:
- deep n-gram repetition is reported after removing common actor/outcome boilerplate; low-level repetition is not a hard failure when component diversity passes.

Semantic diversity means changing the selected execution components, not merely replacing words with synonyms.
