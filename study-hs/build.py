"""ch1.html ~ ch16.html을 묶어 index.html(화면용), print.html과 PDF(출력용)를 만든다.

사용법: python3 study-hs/build.py                    # index.html + print.html + PDF
        python3 study-hs/build.py --no-pdf           # index.html + print.html만
        python3 study-hs/build.py --preview 4 DIR    # 4장만 DIR/preview_ch4.html, .pdf로 (원고 확인용)
"""
import datetime
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INDEX = HERE / "index.html"
HTML = HERE / "print.html"
PDF = HERE / "ogc2025-mip-theory-hs.pdf"

DOC_TITLE = "처음 만나는 최적화 이론"
KICKER = "OGC 2025 1등 풀이를 읽기 위한 · 고등학생용 최적화 이론 교재"
SUB = ("자동차 운반선 문제의 1등 풀이를 이해하는 데 필요한 벡터·행렬, 그래프, 선형계획, 정수계획 이론을 "
       "고등학교 수학에서 출발해 설명합니다. 이과 고3 수준의 수학과 Python 기초만 있으면 읽을 수 있습니다.")
TITLES = [
    "들어가며: 이 책의 지도",
    "최적화 문제의 말과 기호",
    "벡터와 행렬 첫걸음",
    "그래프와 너비 우선 탐색",
    "높이, 방향, 이분 그래프",
    "선형계획 ①: 그림으로 풀기",
    "선형계획 ②: 꼭짓점을 계산으로",
    "심플렉스법",
    "쌍대성",
    "내부점법과 크로스오버",
    "정수계획 모델링 ①: 0과 1로 논리 적기",
    "정수계획 모델링 ②: 흐름, 묶음, 순서",
    "완화와 분지한계법",
    "강한 정식화와 절단평면",
    "분해 기법: 라그랑지 완화와 열 생성",
    "종합: tryAgain 모형을 이론으로 다시 읽기",
]
N = len(TITLES)
LONG_PRE_LINES = 30
LONG_TABLE_ROWS = 15

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')

NAV_JS = """
(function () {
  var chapters = [].slice.call(document.querySelectorAll('.chapter'));
  var links = [].slice.call(document.querySelectorAll('.chapters a'));
  function saved() {
    try { var v = localStorage.getItem('ogc2025-study-hs-chapter'); return v && document.getElementById(v) ? v : null; } catch (e) { return null; }
  }
  function show(scroll) {
    var id = (location.hash || '').slice(1);
    if (!/^ch\\d+$/.test(id) || !document.getElementById(id)) { id = saved() || 'ch1'; }
    chapters.forEach(function (c) { c.hidden = c.id !== id; });
    links.forEach(function (a) { a.classList.toggle('now', a.getAttribute('data-ch') === id); });
    try { localStorage.setItem('ogc2025-study-hs-chapter', id); } catch (e) {}
    if (scroll) { window.scrollTo(0, 0); }
  }
  window.addEventListener('hashchange', function () { show(true); });
  show(false);
})();
"""


def read(name):
    return (HERE / name).read_text()


def py_html(m):
    """<pre class="py">: 줄마다 span으로 싸서 CSS 카운터로 줄 번호를 붙인다(화면·출력 공통)."""
    lines = m.group(1).removeprefix("\n").removesuffix("\n").split("\n")
    cls = "py long" if len(lines) > LONG_PRE_LINES else "py"
    return f'<pre class="{cls}">' + "".join(f'<span class="ln">{l}</span>' for l in lines) + "</pre>"


def chapter_src(n):
    s = read(f"ch{n}.html")
    return re.sub(r'<pre class="py">(.*?)</pre>', py_html, s, flags=re.S)


def build_index():
    css = read("_base.css") + read("_extra.css")
    nav = "\n".join(
        f'    <a href="#ch{n}" data-ch="ch{n}">{n} {t}</a>' for n, t in enumerate(TITLES, 1)
    )
    body = "\n\n".join(chapter_src(n) for n in range(1, N + 1))
    INDEX.write_text(f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{DOC_TITLE}</title>
{FONTS}
<style>
{css}
</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">{KICKER}</div>
  <nav class="chapters" aria-label="전체 구성">
{nav}
  </nav>

{body}

</div>
<script>{NAV_JS}</script>
</body>
</html>
""")


def pre_html(m):
    attrs = m.group(1)
    lines = m.group(2).removeprefix("\n").removesuffix("\n").split("\n")
    long = len(lines) > LONG_PRE_LINES
    if long:
        attrs = attrs[:-1] + ' long"' if 'class="' in attrs else attrs + ' class="long"'
    spans = []
    for l in lines:
        hang = len(l) - len(l.lstrip(" ")) + 4
        spans.append(f'<span class="ln" style="padding-left:{hang}ch;text-indent:-{hang}ch">{l}</span>')
    return f"<pre{attrs}>" + "".join(spans) + "</pre>"


def chapter_print_html(n):
    s = chapter_src(n)
    s = re.sub(r'\s*<div class="pager">.*?</div>', "", s, flags=re.S)
    s = s.replace("<details>", "<details open>")
    # 줄 번호를 이미 붙인 py 블록은 건드리지 않는다
    s = re.sub(r'<pre((?: class="(?!py)[^"]*")?)>(.*?)</pre>', pre_html, s, flags=re.S)
    s = re.sub(
        r"<table([^>]*)>(.*?)</table>",
        lambda m: "<table" + m.group(1) + (' data-long="1"' if m.group(2).count("<tr") > LONG_TABLE_ROWS else "")
        + ">" + m.group(2) + "</table>",
        s,
        flags=re.S,
    )
    return s


def print_css(chapters):
    chapter_pages = "\n".join(
        f'@page ch{n} {{ @bottom-left {{ content: "{n}장 {TITLES[n - 1]}"; font: 8pt "Apple SD Gothic Neo", sans-serif; color: #56657a; }} }}\n'
        f"#ch{n} {{ page: ch{n}; }}"
        for n in chapters
    )
    return (read("_base.css") + read("_extra.css")
            + read("_print.css").replace("CHAPTER_PAGES", chapter_pages) + read("_extra_print.css")
            + "\ntable[data-long] { break-inside: auto; }\n")


def build_print(pages):
    css = print_css(range(1, N + 1))
    toc = "\n".join(
        f'<li><span class="n">{n}장</span><span class="t">{t}</span><span class="p">{pages[n - 1] if pages else ""}</span></li>'
        for n, t in enumerate(TITLES, 1)
    )
    today = datetime.date.today().isoformat()
    body = "\n".join(chapter_print_html(n) for n in range(1, N + 1))
    HTML.write_text(f"""<!doctype html>
<html lang="ko" data-theme="light">
<head>
<meta charset="utf-8">
<title>{DOC_TITLE}</title>
<style>
{css}
.toc ol {{ font-size: 10.5pt; }}
.toc li {{ padding: 5pt 0; }}
</style>
</head>
<body>
<div class="wrap">
<section class="cover">
  <div class="kicker">OGC 2025 · 고등학생용 이론 교재</div>
  <h1>{DOC_TITLE}</h1>
  <p class="sub">{SUB}</p>
  <p class="date">{today} 작성 · 초안</p>
</section>
<section class="toc">
  <h2>차례</h2>
  <ol>
{toc}
  </ol>
</section>
{body}
</div>
</body>
</html>
""")


def render(html=HTML, pdf=PDF):
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
             f"--user-data-dir={profile}", f"--print-to-pdf={pdf}", Path(html).as_uri()],
            check=True, capture_output=True,
        )


def chapter_start_pages():
    text = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], check=True, capture_output=True, text=True).stdout
    pages = text.split("\f")
    found = []
    for n in range(1, N + 1):
        found.append(next(i + 1 for i, p in enumerate(pages) if i >= 2 and re.search(rf"^\s*{n} / {N}\s*$", p, re.M)))
    return found


def preview(n, outdir):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    html, pdf = out / f"preview_ch{n}.html", out / f"preview_ch{n}.pdf"
    html.write_text(f"""<!doctype html>
<html lang="ko" data-theme="light">
<head><meta charset="utf-8"><title>{n}장 미리보기</title>
<style>
{print_css([n])}
</style></head>
<body><div class="wrap">
{chapter_print_html(n)}
</div></body></html>
""")
    render(html, pdf)
    print(pdf)


def main():
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        preview(int(sys.argv[i + 1]), sys.argv[i + 2])
        return
    build_index()
    build_print(None)
    if "--no-pdf" in sys.argv:
        return
    render()
    pages = chapter_start_pages()
    build_print(pages)
    render()
    assert chapter_start_pages() == pages
    print("chapter start pages:", pages)


if __name__ == "__main__":
    main()
