"""채점기를 작게 흉내 낸 것 (2장). 선적·하역 경로만 다룬다.

대회의 진짜 채점 코드(util.py 의 check_feasibility)는 여기에 위치변경 경로 처리와
몇 가지 검사(간선이 실제로 있는지, 항구를 떠날 때 차의 수가 맞는지)가 더 있다.
실행: python3 mini_checker.py
"""


def check(N, F, solution):
    cell = [-1] * N                      # cell[i] = 칸 i에 있는 차의 수요 번호. 비어 있으면 -1
    total = 0
    for port in range(len(solution)):
        for route, k in solution[port]:
            if route[0] == 0:            # 출입구에서 시작 → 선적 경로
                for i in route[1:]:
                    if cell[i] != -1:
                        return "무효: 길에 차가 있음"
                cell[route[-1]] = k      # 도착한 칸에 수요 k의 차를 놓는다
            else:                        # 출입구에서 끝남 → 하역 경로
                if cell[route[0]] == -1:
                    return "무효: 내릴 차가 없음"
                for i in route[1:]:
                    if cell[i] != -1:
                        return "무효: 길에 차가 있음"
                cell[route[0]] = -1      # 칸을 비운다
            total = total + F + len(route) - 1
    return total


if __name__ == "__main__":
    # 미니 문제 B의 해 (가): 항구 1에서 차 A(수요 0)를 잠깐 내린다
    sol_ga = [
        [[[0, 1], 0]],                                  # 항구 0
        [[[1, 0], 0], [[0, 1, 2], 1], [[0, 1], 0]],     # 항구 1
        [[[1, 0], 0]],                                  # 항구 2
        [[[2, 1, 0], 1]],                               # 항구 3
    ]
    print(check(3, 10, sol_ga))

    # 같은 해에서 항구 1의 순서만 바꾼 것: B를 먼저 실으려 한다
    sol_bad = [
        [[[0, 1], 0]],
        [[[0, 1, 2], 1], [[1, 0], 0], [[0, 1], 0]],
        [[[1, 0], 0]],
        [[[2, 1, 0], 1]],
    ]
    print(check(3, 10, sol_bad))
