"""트럭 예(4장)를 솔버에 맡긴다. Google OR-Tools 사용 (pip install ortools).

실행: python3 truck_ortools.py
"""
from ortools.linear_solver import pywraplp

s = pywraplp.Solver.CreateSolver("SCIP")     # 솔버 준비 (SCIP은 무료 솔버 이름)
x = s.IntVar(0, s.infinity(), "big")         # 결정변수: 0 이상의 정수
y = s.IntVar(0, s.infinity(), "small")
s.Minimize(10 * x + 7 * y)                   # 목적함수
s.Add(9 * x + 5 * y >= 30)                   # 제약
s.Solve()                                    # 풀이
print(x.solution_value(), y.solution_value(), s.Objective().Value())
