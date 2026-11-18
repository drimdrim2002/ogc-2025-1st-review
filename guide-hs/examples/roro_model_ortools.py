"""tryAgain의 모형(8장)을 무료 솔버로 푼다. Google OR-Tools 사용.

- 설치: pip install ortools      (라이선스가 필요 없다)
- 실행: python3 roro_model_ortools.py
- 원본: 팀 코드 function.cpp 의 formulate(). 변수와 제약식의 번호 ①~⑥은 8장과 같다.
"""
from ortools.linear_solver import pywraplp


def bfs_height(N, E):
    """6장: 출입구(0)에서 너비 우선 탐색. 높이와 거리, 이웃 목록을 돌려준다."""
    nbr = [[] for _ in range(N)]
    for u, v in E:
        nbr[u].append(v)
        nbr[v].append(u)
    height, dist = [None] * N, [None] * N
    dist[0] = 0
    layer, count = [0], 0
    while layer:
        next_layer = []
        for i in layer:
            height[i] = count
            count += 1
            for j in nbr[i]:
                if dist[j] is None:
                    dist[j] = dist[i] + 1
                    next_layer.append(j)
        layer = next_layer
    return nbr, height, dist


def solve(prob, relax=False):
    """relax=True 이면 '0 또는 1'이라는 조건을 '0 이상 1 이하'로 풀어 준 LP 완화를 푼다 (5장)."""
    N, E, P, K, F = prob["N"], prob["E"], prob["P"], prob["K"], prob["F"]
    nbr, height, dist = bfs_height(N, E)

    pred = {}                                   # pred[i] = 칸 i의 아래 이웃 목록
    for i in range(1, N):
        pred[i] = []
        for j in nbr[i]:
            if height[j] < height[i]:
                pred[i].append(j)

    pairs = []                                  # 항구 쌍 (p, q), p < q
    for p in range(P):
        for q in range(p + 1, P):
            pairs.append((p, q))
    cells = range(1, N)                         # 칸 (출입구 제외)
    mid = range(1, P - 1)                       # 중간 항구

    d = {}                                      # d[p, q] = 항구 p에서 실어 q에서 내릴 차의 수
    for (p, q) in pairs:
        d[p, q] = 0
    for (o, dest), qty in K:
        d[o, dest] = qty

    s = pywraplp.Solver.CreateSolver("GLOP" if relax else "SCIP")
    INF = s.infinity()

    def var(lo, hi, name):          # 정수 변수(완화할 때는 실수 변수) 하나 만들기
        if relax:
            return s.NumVar(lo, hi, name)
        return s.IntVar(lo, hi, name)

    # --- 결정변수 ---
    x, y, z = {}, {}, {}
    for (p, q) in pairs:
        for i in cells:
            x[p, q, i] = var(0, 1, f"x_{p}_{q}_{i}")
    for p in mid:
        for i in range(N):
            y[p, i] = var(0, 1, f"y_{p}_{i}")
    for p in range(P):
        for q in range(p + 1, P):
            for r in range(q + 1, P):
                z[p, q, r] = var(0, INF, f"z_{p}_{q}_{r}")

    # --- 목적함수: 구간 하나 = 선적 경로 + 하역 경로 ---
    cost = 0
    for (p, q) in pairs:
        for i in cells:
            cost = cost + 2 * (F + dist[i]) * x[p, q, i]
    s.Minimize(cost)

    # --- 제약 ① 수요: 항구 쌍마다 구간의 개수 맞추기 ---
    for (p, q) in pairs:
        left = 0
        for i in cells:
            left = left + x[p, q, i]
        right = d[p, q]
        for r in range(p + 1, q):
            right = right - z[p, r, q]          # (p,q)가 r에서 쪼개져 사라진 수
        for r in range(q + 1, P):
            right = right + z[p, q, r]          # (p,r)이 q에서 쪼개진 앞 토막
        for r in range(p):
            right = right + z[r, p, q]          # (r,q)가 p에서 쪼개진 뒤 토막
        s.Add(left == right)

    for q in mid:
        s.Add(y[q, 0] == 1)                     # 제약 ⑥ 출입구는 접근 가능
        for i in cells:
            staying = 0                         # 항구 q에서 칸 i에 머무는 구간
            for p in range(q):
                for r in range(q + 1, P):
                    staying = staying + x[p, r, i]
            s.Add(staying <= 1 - y[q, i])       # 제약 ② 머무는 차가 있으면 접근 불가

            unload = 0                          # 항구 q에서 칸 i로부터 내리는 구간
            for p in range(q):
                unload = unload + x[p, q, i]
            s.Add(unload <= y[q, i])            # 제약 ③ 내리려면 접근 가능

            load = 0                            # 항구 q에서 칸 i에 싣는 구간
            for r in range(q + 1, P):
                load = load + x[q, r, i]
            s.Add(load <= y[q, i])              # 제약 ④ 실으려면 접근 가능

            below = 0                           # 아래 이웃들의 y
            for j in pred[i]:
                below = below + y[q, j]
            s.Add(y[q, i] <= below)             # 제약 ⑤ 아래 이웃이 받쳐 줘야

    status = s.Solve()
    assert status == pywraplp.Solver.OPTIMAL
    xs, zs = {}, {}
    for k in x:
        if x[k].solution_value() > 1e-6:
            xs[k] = x[k].solution_value()
    for k in z:
        if z[k].solution_value() > 1e-6:
            zs[k] = z[k].solution_value()
    return s.Objective().Value(), xs, zs, s.NumVariables(), s.NumConstraints()


if __name__ == "__main__":
    mini_b = {"N": 3, "E": [[0, 1], [1, 2]], "P": 4, "K": [[[0, 2], 1], [[1, 3], 1]], "F": 10}
    official = {"N": 5, "E": [[0, 1], [1, 2], [2, 3], [3, 4]], "P": 5,
                "K": [[[0, 2], 2], [[1, 4], 1], [[2, 3], 1], [[1, 3], 1], [[3, 4], 1]], "F": 10, "LB": 137}
    branch = {"N": 8, "E": [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [5, 6], [5, 7]], "P": 4,
              "K": [[[0, 3], 2], [[0, 2], 1], [[1, 3], 1], [[1, 2], 2], [[2, 3], 2]], "F": 10}

    for name, prob in [("미니 문제 B", mini_b), ("공식 예시", official), ("가지가 있는 배", branch)]:
        cost, xs, zs, nvar, ncon = solve(prob)
        print(f"== {name}: 변수 {nvar}개, 제약 {ncon}개, 총비용 = {cost:.0f}")
        print("   x = 1 (실은 항구, 내린 항구, 칸):", sorted(xs))
        print("   z > 0 (실은 항구, 쪼갠 항구, 내릴 항구):", {k: round(v) for k, v in zs.items()})
        lp, lx, lz, _, _ = solve(prob, relax=True)
        frac = sorted(set(round(v, 4) for v in list(lx.values()) + list(lz.values()) if abs(v - round(v)) > 1e-6))
        print(f"   LP 완화의 값 = {lp:.2f}  (0도 1도 아닌 값들: {frac})")
