"""ch1.html ~ ch10.html을 묶어 index.html(화면용), print.html과 PDF(출력용)를 만든다.

사용법: python3 guide/build.py          # index.html + print.html + PDF
        python3 guide/build.py --no-pdf # index.html + print.html만
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
PDF = HERE / "ogc2025-tryagain-guide.pdf"

DOC_TITLE = "OGC 2025 1등 해법 해설"
KICKER = "OGC 2025 · tryAgain 해법 해설"
TITLES = [
    "문제 이해",
    "풀이 한눈에 보기",
    "MIP 기초 ① 정식화 읽고 쓰기",
    "MIP 기초 ② 솔버가 푸는 법",
    "정식화의 아이디어",
    "정식화 한 줄씩",
    "해 복원",
    "솔버 설정과 시간 관리",
    "결과·한계·베이스라인",
    "학습 로드맵",
]
N = len(TITLES)
LONG_PRE_LINES = 26
LONG_TABLE_ROWS = 15

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')

NAV_JS = """
(function () {
  var chapters = [].slice.call(document.querySelectorAll('.chapter'));
  var links = [].slice.call(document.querySelectorAll('.chapters a'));
  function saved() {
    try { var v = localStorage.getItem('ogc2025-guide-chapter'); return v && document.getElementById(v) ? v : null; } catch (e) { return null; }
  }
  function show(scroll) {
    var id = (location.hash || '').slice(1);
    if (!/^ch\\d+$/.test(id) || !document.getElementById(id)) { id = saved() || 'ch1'; }
    chapters.forEach(function (c) { c.hidden = c.id !== id; });
    links.forEach(function (a) { a.classList.toggle('now', a.getAttribute('data-ch') === id); });
    try { localStorage.setItem('ogc2025-guide-chapter', id); } catch (e) {}
    if (scroll) { window.scrollTo(0, 0); }
  }
  window.addEventListener('hashchange', function () { show(true); });
  show(false);
})();
"""


def read(name):
    return (HERE / name).read_text()


def chapter_src(n):
    return read(f"ch{n}.html")


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
    lines = m.group(1).removeprefix("\n").removesuffix("\n").split("\n")
    cls = ' class="long"' if len(lines) > LONG_PRE_LINES else ""
    spans = []
    for l in lines:
        hang = len(l) - len(l.lstrip(" ")) + 4
        spans.append(f'<span class="ln" style="padding-left:{hang}ch;text-indent:-{hang}ch">{l}</span>')
    return f"<pre{cls}>" + "".join(spans) + "</pre>"


def chapter_print_html(n):
    s = chapter_src(n)
    s = re.sub(r'\s*<div class="pager">.*?</div>', "", s, flags=re.S)
    s = s.replace("<details>", "<details open>")
    s = re.sub(r"<pre>(.*?)</pre>", pre_html, s, flags=re.S)
    s = re.sub(
        r"<table([^>]*)>(.*?)</table>",
        lambda m: "<table" + m.group(1) + (' class="long"' if m.group(2).count("<tr") > LONG_TABLE_ROWS else "")
        + ">" + m.group(2) + "</table>",
        s,
        flags=re.S,
    )
    return s


def build_print(pages):
    chapter_pages = "\n".join(
        f'@page ch{n} {{ @bottom-left {{ content: "{n}장 {t}"; font: 8pt "Apple SD Gothic Neo", sans-serif; color: #56657a; }} }}\n'
        f"#ch{n} {{ page: ch{n}; }}"
        for n, t in enumerate(TITLES, 1)
    )
    css = (read("_base.css") + read("_extra.css")
           + read("_print.css").replace("CHAPTER_PAGES", chapter_pages) + read("_extra_print.css"))
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
</style>
</head>
<body>
<div class="wrap">
<section class="cover">
  <div class="kicker">OGC 2025 · 해설 자료</div>
  <h1>{DOC_TITLE}</h1>
  <p class="sub">자동차 운반선 선적(Roll-on Roll-off) 문제 · tryAgain 팀의 정수선형최적화(MIP) 풀이를 MIP 기초부터 장별로 풀어 설명합니다.</p>
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


def render():
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
             f"--user-data-dir={profile}", f"--print-to-pdf={PDF}", HTML.as_uri()],
            check=True, capture_output=True,
        )


def chapter_start_pages():
    text = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], check=True, capture_output=True, text=True).stdout
    pages = text.split("\f")
    found = []
    for n in range(1, N + 1):
        found.append(next(i + 1 for i, p in enumerate(pages) if i >= 2 and re.search(rf"^\s*{n} / {N}\s*$", p, re.M)))
    return found


def main():
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
