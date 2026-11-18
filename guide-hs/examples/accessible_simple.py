"""7장 본문: 접근 가능 딱지를 높이가 낮은 칸부터 차례로 붙여 본다.
규칙 (가) 출입구는 접근 가능 (나) 머무는 차가 있는 칸은 불가
     (다) 그 밖의 칸은 아래 이웃 중 접근 가능한 칸이 있어야 한다
이 프로그램은 (다)를 지키는 한에서 딱지를 붙일 수 있는 칸에 전부 붙인다.
실행: python3 accessible_simple.py
"""
from bfs_simple import bfs, heights_and_pred


def accessible(N, E, staying):
    order, dist, parent, nbr = bfs(N, E)
    height, pred = heights_and_pred(N, order, nbr)
    ok = [False] * N
    ok[0] = True                      # (가) 출입구
    for i in order[1:]:               # 높이가 낮은 칸부터 차례로
        if i in staying:              # (나) 머무는 차가 있으면 불가
            continue
        for j in pred[i]:             # (다) 아래 이웃 중 하나라도 접근 가능하면
            if ok[j]:
                ok[i] = True
    result = []
    for i in range(N):
        if ok[i]:
            result.append(i)
    return result


def really_reachable(N, E, staying):
    """비교용: 높이를 무시하고, 머무는 차만 피해서 출입구에서 닿는 칸 (실제로 길이 있는 칸)"""
    nbr = []
    for i in range(N):
        nbr.append([])
    for e in E:
        nbr[e[0]].append(e[1])
        nbr[e[1]].append(e[0])
    seen = [0]
    layer = [0]
    while len(layer) > 0:
        next_layer = []
        for i in layer:
            for j in nbr[i]:
                if j not in seen and j not in staying:
                    seen.append(j)
                    next_layer.append(j)
        layer = next_layer
    return sorted(seen)


if __name__ == "__main__":
    branch = [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [5, 6], [5, 7]]
    grid = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [2, 5], [3, 6], [4, 6], [4, 7], [5, 7], [6, 8], [7, 8]]
    ring6 = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]
    small = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 4], [3, 5], [4, 5]]
    cases = [
        ("가지가 있는 배, 머무는 차 4·5·6", 8, branch, [4, 5, 6]),
        ("가지가 있는 배, 머무는 차 2", 8, branch, [2]),
        ("격자 배, 머무는 차 1·4", 9, grid, [1, 4]),
        ("격자 배, 머무는 차 4", 9, grid, [4]),
        ("격자 배, 머무는 차 3·4·5", 9, grid, [3, 4, 5]),
        ("6칸 고리, 머무는 차 1·5", 6, ring6, [1, 5]),
        ("6칸 고리, 머무는 차 1", 6, ring6, [1]),
        ("6칸 고리, 머무는 차 5", 6, ring6, [5]),
        ("작은 격자 배, 머무는 차 1", 6, small, [1]),
        ("작은 격자 배, 머무는 차 4", 6, small, [4]),
    ]
    for name, N, E, staying in cases:
        print(name)
        print("  모형이 접근 가능으로 볼 수 있는 칸:", accessible(N, E, staying))
        print("  실제로 길이 있는 칸            :", really_reachable(N, E, staying))
