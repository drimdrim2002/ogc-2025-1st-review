# OGC2025 1등(tryAgain) 풀이 해설과 MIP 이론 교재

[최적화 그랜드 챌린지 2025](https://ogchallenge.github.io/ogc/2025/)의 1등 팀 tryAgain이 쓴 풀이(C++/Gurobi MIP)를 분석한 자료입니다. 독자로는 CVRPTW 같은 휴리스틱을 다뤄 봤지만 MIP는 처음인 개발자를 생각했습니다.

| 폴더 | 내용 | 출력용 PDF |
|---|---|---|
| [`study/`](study/) | 이론 배경 교재 12장: 선형대수, 그래프, LP(심플렉스·쌍대성·내부점법), 정수계획 모델링, 분지한계법, 절단평면, 분해 기법 | `study/ogc2025-mip-theory-study.pdf` |
| [`guide/`](guide/) | 풀이 해설 10장: 문제, 정식화, 해 복원, 솔버 설정, 결과, 학습 로드맵 | `guide/ogc2025-tryagain-guide.pdf` |

권장 읽기 순서는 `study/` → `guide/`입니다. 화면에서 읽을 때는 각 폴더의 `index.html`을 여세요.

## 다시 빌드하기

장별 원고는 `ch*.html`입니다. 원고를 고친 뒤 아래 명령으로 index·print·PDF를 다시 만듭니다.

```bash
python3 guide/build.py
python3 study/build.py
```

## 참고

- tryAgain 팀의 원본 소스와 발표자료는 이 저장소에 포함하지 않았습니다. 해설 안에는 설명에 필요한 코드 일부만 발췌되어 있습니다.
- 팀 코드와 Gurobi는 실행하지 않았습니다. 본문의 수치는 같은 모형을 순수 Python으로 다시 구현해 계산한 결과입니다. 확인하지 못한 내용은 본문에 따로 표시했습니다.
