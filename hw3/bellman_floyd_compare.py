import time

INF = float('inf')


# 데이터 파싱 함수
def read_graph_data(filename):
    with open(filename, 'r') as f:
        tokens = list(map(int, f.read().split()))

    V, E = tokens[0], tokens[1]

    edges = []
    idx = 2
    for _ in range(E):
        u = tokens[idx]
        v = tokens[idx + 1]
        w = tokens[idx + 2]
        edges.append((u, v, w))
        idx += 3

    return V, E, edges


# ==========================================
# 1. 벨만-포드 알고리즘: 단일 출발점 최단 경로
# ==========================================
def bellman_ford(V, edges, start, end):
    dist = [INF] * V
    pred = [-1] * V

    dist[start] = 0

    start_time = time.perf_counter()

    for _ in range(V - 1):
        updated = False

        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True

        if not updated:
            break

    end_time = time.perf_counter()

    # 역추적
    path = []
    if dist[end] != INF:
        curr = end

        while curr != -1:
            path.append(curr)
            curr = pred[curr]

        path.reverse()

    return dist[end], path, end_time - start_time


# ==========================================
# 2. 플로이드-워셜 알고리즘: 모든 정점 쌍 최단 경로
# ==========================================
def floyd_warshall(V, edges, start, end):
    dist = [[INF] * V for _ in range(V)]
    nxt = [[-1] * V for _ in range(V)]

    for i in range(V):
        dist[i][i] = 0
        nxt[i][i] = i

    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
            nxt[u][v] = v

    start_time = time.perf_counter()

    for k in range(V):
        for i in range(V):
            if dist[i][k] == INF:
                continue

            for j in range(V):
                if dist[k][j] == INF:
                    continue

                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    end_time = time.perf_counter()

    # 경로 복원
    path = []
    if dist[start][end] != INF:
        curr = start
        path.append(curr)

        while curr != end:
            curr = nxt[curr][end]

            if curr == -1:
                path = []
                break

            path.append(curr)

    return dist[start][end], path, end_time - start_time


# ==========================================
# 메인 실행부
# ==========================================
if __name__ == "__main__":
    filename = "sparse_graph_500-1.txt"
    start_vertex = 0
    end_vertex = 499

    try:
        V, E, edges = read_graph_data(filename)
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다.")
        exit()

    print(f"\n[{filename} 분석 결과]")
    print(f"정점 수: {V}, 간선 수: {E}")
    print(f"출발 정점: {start_vertex}, 도착 정점: {end_vertex}")
    print()

    # 1. 벨만-포드
    bf_dist, bf_path, bf_time = bellman_ford(V, edges, start_vertex, end_vertex)

    print("1. 벨만-포드 알고리즘")
    print(f"   최단 거리: {bf_dist}")
    print(f"   경로: {' -> '.join(map(str, bf_path))}")
    print(f"   수행 시간: {bf_time:.6f} 초")
    print()

    # 2. 플로이드-워셜
    fw_dist, fw_path, fw_time = floyd_warshall(V, edges, start_vertex, end_vertex)

    print("2. 플로이드-워셜 알고리즘")
    print(f"   최단 거리: {fw_dist}")
    print(f"   경로: {' -> '.join(map(str, fw_path))}")
    print(f"   수행 시간: {fw_time:.6f} 초")
    print()

    # 결과 비교
    print("3. 결과 비교")

    if bf_dist == fw_dist:
        print("   최단 거리 일치 여부: 일치")
    else:
        print("   최단 거리 일치 여부: 불일치")

    if bf_path == fw_path:
        print("   경로 일치 여부: 일치")
    else:
        print("   경로 일치 여부: 불일치")

    if bf_dist == fw_dist and bf_path == fw_path:
        print("\n=> 검증 완료: 두 알고리즘의 최단 거리와 경로가 동일합니다.\n")
    else:
        print("\n=> 주의: 최단 거리는 같아도 경로는 다를 수 있습니다.\n")
        print("   최단 경로가 여러 개 존재하면 두 알고리즘이 서로 다른 최단 경로를 출력할 수 있습니다.\n")