"""트럭 예(4장)를 '전부 해 보기'로 푼다.

짐 30톤. 큰 트럭은 9톤에 10만 원, 작은 트럭은 5톤에 7만 원.
큰 트럭 x대, 작은 트럭 y대를 0대부터 6대까지 모두 넣어 본다.
실행: python3 truck_try_all.py
"""
best_cost = 1000                 # 아주 큰 수로 시작
best_x = 0
best_y = 0
count = 0
for x in range(0, 7):            # 큰 트럭 0~6대
    for y in range(0, 7):        # 작은 트럭 0~6대
        if 9 * x + 5 * y >= 30:  # 제약: 짐을 다 실을 수 있는가
            count = count + 1
            cost = 10 * x + 7 * y            # 목적함수: 총비용
            if cost < best_cost:             # 지금까지 본 것보다 싸면 기억
                best_cost = cost
                best_x = x
                best_y = y
print("가능해의 수:", count)
print("최적해: 큰 트럭", best_x, "대, 작은 트럭", best_y, "대, 비용", best_cost)
