from collections import deque


class Action:
    def __init__(
        self,
        name,
        preconditions_pos=None,
        preconditions_neg=None,
        effects_pos=None,
        effects_neg=None
    ):
        self.name = name

        self.preconditions_pos = set(preconditions_pos or [])
        self.preconditions_neg = set(preconditions_neg or [])

        self.effects_pos = set(effects_pos or [])
        self.effects_neg = set(effects_neg or [])

    def is_applicable(self, state):
        """
        An action is applicable if:
        1. Every positive precondition is in the state.
        2. Every negative precondition is NOT in the state.
        """

        positive_ok = self.preconditions_pos.issubset(state)
        negative_ok = self.preconditions_neg.isdisjoint(state)

        return positive_ok and negative_ok

    def apply(self, state):
        """
        Apply the action to a state.

        First remove negative effects,
        then add positive effects.
        """

        new_state = set(state)

        new_state -= self.effects_neg
        new_state |= self.effects_pos

        return new_state

    def __str__(self):
        return self.name


def goal_reached(state, goal):
    """
    The goal is reached if every goal proposition
    is present in the current state.
    """

    return goal.issubset(state)


def bfs_planner(initial_state, actions, goal):
    """
    Breadth-First Search planning algorithm.

    Returns:
        List of (action, state) pairs if a plan exists.
        None if no plan exists.
    """

    initial_state = set(initial_state)

    # Queue stores:
    # (current state, sequence of actions)
    queue = deque()

    queue.append((initial_state, []))

    # Avoid visiting the same state repeatedly.
    visited = {frozenset(initial_state)}

    while queue:

        current_state, plan = queue.popleft()

        # Goal test
        if goal_reached(current_state, goal):
            return plan, current_state

        # Explore every possible action
        for action in actions:

            # Logical reasoning:
            # Can this action be executed?
            if action.is_applicable(current_state):

                # Generate successor state
                next_state = action.apply(current_state)

                state_key = frozenset(next_state)

                # Only explore new states
                if state_key not in visited:

                    visited.add(state_key)

                    new_plan = plan + [(action, next_state)]

                    queue.append(
                        (next_state, new_plan)
                    )

    # No solution exists
    return None, None


def print_plan(initial_state, result):
    """
    Print the states reached after every action.
    """

    plan, final_state = result

    if plan is None:
        print("No plan found.")
        return

    print("\nInitial State:")
    print(sorted(initial_state))

    print("\nPlan:")

    for i, (action, state) in enumerate(plan, start=1):

        print(f"\nStep {i}: {action}")
        print("State:", sorted(state))

    print("\nFinal State:")
    print(sorted(final_state))


# --------------------------------------------------
# Warehouse Problem
# --------------------------------------------------

initial_state = {
    "At(Robot,A)",
    "At(Package,A)"
}

goal = {
    "At(Package,C)"
}


actions = [

    # Move A -> B
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

    # Move B -> A
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

    # Move B -> C
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

    # Move C -> B
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

    # Pick up package at A
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

    # Drop package at C
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


if __name__ == "__main__":

    result = bfs_planner(
        initial_state,
        actions,
        goal
    )

    print_plan(
        initial_state,
        result
    )