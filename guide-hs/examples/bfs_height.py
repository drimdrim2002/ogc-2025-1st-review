"""너비 우선 탐색(BFS)으로 노드마다 높이·거리·아래 이웃을 구한다 (6장).

팀 코드 function.cpp 의 getBFSOrientation 을 Python으로 옮긴 것이다.
실행: python3 bfs_height.py
"""


def bfs_height(N, E):
    """N: 노드 수(0이 출입구), E: 간선 목록. (높이, 거리, 방문 순서, 아래 이웃)을 돌려준다."""
    nbr = [[] for _ in range(N)]            # nbr[i] = 노드 i의 이웃 목록
    for u, v in E:
        nbr[u].append(v)
        nbr[v].append(u)

    height = [None] * N                     # 높이 = 방문 순번
    dist = [None] * N                       # 출입구에서의 거리
    order = []                              # 방문한 순서대로 노드 번호
    dist[0] = 0
    layer = [0]                             # 지금 층: 출입구 하나로 시작
    while layer:
        next_layer = []                     # 다음 층
        for i in layer:
            height[i] = len(order)          # 지금까지 방문한 노드 수 = 이번 노드의 순번
            order.append(i)
            for j in nbr[i]:
                if dist[j] is None:         # 처음 발견한 이웃이면
                    dist[j] = dist[i] + 1
                    next_layer.append(j)
        layer = next_layer

    # 아래 이웃: 이웃 가운데 높이가 더 낮은 노드
    pred = {i: [j for j in nbr[i] if height[j] < height[i]] for i in range(1, N)}
    return height, dist, order, pred


if __name__ == "__main__":
    # 2×3 격자 모양의 작은 배 (6장 그림)
    E = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [3, 5], [4, 5]]
    height, dist, order, pred = bfs_height(6, E)
    print("방문 순서:", order)
    print("높이    :", height)
    print("거리    :", dist)
    print("아래 이웃:", pred)

    # 같은 배인데 간선을 적은 순서만 바꾸면? ([0,2]를 [0,1]보다 먼저 적음)
    E2 = [[0, 2], [0, 1], [1, 3], [1, 4], [2, 4], [3, 5], [4, 5]]
    height2, dist2, order2, pred2 = bfs_height(6, E2)
    print("간선 순서를 바꾸면 방문 순서:", order2, " 높이:", height2, " 거리:", dist2)

    # 3×3 격자 (7장 그림). 노드 번호를 높이와 같게 붙여 두었다
    E3 = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [2, 5], [3, 6], [4, 6], [4, 7], [5, 7], [6, 8], [7, 8]]
    height3, dist3, order3, pred3 = bfs_height(9, E3)
    print("3×3 격자 높이:", height3)
    print("3×3 격자 거리:", dist3)
    print("3×3 격자 아래 이웃:", pred3)

    # 고리 모양 배 0-1-2-3-4-5-0 (7장 「섬」 그림): 번호와 높이가 다르다
    E4 = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]
    height4, dist4, order4, pred4 = bfs_height(6, E4)
    print("고리(6) 방문 순서:", order4, " 높이:", height4, " 아래 이웃:", pred4)

    # 홀수 고리 0-1-2-3-4-0 (8장): 거리가 같은 이웃 2와 3
    E5 = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]
    height5, dist5, order5, pred5 = bfs_height(5, E5)
    print("고리(5) 방문 순서:", order5, " 높이:", height5, " 거리:", dist5, " 아래 이웃:", pred5)
