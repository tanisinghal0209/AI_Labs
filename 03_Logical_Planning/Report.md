# Logical Planning Laboratory Report

## Task 0 — Planning problem

The initial state is `I = {At(Robot,A), At(Package,A)}`. The goal is `G = {At(Package,C)}`.

| Action | Preconditions | Positive effects | Negative effects |
|---|---|---|---|
| `Move(A,B)` | `At(Robot,A)` | `At(Robot,B)` | `At(Robot,A)` |
| `Move(B,A)` | `At(Robot,B)` | `At(Robot,A)` | `At(Robot,B)` |
| `Move(B,C)` | `At(Robot,B)` | `At(Robot,C)` | `At(Robot,B)` |
| `Move(C,B)` | `At(Robot,C)` | `At(Robot,B)` | `At(Robot,C)` |
| `PickUp(Package,A)` | `At(Robot,A)`, `At(Package,A)` | `Holding(Package)` | `At(Package,A)` |
| `Drop(Package,C)` | `At(Robot,C)`, `Holding(Package)` | `At(Package,C)` | `Holding(Package)` |

Initially, `Move(A,B)` and `PickUp(Package,A)` are applicable. The other moves have an unsatisfied robot-location precondition. `Drop(Package,C)` is not applicable because neither `At(Robot,C)` nor `Holding(Package)` is true.

## Task 1 — Manual plan

| State | Facts after action |
|---|---|
| `S0` | `At(Robot,A)`, `At(Package,A)` |
| `S1` after `PickUp(Package,A)` | `At(Robot,A)`, `Holding(Package)` |
| `S2` after `Move(A,B)` | `At(Robot,B)`, `Holding(Package)` |
| `S3` after `Move(B,C)` | `At(Robot,C)`, `Holding(Package)` |
| `S4` after `Drop(Package,C)` | `At(Robot,C)`, `At(Package,C)` |

The plan is `PickUp(Package,A)`, `Move(A,B)`, `Move(B,C)`, `Drop(Package,C)`. Every action's preconditions are true in the state immediately before it, and the final state contains the goal.

## Task 2 — Prompt and generated planner

This task-specific prompt was used to guide the supplied implementation; it is recorded here as the prompt for this completion, not as a reconstructed earlier chat transcript.

```text
I want to implement a simple planning agent in Python. Represent a state as a set of logical propositions. Each action should contain a name, positive preconditions, negative preconditions, positive effects, and negative effects. An action is applicable if its positive preconditions are present and its negative preconditions are absent from the current state. When an action is applied, remove its negative effects from the state and add its positive effects. Use breadth-first search to find a sequence of actions that achieves a specified goal. Detect when no plan exists, print the actions and the states reached after each action, and explain the implementation and assumptions.

Problem: the robot and package start at A. The robot can move A<->B and B<->C. It can pick up the package at A and drop it at C. The goal is At(Package,C).
```

The Python implementation represents facts as strings in a set. `Action.is_applicable` performs the precondition check, `Action.apply` performs the effects, and `bfs_planner` searches over reachable states. `visited` is a set of frozen states, so cyclic moves do not cause an infinite search. The planner assumes that all actions have equal cost and returns a minimum-action plan.

## Task 3 — Test results

The existing test suite checks each returned action and resulting state, rather than trusting the printed plan.

| Test | Change or setup | Result |
|---|---|---|
| A — Solvable | Original initial state, actions, and goal | Plan found; every action was applicable; final state contains `At(Package,C)`. PASS. |
| B — Impossible | Remove `PickUp` | No plan found. PASS. |
| C — Irrelevant action | Add robot-only moves that do not move the package | `At(Robot,C)` alone does not satisfy `At(Package,C)`; the planner still finds and verifies a delivery plan. PASS. |

The captured run is under `Python/results/test_run_output.txt`. The Prolog checks are captured under `Prolog/results/prolog_run_output.txt`.

## Task 4 — Logic and search

Logic determines whether the current state satisfies an action's preconditions and applies its effects to form a successor state. Search determines which sequence of those applicable actions to explore. In the implementation, logical applicability is checked before each successor is created; breadth-first search explores the resulting state graph by increasing plan length and checks the goal at every dequeued state.

The missing step in the lab's flow is **select and apply an applicable action**: current state → check preconditions → choose an applicable action → generate successor state → search alternatives → test goal.

## Task 5 — Independent plan verification

For the four-step plan, the verifier checks before each transition that the action is applicable, applies it independently, and compares that state with the state recorded by the planner. It then checks the final goal. This is stronger evidence than an explanation that merely says the plan is valid because it mechanically checks preconditions and effects at every step. If they disagreed, the state-by-state execution should be investigated rather than trusting either assertion without inspection.

## Optional Prolog extension

### Facts, rules, and queries

The facts `connected(a,b)`, `connected(b,a)`, `connected(b,c)`, and `connected(c,b)` describe the links. `can_move(X,Y) :- connected(X,Y).` succeeds for `can_move(a,b)` because the matching fact is present. `can_move(a,c)` fails because no such connection fact can be derived. The rule expresses the implication `Connected(X,Y) → CanMove(X,Y)` for variables `X` and `Y`.

`valid_move(a,b)` and `valid_move(b,c)` succeed; `valid_move(a,c)` fails. The proposed move `Move(a,c)` is therefore not supported by this knowledge base. This is a direct, independent check of the connection preconditions used to propose a move.

### Wet-road inference

The fact `wet_road.` and rules `slippery :- wet_road.` and `reduce_speed :- slippery.` yield:

```text
wet_road ⇒ slippery ⇒ reduce_speed
```

The recorded SWI-Prolog suite passed 10 checks, covering the connected facts, `can_move` and `valid_move` with positive and negative cases, and the wet-road inference.

### Prolog reflection

A fact is a declared piece of knowledge such as `connected(a,b)`. A rule derives a conclusion when its body succeeds, such as deriving `slippery` from `wet_road`. A query asks the Prolog engine whether the supplied facts and rules can prove a goal. Prolog can independently check a proposed movement from a Python planner; this separation can catch an unsupported transition even if the planner or its explanation is mistaken.

## Reflection answers

1. **Why specify preconditions and effects first?** They define exactly when an action is legal and how it changes a state, giving both code and tests an unambiguous contract.
2. **What if preconditions are skipped?** The planner could drop a package it is not holding or move the robot from a location it does not occupy.
3. **Why is a plausible plan not necessarily valid?** It may contain an inapplicable step or fail to establish the package-at-destination goal; every transition must be checked against its state.
4. **What did the LLM contribute?** It helped turn the specified set-based action model and BFS procedure into executable Python and supplied a starting structure for tests.
5. **What needed independent verification?** Applicability of every action, state transitions, impossible-case handling, goal satisfaction, and the Prolog facts/rules.
6. **Where is logical reasoning used?** The planner checks whether positive and negative preconditions hold, then applies effects to create a successor state.
7. **How does planning relate to search?** Planning defines legal state transitions with actions; search explores sequences of those transitions until it reaches a state satisfying the goal.

## Reproduce

From the project root:

```bash
python3 03_Logical_Planning/Python/planner.py
python3 03_Logical_Planning/Python/test_planner.py
swipl -q -s 03_Logical_Planning/Prolog/test_prolog.pl -g run_tests -t halt
```

The lab's Python and Prolog artifacts and their captured outputs are kept in separate subfolders.
