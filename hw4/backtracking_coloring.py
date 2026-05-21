from pathlib import Path
from time import perf_counter
import statistics


def read_graph(path):
    lines = Path(path).read_text(encoding='utf-8').strip().splitlines()
    n, e, m = map(int, lines[0].split())

    edges = [tuple(map(int, line.split())) for line in lines[1:] if line.strip()]

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    return n, e, m, edges, adj


def is_valid_full(colors, edges):
    for u, v in edges:
        if colors[u] == colors[v]:
            return False
    return True


def brute_force(path):
    """
    완전 탐색:
    모든 정점에 색을 배정한 뒤, 리프 노드에서 전체 간선을 검사한다.
    """
    n, e, m, edges, adj = read_graph(path)

    colors = [-1] * n
    visited = 0
    pruned = 0
    solution = None

    start = perf_counter()

    def dfs(k):
        nonlocal visited, solution

        visited += 1

        if k == n:
            if is_valid_full(colors, edges):
                solution = colors.copy()
                return True
            return False

        for c in range(m):
            colors[k] = c

            if dfs(k + 1):
                return True

        colors[k] = -1
        return False

    possible = dfs(0)
    elapsed_ms = (perf_counter() - start) * 1000

    return possible, elapsed_ms, visited, pruned, list(range(n)), solution


def backtracking(path, improved=False):
    """
    백트래킹:
    색을 배정하는 도중 이미 색칠된 인접 정점과 충돌하면 가지치기한다.

    improved=False: 정점 번호 순서대로 탐색
    improved=True : 차수가 높은 정점부터 탐색
    """
    n, e, m, edges, adj = read_graph(path)

    if improved:
        order = sorted(range(n), key=lambda v: (-len(adj[v]), v))
    else:
        order = list(range(n))

    colors = [-1] * n
    visited = 0
    pruned = 0
    solution = None

    def safe(v, c):
        for u in adj[v]:
            if colors[u] == c:
                return False
        return True

    start = perf_counter()

    def dfs(level):
        nonlocal visited, pruned, solution

        visited += 1

        if level == n:
            solution = colors.copy()
            return True

        v = order[level]

        for c in range(m):
            if safe(v, c):
                colors[v] = c

                if dfs(level + 1):
                    return True

                colors[v] = -1
            else:
                pruned += 1

        return False

    possible = dfs(0)
    elapsed_ms = (perf_counter() - start) * 1000

    return possible, elapsed_ms, visited, pruned, order, solution


def run_once(path, algorithm):
    if algorithm == 'brute':
        return brute_force(path)

    if algorithm == 'basic':
        return backtracking(path, improved=False)

    if algorithm == 'improved':
        return backtracking(path, improved=True)

    raise ValueError('unknown algorithm')


def main():
    files = [
        'sparse_coloring.txt',
        'dense_coloring.txt',
        'hard_coloring.txt'
    ]

    algorithms = [
        ('brute', '완전 탐색'),
        ('basic', '기본 백트래킹'),
        ('improved', '개선 백트래킹')
    ]

    print('파일,알고리즘,가능여부,평균시간(ms),방문노드수,가지치기횟수,정점순서,색배정')

    for file_name in files:
        path = Path(file_name)

        for algorithm, label in algorithms:
            runs = [run_once(path, algorithm) for _ in range(5)]
            times = [r[1] for r in runs]

            possible, _, visited, pruned, order, solution = runs[0]

            print(
                f'{file_name},'
                f'{label},'
                f'{"가능" if possible else "불가능"},'
                f'{statistics.mean(times):.6f},'
                f'{visited},'
                f'{pruned},'
                f'"{order}",'
                f'"{solution}"'
            )


if __name__ == '__main__':
    main()