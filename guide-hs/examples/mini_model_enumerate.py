"""미니 문제 B의 모형(8장)을 '변수 값의 모든 조합을 다 넣어 보기'로 푼다.

솔버가 하는 일을 가장 무식한 방법으로 흉내 낸 것이다.
변수에 0과 1을 넣는 모든 경우를 만들고, 제약식 ①~⑥을 전부 지키는 것만 남긴 뒤,
그중 목적함수 값이 가장 작은 것을 고른다.
실행: python3 mini_model_enumerate.py
"""
from itertools import product

# ----- 문제: 일렬 배(출입구 0, 칸 1, 칸 2), 항구 0~3, 고정비 10 -----
P, F = 4, 10
cells = [1, 2]                      # 칸
dist = {1: 1, 2: 2}                 # 출입구에서 칸까지의 거리
pred = {1: [0], 2: [1]}             # 아래 이웃 (7장)
demand = {(0, 2): 1, (1, 3): 1}     # 차 A: 항구 0→2, 차 B: 항구 1→3

pairs = [(p, q) for p in range(P) for q in range(p + 1, P)]            # 항구 쌍 6개
mid = [1, 2]                                                           # 중간 항구
xkeys = [(p, q, i) for (p, q) in pairs for i in cells]                 # x 12개
ykeys = [(p, i) for p in mid for i in cells]                           # y 4개 (y_p0 은 1로 고정)
zkeys = [(p, q, r) for p in range(P) for q in range(p + 1, P) for r in range(q + 1, P)]  # z 4개


def demand_ok(x, z):
    """제약 ①: 항구 쌍 (p, q)마다 구간의 개수가 맞는가"""
    for (p, q) in pairs:
        left = sum(x[p, q, i] for i in cells)
        right = (demand.get((p, q), 0)
                 - sum(z[p, r, q] for r in range(p + 1, q))      # (p,q)가 r에서 쪼개져 사라진 수
                 + sum(z[p, q, r] for r in range(q + 1, P))      # (p,r)이 q에서 쪼개진 앞 토막
                 + sum(z[r, p, q] for r in range(p)))            # (r,q)가 p에서 쪼개진 뒤 토막
        if left != right:
            return False
    return True


def access_ok(x, y):
    """제약 ②~⑥: 중간 항구마다, 칸마다"""
    for q in mid:
        yq = {0: 1}                                              # ⑥ 출입구는 항상 접근 가능
        for i in cells:
            yq[i] = y[q, i]
        for i in cells:
            staying = sum(x[p, r, i] for p in range(q) for r in range(q + 1, P))
            unload = sum(x[p, q, i] for p in range(q))
            load = sum(x[q, r, i] for r in range(q + 1, P))
            if staying > 1 - yq[i]: return False                 # ② 머무는 차가 있으면 접근 불가
            if unload > yq[i]: return False                      # ③ 내리려면 접근 가능해야
            if load > yq[i]: return False                        # ④ 실으려면 접근 가능해야
            if yq[i] > sum(yq[j] for j in pred[i]): return False  # ⑤ 아래 이웃이 받쳐 줘야
    return True


def cost(x):
    return sum(2 * (F + dist[i]) * x[p, q, i] for (p, q, i) in xkeys)


tried = feasible = 0
best_cost, best = None, []
for xv in product((0, 1), repeat=len(xkeys)):                    # x: 2^12 = 4096가지
    x = dict(zip(xkeys, xv))
    for zv in product((0, 1, 2), repeat=len(zkeys)):             # z: 0, 1, 2 → 3^4 = 81가지
        z = dict(zip(zkeys, zv))
        tried += 16                                              # y 16가지를 함께 센 것
        if not demand_ok(x, z):
            continue
        for yv in product((0, 1), repeat=len(ykeys)):            # y: 2^4 = 16가지
            y = dict(zip(ykeys, yv))
            if not access_ok(x, y):
                continue
            feasible += 1
            c = cost(x)
            if best_cost is None or c < best_cost:
                best_cost, best = c, []
            if c == best_cost:
                best.append((x, y, z))

print("넣어 본 조합:", tried)
print("제약을 모두 지킨 조합(가능해):", feasible)
print("가장 작은 목적함수 값:", best_cost)
seen = set()
for x, y, z in best:
    key = (tuple(k for k in xkeys if x[k]), tuple((k, z[k]) for k in zkeys if z[k]))
    if key in seen:
        continue
    seen.add(key)
    print("  x = 1:", [k for k in xkeys if x[k]], " z > 0:", {k: z[k] for k in zkeys if z[k]},
          " y = 1:", [k for k in ykeys if y[k]])
print("x, z 가 서로 다른 최적해의 수:", len(seen), " (y 까지 구별하면", len(best), "개)")
