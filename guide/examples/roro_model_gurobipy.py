"""tryAgain의 정식화(가이드 6장)를 gurobipy로 옮긴 실습용 코드.

- 원본: tryAgain_소스/function.cpp 의 formulate()
- 주의: 이 파일은 Gurobi가 없는 환경에서 작성되어 실행 확인을 하지 못했다.
  예시 문제에서 목적함수 190(= 총비용)이 나와야 한다.
  같은 폴더의 toy_bruteforce.py로 값을 대조할 수 있다.
- 실행: pip install gurobipy  →  python3 roro_model_gurobipy.py
  (pip 설치본의 제한 라이선스는 변수 2000개, 제약 2000개까지)
"""
import gurobipy as gp
from gurobipy import GRB


def bfs_orientation(N, E):
    """5장: 출입구(0)에서 층별 BFS. 높이 pos, 거리 dist, 이웃 목록 nbr를 돌려준다."""
    nbr = [[] for _ in range(N)]
    for u, v in E:
        nbr[u].append(v)
        nbr[v].append(u)
    pos, dist = [None] * N, [None] * N
    dist[0] = 0
    layer, position = [0], 0
    seen = {0}
    while layer:
        nxt = []
        for i in layer:
            pos[i] = position
            position += 1
            for j in nbr[i]:
                if j not in seen:
                    seen.add(j)
                    dist[j] = dist[i] + 1
                    nxt.append(j)
        layer = nxt
    return nbr, pos, dist


def build_model(prob):
    N, E, P, K, F = prob["N"], prob["E"], prob["P"], prob["K"], prob["F"]
    nbr, pos, dist = bfs_orientation(N, E)
    pred = {i: [j for j in nbr[i] if pos[j] < pos[i]] for i in range(1, N)}
    d = {(p, q): 0 for p in range(P) for q in range(p + 1, P)}
    for (o, dest), qty in K:
        d[o, dest] = qty

    m = gp.Model("roro")
    pairs = [(p, q) for p in range(P) for q in range(p + 1, P)]
    nodes = range(1, N)          # 칸 (출입구 제외)
    mid = range(1, P - 1)        # 첫 항구와 마지막 항구를 뺀 항구

    # --- 변수 ---
    x = m.addVars(((p, q, i) for (p, q) in pairs for i in nodes), vtype=GRB.BINARY, name="x")
    y = m.addVars(((p, i) for p in mid for i in range(N)), vtype=GRB.BINARY, name="y")
    z = m.addVars(((p, q, r) for p in range(P) for q in range(p + 1, P) for r in range(q + 1, P)),
                  vtype=GRB.INTEGER, lb=0, name="z")

    # --- 목적함수: 구간 하나 = 선적 경로 + 하역 경로 ---
    m.setObjective(gp.quicksum(2 * (F + dist[i]) * x[p, q, i] for (p, q) in pairs for i in nodes),
                   GRB.MINIMIZE)

    # --- 제약 ① 수요 ---
    for (p, q) in pairs:
        m.addConstr(
            gp.quicksum(x[p, q, i] for i in nodes)
            == d[p, q]
            - gp.quicksum(z[p, r, q] for r in range(p + 1, q))      # (p,q)가 r에서 쪼개져 없어짐
            + gp.quicksum(z[p, q, r] for r in range(q + 1, P))      # (p,r)이 q에서 쪼개진 앞 토막
            + gp.quicksum(z[r, p, q] for r in range(p)),            # (r,q)가 p에서 쪼개진 뒤 토막
            name=f"demand_{p}_{q}")

    for q in mid:
        m.addConstr(y[q, 0] == 1, name=f"gate_{q}")                                   # ⑥
        for i in nodes:
            staying = gp.quicksum(x[p, r, i] for p in range(q) for r in range(q + 1, P))
            m.addConstr(staying <= 1 - y[q, i], name=f"occupied_{q}_{i}")              # ②
            m.addConstr(gp.quicksum(x[p, q, i] for p in range(q)) <= y[q, i],
                        name=f"unload_{q}_{i}")                                       # ③
            m.addConstr(gp.quicksum(x[q, r, i] for r in range(q + 1, P)) <= y[q, i],
                        name=f"load_{q}_{i}")                                         # ④
            m.addConstr(y[q, i] <= gp.quicksum(y[q, j] for j in pred[i]),
                        name=f"propagate_{q}_{i}")                                    # ⑤
    return m, x, y, z


if __name__ == "__main__":
    example = {
        "N": 5, "E": [[0, 1], [1, 2], [2, 3], [3, 4]], "P": 5,
        "K": [[[0, 2], 2], [[1, 4], 1], [[2, 3], 1], [[1, 3], 1], [[3, 4], 1]],
        "F": 10, "LB": 137,
    }
    model, x, y, z = build_model(example)

    # tryAgain이 건 설정 (8장). 주석을 풀어 가며 로그가 어떻게 달라지는지 비교해 볼 수 있다.
    # model.Params.MIPGapAbs = 2 - 1e-3
    # model.Params.Heuristics = 0.15
    # model.Params.Method = 2
    # model.Params.NoRelHeurTime = 5

    model.optimize()
    print("총비용 =", model.ObjVal, " 목적함수(총비용 - LB) =", model.ObjVal - example["LB"])
    print("x = 1 (실은 항구, 내린 항구, 칸):", sorted(k for k, v in x.items() if v.X > 0.5))
    print("z > 0 (p, 쪼갠 항구 q, r):", {k: round(v.X) for k, v in z.items() if v.X > 0.5})
