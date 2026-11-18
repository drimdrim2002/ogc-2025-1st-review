"""tryAgain 이 Gurobi 에 건 설정(10장)을 직접 걸어 보는 실험.

- 설치: pip install gurobipy   (pip 설치본의 제한 라이선스로 충분하다)
- 실행: python3 gurobi_params_demo.py
- 같은 폴더의 roro_model_gurobipy.py 가 만든 모형을 쓴다.
- 실험 1: 공식 예시. 아주 작아서 어떤 설정이든 순식간에 190 이 나온다.
- 실험 2: 직접 만든 조금 큰 문제(5×8 격자 배, 항구 6개, 차 107대, F = 100).
          총비용이 2만을 넘으면 상대 gap 기준이 먼저 걸린다는 것을 본다.
- 아래 결과는 gurobipy 14.0.0 에서 확인했다. 버전이나 컴퓨터가 다르면 숫자가 달라질 수 있다.
"""
import os
import tempfile

from roro_model_gurobipy import build_model

official = {
    "N": 5, "E": [[0, 1], [1, 2], [2, 3], [3, 4]], "P": 5,
    "K": [[[0, 2], 2], [[1, 4], 1], [[2, 3], 1], [[1, 3], 1], [[3, 4], 1]],
    "F": 10, "LB": 137,
}


def grid_ship(rows, cols):
    """rows × cols 격자 모양 배의 간선 목록. 왼쪽 위(노드 0)가 출입구."""
    E = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                E.append([r * cols + c, r * cols + c + 1])
            if r + 1 < rows:
                E.append([r * cols + c, (r + 1) * cols + c])
    return E


bigger = {
    "N": 40, "E": grid_ship(5, 8), "P": 6, "F": 100,
    "K": [[[0, 1], 20], [[0, 2], 5], [[0, 3], 6], [[0, 4], 2], [[0, 5], 1],
          [[1, 2], 12], [[1, 3], 2], [[1, 4], 5], [[1, 5], 4],
          [[2, 3], 7], [[2, 4], 4], [[2, 5], 6], [[3, 4], 7], [[3, 5], 8], [[4, 5], 18]],
}


def run(name, prob, team_settings=False, norel=0, mipgap=None):
    model, x, y, z = build_model(prob)
    log_path = os.path.join(tempfile.mkdtemp(), "gurobi.log")
    model.Params.LogToConsole = 0                # 화면에는 로그를 찍지 않고
    model.Params.LogFile = log_path              # 파일에만 남긴다
    if team_settings:
        model.Params.MIPGapAbs = 2 - 1e-3        # 차이가 2 미만이면 멈춘다
        model.Params.PoolSolutions = 1           # 해는 하나만 보관
        model.Params.Method = 2                  # 뿌리의 LP 를 배리어로
        model.Params.Crossover = 0               # 크로스오버 끄기 (10장의 단서 참고)
        model.Params.TimeLimit = 30              # 솔버가 쓸 수 있는 시간(초)
        model.Params.Heuristics = 0.15           # 휴리스틱 비율 15%
    if norel > 0:
        model.Params.NoRelHeurTime = norel       # 처음 norel 초는 NoRel 휴리스틱
    if mipgap is not None:
        model.Params.MIPGap = mipgap             # 상대 gap 기준 (기본값 1e-4)
    model.optimize()
    print(name, "→ 총비용", round(model.ObjVal), " 하한", round(model.ObjBound, 2),
          " 변수", model.NumVars, "개")
    for line in open(log_path):                  # 로그에서 경고 줄만 골라 보여 준다
        if line.startswith("Warning"):
            print("    로그:", line.strip())


print("실험 1: 공식 예시")
run("  기본 설정            ", official)
run("  팀의 설정            ", official, team_settings=True)
run("  팀의 설정 + NoRel 3초", official, team_settings=True, norel=3)

print("실험 2: 조금 큰 문제")
run("  팀의 설정            ", bigger, team_settings=True)
run("  팀의 설정 + MIPGap=0 ", bigger, team_settings=True, mipgap=0)
