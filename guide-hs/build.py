"""ch1.html ~ ch12.html을 묶어 index.html(화면용), print.html과 PDF(출력용)를 만든다.

사용법: python3 guide-hs/build.py                    # index.html + print.html + PDF
        python3 guide-hs/build.py --no-pdf           # index.html + print.html만
        python3 guide-hs/build.py --preview 4 DIR    # 4장만 DIR/preview_ch4.html, .pdf로 (원고 확인용)
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
PDF = HERE / "ogc2025-tryagain-guide-hs.pdf"

DOC_TITLE = "OGC 2025 1등 풀이 해설: 고등학생판"
KICKER = "OGC 2025 · tryAgain 풀이 해설 · 고등학생판"
SUB = ("자동차 운반선에 차를 싣고 내리는 순서를 정하는 문제와, 1등 팀 tryAgain의 풀이를 "
       "손으로 풀 수 있는 작은 예에서 출발해 설명합니다. 이과 고3 수준의 수학과 Python 기초만 있으면 읽을 수 있습니다.")
TITLES = [
    "문제 이해 ① 손으로 풀어 보기",
    "문제 이해 ② 대회 문제의 실제 모습",
    "풀이 한눈에 보기",
    "식으로 적는 법",
    "솔버가 푸는 법",
    "높이 매기기: 그래프와 너비 우선 탐색",
    "풀이의 아이디어: 규칙 두 개",
    "모형 한 줄씩",
    "해 복원",
    "솔버 설정과 시간 관리",
    "결과·한계·개선 방향",
    "학습 로드맵",
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
    try { var v = localStorage.getItem('ogc2025-guide-hs-chapter'); return v && document.getElementById(v) ? v : null; } catch (e) { return null; }
  }
  function show(scroll) {
    var id = (location.hash || '').slice(1);
    if (!/^ch\\d+$/.test(id) || !document.getElementById(id)) { id = saved() || 'ch1'; }
    chapters.forEach(function (c) { c.hidden = c.id !== id; });
    links.forEach(function (a) { a.classList.toggle('now', a.getAttribute('data-ch') === id); });
    try { localStorage.setItem('ogc2025-guide-hs-chapter', id); } catch (e) {}
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
  <div class="kicker">OGC 2025 · 풀이 해설 · 고등학생판</div>
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
