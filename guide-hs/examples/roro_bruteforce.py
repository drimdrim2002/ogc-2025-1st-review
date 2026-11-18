"""tryAgain 모형을 아주 작은 문제에서 '모든 경우를 다 해 보기'로 푸는 검증용 프로그램.

- 솔버 없이 Python만으로 돈다. 팀 코드를 실행한 것이 아니라 같은 모형을 다시 쓴 것이다.
- solve()       : 모형의 최적해 찾기 (8장)
- reconstruct() : 해를 경로 목록으로 바꾸기 = 팀의 get_solution (9장)
- check()       : 대회 채점 규칙으로 검사 (2장)
- 실행: python3 roro_bruteforce.py   (칸 10개, 차 10대 정도까지만 금방 끝난다)
"""
import itertools, sys, json
from collections import Counter

def bfs_orientation(N, E, accessible=None):
    nbr = [[] for _ in range(N)]
    for u, v in E:
        nbr[u].append(v); nbr[v].append(u)
    if accessible is None: accessible = [True]*N
    INF = float('inf')
    pred = [INF]*N; pos = [INF]*N; dist = [INF]*N
    order = []
    search = [0]; dist[0] = 0; pred[0] = -1; p = 0
    while search:
        nxt = []
        for i in search:
            order.append(i); pos[i] = p; p += 1
            for j in nbr[i]:
                if accessible[j] and pred[j] == INF:
                    pred[j] = i; dist[j] = dist[i]+1; nxt.append(j)
        search = nxt
    return nbr, pred, pos, dist, order

def compositions(o, d):
    """[o,d) 구간을 연속한 구간(leg)들로 쪼개는 모든 방법"""
    res = []
    mids = list(range(o+1, d))
    for r in range(len(mids)+1):
        for cut in itertools.combinations(mids, r):
            pts = [o, *cut, d]
            res.append(tuple(zip(pts[:-1], pts[1:])))
    return res

def solve(N, E, P, K, F, verbose=True):
    nbr, pred0, pos, dist, order = bfs_orientation(N, E)
    predset = {i: [j for j in nbr[i] if pos[j] < pos[i]] for i in range(1, N)}
    cars = []
    for k, ((o, d), q) in enumerate(K):
        cars += [(k, o, d)]*q
    best = [float('inf'), None]
    nodes_by_dist = sorted(range(1, N), key=lambda i: (dist[i], pos[i]))

    def accessible_ok(assign):
        # assign: list of (p,q,i)
        for port in range(1, P-1):
            staying = {i for (p, q, i) in assign if p < port < q}
            active = {i for (p, q, i) in assign if p == port or q == port}
            if active & staying: return False
            # y: 가장 크게 잡을 수 있는 y (staying 아닌 노드 중 단조 경로로 닿는 것)
            y = {0}
            for i in order[1:]:
                if i not in staying and any(j in y for j in predset[i]):
                    y.add(i)
            if not active <= y: return False
        return True

    seen_multisets = set()
    for combo in itertools.product(*[compositions(o, d) for (_, o, d) in cars]):
        legs = sorted(l for c in combo for l in c)
        key = tuple(legs)
        if key in seen_multisets: continue
        seen_multisets.add(key)
        # 하한: 모든 leg가 가장 가까운 노드에
        if 2*len(legs)*(F+1) >= best[0]: continue
        occ = {i: [] for i in range(1, N)}
        assign = []
        def dfs(idx, cost):
            if cost + 2*(len(legs)-idx)*(F+1) >= best[0]: return
            if idx == len(legs):
                if accessible_ok(assign):
                    best[0] = cost; best[1] = (list(assign), combo)
                return
            p, q = legs[idx]
            prev_same = idx > 0 and legs[idx-1] == (p, q)
            for i in nodes_by_dist:
                if prev_same and pos[i] < pos[assign[-1][2]]: continue  # 대칭 제거
                if any(not (q <= a or b <= p) for a, b in occ[i]): continue
                occ[i].append((p, q)); assign.append((p, q, i))
                dfs(idx+1, cost + 2*(F+dist[i]))
                assign.pop(); occ[i].pop()
        dfs(0, 0)
    cost, (assign, combo) = best
    # z 복원
    z = Counter()
    for (k, o, d), comp in zip(cars, combo):
        # 순차 분할: (o,d) -> 첫 leg (o,m) + (m,d) ...  (긴 구간에서 짧은 구간으로)
        cur_o = o
        for (a, b) in comp[:-1]:
            z[(a, b, d)] += 1
    return dict(cost=cost, x=sorted(assign), z=dict(z), dist=dist, pos=pos,
                predset=predset, cars=cars, combo=combo)

def reconstruct(N, E, P, K, x, z):
    """function.cpp의 get_solution을 그대로 옮긴 것"""
    xs = set(x)
    pool = {}
    for k, ((o, d), q) in enumerate(K):
        pool[(o, d)] = [k]*q
    rem = dict(z)
    left = len([v for v in rem.values() if v > 0])
    while left > 0:
        for key in list(rem):
            value = rem[key]
            p, q, r = key
            amt = min(value, len(pool.get((p, r), [])))
            if amt == 0: continue
            for _ in range(amt):
                k = pool[(p, r)].pop()
                pool.setdefault((p, q), []).append(k)
                pool.setdefault((q, r), []).append(k)
            rem[key] -= amt
            if amt == value: left -= 1
    sol = {p: [] for p in range(P)}
    for c in range(P):
        acc = [True]*N
        if 0 < c < P-1:
            for i in range(1, N):
                acc[i] = not any((p, r, i) in xs for p in range(c) for r in range(c+1, P))
        nbr, pred, pos, dist, order = bfs_orientation(N, E, acc)
        def route(i):
            r = []
            while i != 0:
                r.append(i); i = pred[i]
            r.append(0); return r
        if c > 0:
            for i in order[1:]:
                for p in range(c):
                    if (p, c, i) in xs:
                        sol[c].append([route(i), 0])   # 원 코드: 하역 경로의 수요 번호는 항상 0
        if c < P-1:
            for i in reversed(order[1:]):
                for r in range(c+1, P):
                    if (c, r, i) in xs:
                        k = pool[(c, r)].pop()
                        sol[c].append([route(i)[::-1], k])
    return sol

def check(N, E, P, K, F, LB, solution):
    """util.check_feasibility를 numpy 없이 옮긴 것"""
    Eset = set(map(tuple, E))
    alloc = [-1]*N
    obj = 0; inf = []
    for p in range(P):
        for route, k in solution[p]:
            if len(route) <= 1: inf.append('short')
            if len(route) != len(set(route)): inf.append('not simple')
            for u, v in zip(route[:-1], route[1:]):
                if (u, v) not in Eset and (v, u) not in Eset: inf.append(f'bad edge {(u,v)}')
            if route[0] == 0:
                if alloc[route[-1]] != -1: inf.append(f'load occupied {route}')
                if any(alloc[i] != -1 for i in route[:-1]): inf.append(f'load blocked {route}')
                alloc[route[-1]] = k
            elif route[-1] == 0:
                if alloc[route[0]] == -1: inf.append(f'unload empty {route}')
                if any(alloc[i] != -1 for i in route[1:]): inf.append(f'unload blocked {route}')
                alloc[route[0]] = -1
            else:
                inf.append('rehandling route (not expected)')
            obj += F + len(route) - 1
        cur = Counter(a for a in alloc if a >= 0)
        exp = {k: r for k, ((o, d), r) in enumerate(K) if o <= p < d}
        if cur != exp: inf.append(f'port {p}: {dict(cur)} != {exp}')
    return obj, obj - LB, inf

def lower_bound(N, E, P, K, F):
    _, _, _, dist, _ = bfs_orientation(N, E)
    ds = sorted(dist[1:])
    LB = 0
    for p in range(P):
        load = sum(q for ((o, d), q) in K if o == p)
        unload = sum(q for ((o, d), q) in K if d == p)
        LB += F*(load+unload) + sum(ds[:load]) + sum(ds[:unload])
    return LB

def run(name, N, E, P, K, F):
    print('=====', name)
    LB = lower_bound(N, E, P, K, F)
    r = solve(N, E, P, K, F)
    print('dist', r['dist']); print('pos', r['pos']); print('pred', r['predset'])
    print('model cost', r['cost'], 'LB', LB, 'model obj', r['cost']-LB)
    print('x (p,q,i):', r['x'])
    print('z (p,q,r):', r['z'])
    sol = reconstruct(N, E, P, K, r['x'], r['z'])
    for p in range(P):
        print(' port', p)
        for route, k in sol[p]: print('    ', route, k)
    print('check (total, obj, infeasibility):', check(N, E, P, K, F, LB, sol))
    return r, sol

if __name__ == '__main__':
    LINE3 = [[0, 1], [1, 2]]                       # 일렬 배, 칸 2개
    # 미니 문제 A: 항구 3개. 차 A(0→2), 차 B(0→1)
    run('mini-A', 3, LINE3, 3, [[[0, 2], 1], [[0, 1], 1]], 10)
    # 미니 문제 B: 항구 4개. 차 A(0→2), 차 B(1→3)
    run('mini-B', 3, LINE3, 4, [[[0, 2], 1], [[1, 3], 1]], 10)
    # 미니 문제 B를 갈림길이 있는 배(0-1, 1-2, 1-3)에서
    run('mini-B-fork', 4, [[0, 1], [1, 2], [1, 3]], 4, [[[0, 2], 1], [[1, 3], 1]], 10)
    # 공식 예시: 일렬 배 0-1-2-3-4, 항구 5개, F=10
    run('official', 5, [[0, 1], [1, 2], [2, 3], [3, 4]], 5,
        [[[0, 2], 2], [[1, 4], 1], [[2, 3], 1], [[1, 3], 1], [[3, 4], 1]], 10)
    # 가지가 있는 배 (2장 그림 (가))
    E1 = [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [5, 6], [5, 7]]
    run('branch', 8, E1, 4, [[[0, 3], 2], [[0, 2], 1], [[1, 3], 1], [[1, 2], 2], [[2, 3], 2]], 10)
