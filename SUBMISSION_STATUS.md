# Submission Status

All four supplied laboratory briefs now have a matching report, implementation or exercise evidence, and captured verification results.

| Lab | Submission contents | Verification |
|---|---|---|
| Search and A* | Search formulation, design, prompt, A* and BFS code, heuristic experiments, tests, reflections | 7 tests passed; both algorithms found length 40; original-map runs expanded 63 states each. |
| Neural Models | XOR specification, PyTorch 2–2–1 and 2–2–3 experiments, prompt, loss/prediction/gradient/symmetry/activation results, reflections | Script assertions passed; 4/4 binary labels and 4/4 three-class labels correct; gradient and softmax checks passed. |
| Logical Planning | Action specification, manual plan, prompt, Python test results, logic/search explanation, Prolog verifier and reflections | Python scenarios A/B/C passed; 10 Prolog checks passed. |
| Goal-Based Agents | Problem answers, agent design, prompt record, warehouse BFS agent and tests | 6 tests passed; exact map route has 20 moves. |

## Reproduction commands

Run these from the project root. The Neural Models command requires Python 3 with PyTorch installed. Prolog checks require SWI-Prolog.

```bash
python3 01_Search_and_A_Star/test_search_agent.py
python3 01_Search_and_A_Star/run_experiments.py
python3 02_Neural_Models/neural_models_experiment.py
python3 03_Logical_Planning/Python/test_planner.py
swipl -q -s 03_Logical_Planning/Prolog/test_prolog.pl -g run_tests -t halt
python3 04_Goal_Based_Agents/test_warehouse_agent.py
```

The associated run transcripts are stored under each lab's `Results`, `results`, or lab root directory. The reports distinguish prompt specifications written for this completion from historical chat transcripts, which were not part of the supplied workspace.
