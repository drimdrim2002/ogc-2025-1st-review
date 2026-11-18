"""솔버 로그를 구경하기 위한 예 (5장). 일렬 배(칸 8개), 항구 7개, 차 25대.

공식 예시는 너무 작아 로그가 한 줄로 끝난다. 이 문제는 조금 커서
휴리스틱이 해를 찾는 줄(H)과 하한이 올라가는 모습이 로그에 나온다.
- 설치: pip install gurobipy   (제한 라이선스로 풀 수 있는 크기다: 변수 248개)
- 실행: python3 gurobi_log_demo.py   (같은 폴더의 roro_model_gurobipy.py 를 쓴다)
"""
from roro_model_gurobipy import build_model

prob = {
    "N": 9, "E": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8]], "P": 7,
    "K": [[[0, 1], 3], [[0, 2], 1], [[0, 3], 2], [[0, 4], 1], [[1, 2], 2], [[1, 6], 1], [[2, 3], 2],
          [[2, 4], 1], [[3, 4], 1], [[3, 5], 2], [[3, 6], 1], [[4, 5], 3], [[5, 6], 5]],
    "F": 10,
}
model, x, y, z = build_model(prob)
model.Params.Threads = 1        # 스레드 하나로: 돌릴 때마다 같은 로그가 나오게
model.optimize()
print("총비용 =", model.ObjVal)
