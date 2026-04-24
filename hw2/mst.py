import time
import heapq
import numpy as np

# 데이터 파싱 함수
def read_graph_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        V, E = map(int, lines[0].split())
        edges = []
        for line in lines[1:]:
            u, v, w = map(int, line.split())
            edges.append((u, v, w))
    return V, E, edges

# ==========================================
# 1. 프림 알고리즘: 인접 행렬 + 배열 (Numpy 최적화)
# ==========================================
def prim_matrix_numpy(V, edges):
    # 인접 행렬 생성 및 초기화 (무한대)
    adj_matrix = np.full((V, V), np.inf)
    for u, v, w in edges:
        adj_matrix[u][v] = w
        adj_matrix[v][u] = w # 무방향 그래프

    visited = np.zeros(V, dtype=bool)
    min_weight = np.full(V, np.inf)
    min_weight[0] = 0 # 시작 정점(0번) 가중치는 0
    
    mst_weight_sum = 0
    
    start_time = time.perf_counter()
    
    for _ in range(V):
        # 1. np.where와 np.argmin으로 방문 안 한 정점 중 최소 가중치 정점 찾기
        unvisited_weights = np.where(visited, np.inf, min_weight)
        u = int(np.argmin(unvisited_weights))
        
        # 방문 처리 및 가중치 합산
        visited[u] = True
        mst_weight_sum += min_weight[u]
        
        # 2. np.minimum으로 반복문 없이 인접 정점의 최소 가중치 배열 일괄 갱신
        min_weight = np.minimum(min_weight, adj_matrix[u])
        
    end_time = time.perf_counter()
    return int(mst_weight_sum), end_time - start_time

# ==========================================
# 2. 프림 알고리즘: 인접 리스트 + 우선순위 큐 (Min-heap)
# ==========================================
def prim_list_heap(V, edges):
    # 인접 리스트 구성
    adj_list = {i: [] for i in range(V)}
    for u, v, w in edges:
        adj_list[u].append((w, v))
        adj_list[v].append((w, u))
        
    visited = [False] * V
    mst_weight_sum = 0
    
    # (가중치, 정점) 형태의 힙
    min_heap = [(0, 0)] 
    
    start_time = time.perf_counter()
    
    while min_heap:
        weight, u = heapq.heappop(min_heap)
        
        if visited[u]:
            continue
            
        visited[u] = True
        mst_weight_sum += weight
        
        for next_weight, v in adj_list[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (next_weight, v))
                
    end_time = time.perf_counter()
    return mst_weight_sum, end_time - start_time

# ==========================================
# 3. 크루스칼 알고리즘: 간선 리스트 + Union-Find
# ==========================================
# Union-Find 자료구조 (경로 압축 적용)
def find(parent, i):
    if parent[i] == i:
        return i
    parent[i] = find(parent, parent[i]) # 경로 압축
    return parent[i]

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)
    
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1

def kruskal_uf(V, edges):
    parent = [i for i in range(V)]
    rank = [0] * V
    mst_weight_sum = 0
    edges_count = 0
    
    start_time = time.perf_counter()
    
    # 간선을 가중치 기준으로 오름차순 정렬
    sorted_edges = sorted(edges, key=lambda item: item[2])
    
    for u, v, w in sorted_edges:
        x = find(parent, u)
        y = find(parent, v)
        
        # 사이클이 생기지 않는다면 간선 추가
        if x != y:
            mst_weight_sum += w
            union(parent, rank, x, y)
            edges_count += 1
            if edges_count == V - 1: # MST 완성 조건
                break
                
    end_time = time.perf_counter()
    return mst_weight_sum, end_time - start_time

# ==========================================
# 메인 실행부
# ==========================================
def run_and_evaluate(filename, graph_type):
    print(f"\n[{graph_type} ({filename}) 분석 결과]")
    try:
        V, E, edges = read_graph_data(filename)
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일이 같은 폴더에 없습니다. 파일을 준비해주세요.")
        return

    # 1. 프림 (행렬+배열)
    w1, t1 = prim_matrix_numpy(V, edges)
    print(f"1. 프림 (행렬+배열)   | 가중치: {w1} | 소요 시간: {t1:.6f} 초")

    # 2. 프림 (리스트+힙)
    w2, t2 = prim_list_heap(V, edges)
    print(f"2. 프림 (리스트+힙)   | 가중치: {w2} | 소요 시간: {t2:.6f} 초")

    # 3. 크루스칼 (간선리스트+UF)
    w3, t3 = kruskal_uf(V, edges)
    print(f"3. 크루스칼 (간선+UF) | 가중치: {w3} | 소요 시간: {t3:.6f} 초")
    
    if w1 == w2 == w3:
        print("=> 검증 완료: 세 알고리즘의 MST 가중치가 동일합니다.")
    else:
        print("=> 경고: 가중치 결과가 다릅니다. 데이터를 확인하세요.")

if __name__ == "__main__":
    # 파일명은 실제 제공된 파일명과 동일하게 맞춰주세요.
    run_and_evaluate("sparse_graph.txt", "희소 그래프")
    run_and_evaluate("dense_graph.txt", "밀집 그래프")