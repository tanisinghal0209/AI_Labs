"""Run the Search laboratory's BFS/A* and heuristic comparisons."""

from search_agent import WAREHOUSE_MAP, a_star_search, breadth_first_search, print_result


def main() -> None:
    print("Original warehouse: BFS versus A* (Manhattan)")
    print_result("BFS", breadth_first_search(WAREHOUSE_MAP))
    print_result("A* Manhattan", a_star_search(WAREHOUSE_MAP, "manhattan"))

    print("\nA* heuristic investigation on the original warehouse")
    for name in ("zero", "euclidean", "double_manhattan"):
        print_result(f"A* {name}", a_star_search(WAREHOUSE_MAP, name))


if __name__ == "__main__":
    main()
