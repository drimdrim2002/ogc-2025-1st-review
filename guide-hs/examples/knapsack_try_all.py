"""배낭 예(4장)를 '전부 해 보기'로 푼다. Σ 가 for 문이라는 것을 보이는 예.

물건 3개(가치 6, 5, 4 / 무게 4, 3, 2 kg), 배낭 용량 5 kg.
실행: python3 knapsack_try_all.py
"""
v = [6, 5, 4]                    # 가치
w = [4, 3, 2]                    # 무게(kg)
W = 5                            # 배낭 용량
best = 0
best_x = [0, 0, 0]
for x1 in range(2):              # 0 또는 1
    for x2 in range(2):
        for x3 in range(2):
            x = [x1, x2, x3]
            weight = 0
            value = 0
            for j in range(3):                   # Σ 를 for 문으로
                weight = weight + w[j] * x[j]
                value = value + v[j] * x[j]
            if weight <= W and value > best:     # 제약을 지키고 더 좋으면 기억
                best = value
                best_x = x
print(best_x, best)
