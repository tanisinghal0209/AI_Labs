from planner import Action, bfs_planner


# ============================================================
# Helper function
# ============================================================

def verify_plan(initial_state, plan, goal):
    """
    Actually execute the returned plan from the initial state
    and verify that every action is applicable.

    Returns:
        True  -> plan is valid and achieves goal
        False -> plan is invalid
    """

    current_state = set(initial_state)

    if plan is None:
        return False

    print("\nVerifying every action:")

    for step, (action, expected_state) in enumerate(plan, start=1):

        print(f"\nStep {step}: {action}")

        # Check whether action is actually applicable
        if not action.is_applicable(current_state):
            print("ERROR: Action is NOT applicable!")
            return False

        print("Preconditions satisfied.")

        # Apply the action ourselves
        current_state = action.apply(current_state)

        print("Resulting state:", sorted(current_state))

        # Check that the state produced by the planner
        # agrees with the state produced by applying the action
        if current_state != expected_state:
            print("ERROR: Planner state does not match actual state!")
            return False

    # Finally check the goal
    if goal.issubset(current_state):
        print("\nGoal is satisfied.")
        return True
    else:
        print("\nGoal is NOT satisfied.")
        return False


# ============================================================
# Original Warehouse Actions
# ============================================================

def create_warehouse_actions():

    actions = [

        # -------------------------
        # Move A -> B
        # -------------------------
        Action(
            name="Move(A,B)",
            preconditions_pos={
                "At(Robot,A)"
            },
            effects_pos={
                "At(Robot,B)"
            },
            effects_neg={
                "At(Robot,A)"
            }
        ),

        # -------------------------
        # Move B -> A
        # -------------------------
        Action(
            name="Move(B,A)",
            preconditions_pos={
                "At(Robot,B)"
            },
            effects_pos={
                "At(Robot,A)"
            },
            effects_neg={
                "At(Robot,B)"
            }
        ),

        # -------------------------
        # Move B -> C
        # -------------------------
        Action(
            name="Move(B,C)",
            preconditions_pos={
                "At(Robot,B)"
            },
            effects_pos={
                "At(Robot,C)"
            },
            effects_neg={
                "At(Robot,B)"
            }
        ),

        # -------------------------
        # Move C -> B
        # -------------------------
        Action(
            name="Move(C,B)",
            preconditions_pos={
                "At(Robot,C)"
            },
            effects_pos={
                "At(Robot,B)"
            },
            effects_neg={
                "At(Robot,C)"
            }
        ),

        # -------------------------
        # Pick Up Package at A
        # -------------------------
        Action(
            name="PickUp(Package,A)",
            preconditions_pos={
                "At(Robot,A)",
                "At(Package,A)"
            },
            effects_pos={
                "Holding(Package)"
            },
            effects_neg={
                "At(Package,A)"
            }
        ),

        # -------------------------
        # Drop Package at C
        # -------------------------
        Action(
            name="Drop(Package,C)",
            preconditions_pos={
                "At(Robot,C)",
                "Holding(Package)"
            },
            effects_pos={
                "At(Package,C)"
            },
            effects_neg={
                "Holding(Package)"
            }
        )
    ]

    return actions


# ============================================================
# TEST A
# Solvable Problem
# ============================================================

def test_A():

    print("\n")
    print("=" * 60)
    print("TEST A: SOLVABLE PROBLEM")
    print("=" * 60)

    initial_state = {
        "At(Robot,A)",
        "At(Package,A)"
    }

    goal = {
        "At(Package,C)"
    }

    actions = create_warehouse_actions()

    print("\nInitial State:")
    print(sorted(initial_state))

    print("\nGoal:")
    print(sorted(goal))

    plan, final_state = bfs_planner(
        initial_state,
        actions,
        goal
    )

    if plan is None:

        print("\nRESULT: FAIL")
        print("The planner should have found a plan.")

        return

    print("\nPlan found:")

    for i, (action, state) in enumerate(plan, start=1):
        print(f"{i}. {action}")
        print("   ->", sorted(state))

    # Verify every action
    valid = verify_plan(
        initial_state,
        plan,
        goal
    )

    if valid:
        print("\nTEST A RESULT: PASS")
        print("The plan is valid and achieves At(Package,C).")
    else:
        print("\nTEST A RESULT: FAIL")


# ============================================================
# TEST B
# Impossible Problem
# Remove PickUp action
# ============================================================

def test_B():

    print("\n")
    print("=" * 60)
    print("TEST B: IMPOSSIBLE PROBLEM")
    print("=" * 60)

    initial_state = {
        "At(Robot,A)",
        "At(Package,A)"
    }

    goal = {
        "At(Package,C)"
    }

    actions = create_warehouse_actions()

    # --------------------------------------------------------
    # Remove PickUp action
    # --------------------------------------------------------

    actions = [
        action
        for action in actions
        if not action.name.startswith("PickUp")
    ]

    print("\nInitial State:")
    print(sorted(initial_state))

    print("\nGoal:")
    print(sorted(goal))

    print("\nPickUp action has been removed.")

    plan, final_state = bfs_planner(
        initial_state,
        actions,
        goal
    )

    if plan is None:

        print("\nPlanner output:")
        print("No plan found.")

        print("\nTEST B RESULT: PASS")
        print(
            "The planner correctly detected that the "
            "problem is impossible."
        )

    else:

        print("\nTEST B RESULT: FAIL")
        print("The planner incorrectly found a plan:")
        for action, state in plan:
            print(action)


# ============================================================
# TEST C
# Irrelevant Actions
# ============================================================

def test_C():

    print("\n")
    print("=" * 60)
    print("TEST C: IRRELEVANT ACTION")
    print("=" * 60)

    initial_state = {
        "At(Robot,A)",
        "At(Package,A)"
    }

    goal = {
        "At(Package,C)"
    }

    actions = create_warehouse_actions()

    # --------------------------------------------------------
    # Add irrelevant robot-only actions
    # --------------------------------------------------------

    actions.append(
        Action(
            name="MoveRobotOnly(A,B)",
            preconditions_pos={
                "At(Robot,A)"
            },
            effects_pos={
                "At(Robot,B)"
            },
            effects_neg={
                "At(Robot,A)"
            }
        )
    )

    actions.append(
        Action(
            name="MoveRobotOnly(B,C)",
            preconditions_pos={
                "At(Robot,B)"
            },
            effects_pos={
                "At(Robot,C)"
            },
            effects_neg={
                "At(Robot,B)"
            }
        )
    )

    print("\nInitial State:")
    print(sorted(initial_state))

    print("\nGoal:")
    print(sorted(goal))

    print("\nIrrelevant actions added:")
    print("MoveRobotOnly(A,B)")
    print("MoveRobotOnly(B,C)")

    # --------------------------------------------------------
    # First demonstrate the important point manually:
    #
    # Robot can reach C without package reaching C.
    # --------------------------------------------------------

    print("\n--- Checking robot-only path ---")

    current_state = set(initial_state)

    robot_only_actions = [
        action for action in actions
        if action.name in [
            "MoveRobotOnly(A,B)",
            "MoveRobotOnly(B,C)"
        ]
    ]

    for action in robot_only_actions:

        if action.is_applicable(current_state):

            current_state = action.apply(current_state)

            print(action)
            print("->", sorted(current_state))

    print("\nAfter robot-only actions:")

    print(sorted(current_state))

    if "At(Robot,C)" in current_state:
        print("Robot reached C.")

    if "At(Package,C)" not in current_state:
        print("Package did NOT reach C.")

    # --------------------------------------------------------
    # Therefore Robot(C) must NOT satisfy Package(C)
    # --------------------------------------------------------

    if "At(Package,C)" in current_state:

        print("\nTEST C RESULT: FAIL")
        print("Package incorrectly appears to be at C.")

        return

    print("\nCorrect:")
    print("At(Robot,C) != At(Package,C)")

    # --------------------------------------------------------
    # Now run the actual planner.
    # --------------------------------------------------------

    print("\n--- Running BFS planner ---")

    plan, final_state = bfs_planner(
        initial_state,
        actions,
        goal
    )

    if plan is None:

        print("\nTEST C RESULT: FAIL")
        print("Planner should be able to deliver the package.")

        return

    print("\nPlanner found:")

    for i, (action, state) in enumerate(plan, start=1):

        print(f"{i}. {action}")
        print("   ->", sorted(state))

    # Verify the returned plan
    valid = verify_plan(
        initial_state,
        plan,
        goal
    )

    if valid:

        print("\nTEST C RESULT: PASS")
        print(
            "The planner did not confuse the robot "
            "reaching C with the package reaching C."
        )

    else:

        print("\nTEST C RESULT: FAIL")


# ============================================================
# Run all tests
# ============================================================

if __name__ == "__main__":

    test_A()
    test_B()
    test_C()