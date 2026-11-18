"""6장 본문의 너비 우선 탐색 코드. 기초 문법(리스트, for, while, if)만 쓴다.
실행: python3 bfs_simple.py
"""


def bfs(N, E):
    nbr = []                          # nbr[i] = 노드 i의 이웃 목록
    for i in range(N):
        nbr.append([])
    for e in E:                       # 간선 [u, v] 하나마다
        nbr[e[0]].append(e[1])        # u의 이웃에 v를,
        nbr[e[1]].append(e[0])        # v의 이웃에 u를 적는다
    dist = [-1] * N                   # 거리. -1은 "아직 발견 못 함"
    parent = [-1] * N                 # 나를 처음 발견해 준 노드
    order = []                        # 방문한 순서
    dist[0] = 0
    layer = [0]                       # 지금 층: 출입구 하나로 시작
    while len(layer) > 0:
        next_layer = []               # 다음 층
        for i in layer:
            order.append(i)           # i를 방문한다
            for j in nbr[i]:
                if dist[j] == -1:     # 처음 보는 이웃이면
                    dist[j] = dist[i] + 1
                    parent[j] = i
                    next_layer.append(j)
        layer = next_layer
    return order, dist, parent, nbr


def heights_and_pred(N, order, nbr):
    height = [0] * N
    for k in range(len(order)):       # k번째로 방문한 노드의 높이는 k
        height[order[k]] = k
    pred = []                         # pred[i] = 노드 i의 아래 이웃 목록
    for i in range(N):
        below = []
        for j in nbr[i]:
            if height[j] < height[i]:
                below.append(j)
        pred.append(below)
    return height, pred


def show(name, N, E):
    order, dist, parent, nbr = bfs(N, E)
    height, pred = heights_and_pred(N, order, nbr)
    print("==", name)
    print("방문 순서:", order)
    print("거리:", dist)
    print("부모:", parent)
    print("높이:", height)
    for i in range(1, N):
        print("  pred(%d) = %s" % (i, pred[i]))
    same = 0
    for i in range(N):
        if height[i] == i:
            same += 1
    print("높이와 번호가 같은 노드:", same, "/", N)


if __name__ == "__main__":
    small = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [3, 5], [4, 5]]
    show("작은 격자 배", 6, small)
    show("작은 격자 배 (간선 [0,2]를 먼저 적음)", 6, [[0, 2], [0, 1], [1, 3], [1, 4], [2, 4], [3, 5], [4, 5]])
    show("가지가 있는 배", 8, [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [5, 6], [5, 7]])
    show("격자 배 (3x3)", 9, [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [2, 5], [3, 6], [4, 6], [4, 7], [5, 7], [6, 8], [7, 8]])
    show("6칸 고리", 6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]])
    show("5칸 고리", 5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]])
    show("일렬 배 (공식 예시)", 5, [[0, 1], [1, 2], [2, 3], [3, 4]])
