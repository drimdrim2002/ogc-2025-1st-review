"""해 복원(9장)을 리스트와 for 문만으로 다시 쓴 것. 팀 코드 get_solution 을 Python으로 옮겼다.

- 입력: 모형의 답 x(값이 1인 것만 [p, q, i] 로), z(0보다 큰 것만 [p, q, r, 대수] 로)
- 출력: 항구마다 [경로, 수요 번호] 의 목록
- 실행: python3 restore_demo.py   (솔버가 필요 없다. 같은 폴더의 roro_bruteforce.py 로 채점한다)
"""


def make_bags(P, K, z, trace=False):
    """1부. 주머니 bag[p][q] = 구간 (p, q) 로 실릴 차들의 수요 번호 목록."""
    bag = []
    for p in range(P):
        row = []
        for q in range(P):
            row.append([])
        bag.append(row)
    for k in range(len(K)):                 # 1단계: 원래 수요를 넣는다
        o, d = K[k][0]
        for n in range(K[k][1]):
            bag[o][d].append(k)
    splits = []                             # 2단계: 쪼갤 일의 목록 [p, q, r, 남은 대수]
    for s in z:
        splits.append([s[0], s[1], s[2], s[3]])
    remaining = len(splits)                 # 아직 다 못 쪼갠 일의 수
    while remaining > 0:
        for s in splits:
            p, q, r, n = s
            take = min(n, len(bag[p][r]))   # 이번에 쪼갤 수 있는 대수
            if trace and n > 0:
                print("   z", (p, q, r), ": 주머니", (p, r), "=", bag[p][r], "→", take, "대 쪼갬")
            if take == 0:
                continue                    # 재료가 아직 없으면 다음 바퀴에
            for n2 in range(take):
                k = bag[p][r].pop()         # 주머니 (p, r) 에서 번호 하나를 꺼내
                bag[p][q].append(k)         # 앞 토막 주머니와
                bag[q][r].append(k)         # 뒤 토막 주머니에 넣는다
            s[3] = n - take
            if s[3] == 0:
                remaining -= 1
    return bag


def bfs(N, E, blocked):
    """6장의 너비 우선 탐색. blocked[i] 가 True 인 칸은 지나가지 않는다. (방문 순서, 부모) 를 돌려준다."""
    nbr = []
    for i in range(N):
        nbr.append([])
    for e in E:
        nbr[e[0]].append(e[1])
        nbr[e[1]].append(e[0])
    parent = [None] * N
    parent[0] = -1
    order = []
    layer = [0]
    while len(layer) > 0:
        next_layer = []
        for i in layer:
            order.append(i)
            for j in nbr[i]:
                if not blocked[j] and parent[j] is None:
                    parent[j] = i
                    next_layer.append(j)
        layer = next_layer
    return order, parent


def route_out(parent, i):
    """칸 i 에서 부모를 따라 출입구까지. 하역 경로 [i, ..., 0]."""
    route = []
    while i != 0:
        route.append(i)
        i = parent[i]
    route.append(0)
    return route


def restore(N, E, P, K, x, z, trace=False):
    """2부. 항구마다 경로 목록을 만든다."""
    bag = make_bags(P, K, z)
    solution = []
    for c in range(P):                                  # c = 지금 항구
        blocked = [False] * N                           # ① 머무는 차가 있는 칸 표시
        if 0 < c and c < P - 1:
            for i in range(1, N):
                for p in range(c):
                    for r in range(c + 1, P):
                        if [p, r, i] in x:
                            blocked[i] = True
        order, parent = bfs(N, E, blocked)              # ② 남은 칸으로 BFS
        routes = []
        if c > 0:                                       # ③ 하역: 가까운 칸부터
            for idx in range(1, len(order)):
                i = order[idx]
                for p in range(c):
                    if [p, c, i] in x:
                        routes.append([route_out(parent, i), 0])
        if c < P - 1:                                   # ④ 선적: 먼 칸부터
            for idx in range(len(order) - 1, 0, -1):
                i = order[idx]
                for r in range(c + 1, P):
                    if [c, r, i] in x:
                        k = bag[c][r].pop()
                        route = route_out(parent, i)
                        route.reverse()
                        routes.append([route, k])
        if trace:
            stay = []
            for i in range(1, N):
                if blocked[i]:
                    stay.append(i)
            print("  항구", c, ": 머무는 차가 있는 칸", stay, " BFS로 닿는 칸", order[1:])
            for rt in routes:
                print("     ", rt[0], " 수요", rt[1])
        solution.append(routes)
    return solution


def flatten(solution):
    """3부. C++ 이 Python 에 돌려주는 납작한 배열 네 개."""
    port_route_num, demand_indices, route_lengths, routes = [], [], [], []
    for port_routes in solution:
        port_route_num.append(len(port_routes))
        for rt in port_routes:
            demand_indices.append(rt[1])
            route_lengths.append(len(rt[0]))
            for node in rt[0]:
                routes.append(node)
    return port_route_num, demand_indices, route_lengths, routes


def unflatten(P, port_route_num, demand_indices, route_lengths, routes):
    """3부. myalgorithm.py 가 하는 일: 커서 두 개로 배열을 다시 자른다."""
    solution = []
    route_cursor = 0        # 몇 번째 경로인가
    node_cursor = 0         # routes 배열의 어디까지 읽었는가
    for port in range(P):
        port_routes = []
        for n in range(port_route_num[port]):
            length = route_lengths[route_cursor]
            k = demand_indices[route_cursor]
            route = []
            for j in range(node_cursor, node_cursor + length):
                route.append(routes[j])
            port_routes.append([route, k])
            node_cursor += length
            route_cursor += 1
        solution.append(port_routes)
    return solution


def show(name, N, E, P, K, F, x, z):
    from roro_bruteforce import check, lower_bound
    print("=====", name)
    sol = restore(N, E, P, K, x, z, trace=True)
    as_dict = {}
    for p in range(P):
        as_dict[p] = sol[p]
    LB = lower_bound(N, E, P, K, F)
    total, obj, problems = check(N, E, P, K, F, LB, as_dict)
    print("  채점: 총비용", total, " 대회 LB", LB, " 목적함수", obj, " 문제점", problems)
    return sol


if __name__ == "__main__":
    LINE3 = [[0, 1], [1, 2]]
    K_B = [[[0, 2], 1], [[1, 3], 1]]
    # 미니 문제 B 의 최적해 (가): 항구 1 에서 차 A 를 임시로 내린다
    show("미니 문제 B (가)", 3, LINE3, 4, K_B, 10, [[0, 1, 1], [1, 2, 1], [1, 3, 2]], [[0, 1, 2, 1]])
    # 미니 문제 B 의 최적해 (나): 항구 2 에서 차 B 를 임시로 내린다
    show("미니 문제 B (나)", 3, LINE3, 4, K_B, 10, [[0, 2, 2], [1, 2, 1], [2, 3, 1]], [[1, 2, 3, 1]])

    # 공식 예시의 최적해
    LINE5 = [[0, 1], [1, 2], [2, 3], [3, 4]]
    K_OFF = [[[0, 2], 2], [[1, 4], 1], [[2, 3], 1], [[1, 3], 1], [[3, 4], 1]]
    X_OFF = [[0, 1, 1], [0, 1, 2], [1, 2, 1], [1, 2, 2], [1, 3, 3], [1, 4, 4], [2, 3, 1], [3, 4, 1]]
    Z_OFF = [[0, 1, 2, 2]]
    bag = make_bags(5, K_OFF, Z_OFF)
    print("===== 공식 예시의 주머니 (2단계 뒤)")
    for p in range(5):
        for q in range(p + 1, 5):
            if len(bag[p][q]) > 0:
                print("  ", (p, q), bag[p][q])
    sol = show("공식 예시", 5, LINE5, 5, K_OFF, 10, X_OFF, Z_OFF)

    a, b, c, d = flatten(sol)
    print("  out_port_route_num =", a)
    print("  out_demand_indices =", b)
    print("  out_route_lengths  =", c)
    print("  out_routes         =", d)
    print("  노드 수의 합", sum(c), " 경로 수", len(c), " 다시 자른 것이 원래와 같은가:", unflatten(5, a, b, c, d) == sol)
    upper = 0
    for item in K_OFF:
        upper += 2 * (item[0][1] - item[0][0]) * item[1]
    print("  경로 개수의 상한 max_num_routes =", upper)

    # 두 번 쪼개지는 차: 항구 0→4 인 차 한 대가 항구 2 와 항구 3 에서 임시로 내려진다
    print("===== 두 번 쪼개지는 예 (z 를 일부러 (2,3,4) 먼저 적음)")
    bag = make_bags(5, [[[0, 4], 1]], [[2, 3, 4, 1], [0, 2, 4, 1]], trace=True)
    for p in range(5):
        for q in range(p + 1, 5):
            if len(bag[p][q]) > 0:
                print("  ", (p, q), bag[p][q])
