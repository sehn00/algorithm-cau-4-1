from __future__ import annotations

import argparse
import csv
import heapq
import math
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class Item:
    weight: int
    value: int

    @property
    def density(self) -> float:
        return self.value / self.weight


@dataclass(order=True)
class HeapNode:
    priority: float
    serial: int
    level: int
    weight: int
    value: int
    upper_bound: float


@dataclass
class Result:
    instance: str
    method: str
    best_value: int
    elapsed_ms: float
    visited_nodes: int
    pruned_nodes: int
    completed: bool = True
    dual_bound: float | None = None
    gap_percent: float | None = None


def load_instance(path: Path) -> tuple[int, list[Item]]:
    with path.open('r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    n, capacity = map(int, lines[0].split())
    items = [Item(*map(int, line.split())) for line in lines[1:]]
    if len(items) != n:
        raise ValueError(f'{path}: expected {n} items, found {len(items)}')
    return capacity, items


def brute_force(capacity: int, items: list[Item]) -> tuple[int, int, int]:
    """DFS over the subset tree. Overweight branches are cut immediately."""
    n = len(items)
    best = 0
    visited = 0
    pruned = 0

    def dfs(index: int, weight: int, value: int) -> None:
        nonlocal best, visited, pruned
        visited += 1
        if weight > capacity:
            pruned += 1
            return
        if index == n:
            if value > best:
                best = value
            return
        item = items[index]
        dfs(index + 1, weight + item.weight, value + item.value)
        dfs(index + 1, weight, value)

    dfs(0, 0, 0)
    return best, visited, pruned


def dynamic_programming(capacity: int, items: list[Item]) -> tuple[int, int, int]:
    """One-dimensional weight-indexed DP. visited = examined (item, weight) states."""
    dp = [0] * (capacity + 1)
    visited = 0
    for item in items:
        for w in range(capacity, item.weight - 1, -1):
            visited += 1
            candidate = dp[w - item.weight] + item.value
            if candidate > dp[w]:
                dp[w] = candidate
    return dp[capacity], visited, 0


def greedy_lower_bound(capacity: int, items: list[Item]) -> int:
    total_weight = 0
    total_value = 0
    for item in items:
        if total_weight + item.weight <= capacity:
            total_weight += item.weight
            total_value += item.value
    return total_value


def loose_bound(level: int, weight: int, value: int, capacity: int, items: list[Item], suffix_values: list[int]) -> float:
    if weight > capacity:
        return -math.inf
    return float(value + suffix_values[level])


def fractional_bound(level: int, weight: int, value: int, capacity: int, items: list[Item], suffix_values: list[int]) -> float:
    if weight > capacity:
        return -math.inf
    remaining = capacity - weight
    bound = float(value)
    for i in range(level, len(items)):
        item = items[i]
        if item.weight <= remaining:
            remaining -= item.weight
            bound += item.value
        else:
            bound += item.density * remaining
            break
    return bound


def branch_and_bound(
    capacity: int,
    original_items: list[Item],
    bound_kind: str,
    timeout_s: float | None = None,
    checkpoints_s: Iterable[float] = (),
) -> tuple[int, int, int, bool, float, float, list[tuple[float, int, float, float]]]:
    """Best-first B&B. Items are sorted by density for deterministic branching.

    visited: nodes popped from the priority queue and examined.
    pruned: infeasible or bound-dominated generated/popped nodes discarded.
    """
    items = sorted(original_items, key=lambda x: (x.density, x.value, -x.weight), reverse=True)
    n = len(items)
    suffix_values = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix_values[i] = suffix_values[i + 1] + items[i].value

    if bound_kind == 'loose':
        bound_fn: Callable[[int, int, int, int, list[Item], list[int]], float] = loose_bound
    elif bound_kind == 'fractional':
        bound_fn = fractional_bound
    else:
        raise ValueError(f'unknown bound kind: {bound_kind}')

    best = greedy_lower_bound(capacity, items)
    root_ub = bound_fn(0, 0, 0, capacity, items, suffix_values)
    serial = 0
    heap: list[HeapNode] = [HeapNode(-root_ub, serial, 0, 0, 0, root_ub)]
    visited = 0
    pruned = 0
    checkpoints = sorted(checkpoints_s)
    checkpoint_index = 0
    snapshots: list[tuple[float, int, float, float]] = []
    start = time.perf_counter()

    def current_dual_bound() -> float:
        if not heap:
            return float(best)
        return max(float(best), -heap[0].priority)

    def record_due_checkpoints(now: float) -> None:
        nonlocal checkpoint_index
        elapsed = now - start
        while checkpoint_index < len(checkpoints) and elapsed >= checkpoints[checkpoint_index]:
            dual = current_dual_bound()
            gap = (dual - best) / max(best, 1) * 100.0
            snapshots.append((checkpoints[checkpoint_index], best, dual, gap))
            checkpoint_index += 1

    completed = True
    while heap:
        now = time.perf_counter()
        record_due_checkpoints(now)
        if timeout_s is not None and now - start >= timeout_s:
            completed = False
            break

        node = heapq.heappop(heap)
        visited += 1
        if node.upper_bound <= best:
            pruned += 1
            continue
        if node.level == n:
            if node.value > best:
                best = node.value
            continue

        item = items[node.level]
        next_level = node.level + 1

        # Include child
        include_weight = node.weight + item.weight
        include_value = node.value + item.value
        if include_weight <= capacity:
            if include_value > best:
                best = include_value
            ub = bound_fn(next_level, include_weight, include_value, capacity, items, suffix_values)
            if ub > best:
                serial += 1
                heapq.heappush(heap, HeapNode(-ub, serial, next_level, include_weight, include_value, ub))
            else:
                pruned += 1
        else:
            pruned += 1

        # Exclude child
        ub = bound_fn(next_level, node.weight, node.value, capacity, items, suffix_values)
        if ub > best:
            serial += 1
            heapq.heappush(heap, HeapNode(-ub, serial, next_level, node.weight, node.value, ub))
        else:
            pruned += 1

    now = time.perf_counter()
    record_due_checkpoints(now)
    dual = current_dual_bound()
    gap = (dual - best) / max(best, 1) * 100.0
    # If search completed before a checkpoint, the exact optimality gap remains 0 afterwards.
    while checkpoint_index < len(checkpoints):
        snapshots.append((checkpoints[checkpoint_index], best, float(best), 0.0))
        checkpoint_index += 1
    return best, visited, pruned, completed, dual, gap, snapshots


def timed_run(fn: Callable[[], tuple[int, int, int]], repeats: int) -> tuple[int, float, int, int]:
    times: list[float] = []
    outputs: list[tuple[int, int, int]] = []
    for _ in range(repeats):
        start = time.perf_counter()
        outputs.append(fn())
        times.append((time.perf_counter() - start) * 1000.0)
    if len(set(outputs)) != 1:
        raise RuntimeError('non-deterministic outputs detected')
    best, visited, pruned = outputs[0]
    return best, statistics.median(times), visited, pruned


def run_all(data_dir: Path, output_csv: Path, snapshots_csv: Path) -> None:
    required_files = [
        'knapsack_small.txt',
        'knapsack_large_w.txt',
        'knapsack_bnb_easy.txt',
        'knapsack_bnb_hard.txt',
    ]

    if not data_dir.is_dir():
        raise FileNotFoundError(
            f'Data directory not found: {data_dir}\n'
            'Create a data directory next to this Python file and place the four txt files inside it.'
        )

    missing_files = [name for name in required_files if not (data_dir / name).is_file()]
    if missing_files:
        missing_text = '\n'.join(f'  - {name}' for name in missing_files)
        raise FileNotFoundError(
            f'Missing input files in {data_dir}:\n{missing_text}'
        )

    paths = [data_dir / name for name in required_files]
    print(f'Using data directory: {data_dir}')
    results: list[Result] = []
    hard_snapshots: list[tuple[float, int, float, float]] = []

    for path in paths:
        capacity, items = load_instance(path)
        instance = path.stem
        print(f'[{instance}] n={len(items)}, W={capacity}')

        # Median timing prevents one-off OS jitter from dominating tiny instances.
        for method, fn, repeats in [
            ('Brute Force', lambda c=capacity, it=items: brute_force(c, it), 3),
            ('Dynamic Programming', lambda c=capacity, it=items: dynamic_programming(c, it), 5),
        ]:
            best, elapsed, visited, pruned = timed_run(fn, repeats)
            results.append(Result(instance, method, best, elapsed, visited, pruned))
            print(f'  {method:24s} best={best:5d} time={elapsed:10.3f} ms visited={visited:9d} pruned={pruned:9d}')

        for bound_kind, method in [('loose', 'B&B Loose UB'), ('fractional', 'B&B Fractional UB')]:
            def fn(kind=bound_kind, c=capacity, it=items):
                best, visited, pruned, completed, _, _, _ = branch_and_bound(c, it, kind)
                if not completed:
                    raise RuntimeError('unexpected timeout')
                return best, visited, pruned
            repeats = 1 if (instance == 'knapsack_bnb_hard' and bound_kind == 'loose') else 5
            best, elapsed, visited, pruned = timed_run(fn, repeats)
            results.append(Result(instance, method, best, elapsed, visited, pruned))
            print(f'  {method:24s} best={best:5d} time={elapsed:10.3f} ms visited={visited:9d} pruned={pruned:9d}')

        checkpoints = (0.1, 0.5, 1.0) if instance == 'knapsack_bnb_hard' else ()
        start = time.perf_counter()
        best, visited, pruned, completed, dual, gap, snapshots = branch_and_bound(
            capacity, items, 'loose', timeout_s=1.0, checkpoints_s=checkpoints
        )
        elapsed = (time.perf_counter() - start) * 1000.0
        results.append(Result(instance, 'B&B Loose UB (1s limit)', best, elapsed, visited, pruned, completed, dual, gap))
        print(f'  {"B&B Loose UB (1s limit)":24s} best={best:5d} time={elapsed:10.3f} ms visited={visited:9d} pruned={pruned:9d} completed={completed} gap={gap:.3f}%')
        if instance == 'knapsack_bnb_hard':
            hard_snapshots = snapshots

        # Cross-check exact methods.
        exact_values = {r.best_value for r in results if r.instance == instance and r.completed and '(1s limit)' not in r.method}
        if len(exact_values) != 1:
            raise RuntimeError(f'{instance}: exact methods disagree: {exact_values}')

    with output_csv.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['instance', 'method', 'best_value', 'elapsed_ms', 'visited_nodes', 'pruned_nodes', 'completed', 'dual_bound', 'gap_percent'])
        for r in results:
            writer.writerow([
                r.instance, r.method, r.best_value, f'{r.elapsed_ms:.6f}', r.visited_nodes,
                r.pruned_nodes, r.completed,
                '' if r.dual_bound is None else f'{r.dual_bound:.6f}',
                '' if r.gap_percent is None else f'{r.gap_percent:.6f}',
            ])

    with snapshots_csv.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['checkpoint_ms', 'best_value', 'dual_bound', 'gap_percent'])
        for checkpoint, best, dual, gap in hard_snapshots:
            writer.writerow([f'{checkpoint * 1000:.0f}', best, f'{dual:.6f}', f'{gap:.6f}'])

    print(f'\nSaved: {output_csv}')
    print(f'Saved: {snapshots_csv}')


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description='Compare 0-1 knapsack solvers for Practice 05.')
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=script_dir / 'data',
        help='Directory containing the four txt files. Default: ./data next to this Python file.',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=script_dir / 'results.csv',
        help='Result CSV path. Default: ./results.csv next to this Python file.',
    )
    parser.add_argument(
        '--snapshots-output',
        type=Path,
        default=script_dir / 'hard_gap_snapshots.csv',
        help='Gap snapshot CSV path. Default: ./hard_gap_snapshots.csv next to this Python file.',
    )
    args = parser.parse_args()
    run_all(args.data_dir.resolve(), args.output.resolve(), args.snapshots_output.resolve())


if __name__ == '__main__':
    main()
