# STUDY_GUIDE.md -> STUDY_GUIDE.html  (run again after editing the .md)
import re, markdown, pathlib

here = pathlib.Path(__file__).parent
md = (here / "STUDY_GUIDE.md").read_text(encoding="utf8")
md = re.sub(r"~~(.+?)~~", r"<del>\1</del>", md)
md = re.sub(r"==(.+?)==", r"<mark>\1</mark>", md)  # 赤点回避 = must-know
# python-markdown needs a blank line before a list (GitHub doesn't)
is_li = lambda l: re.match(r"\s*(- |\d+\. )", l)
out, fence = [], False
for line in md.split("\n"):
    if line.startswith("```"): fence = not fence
    if not fence and is_li(line) and out and out[-1].strip() and not is_li(out[-1]) and not out[-1].startswith("  "):
        out.append("")
    if not fence and line[:1] in "📌✍🔁" and line and out and out[-1].strip():
        out.append("")  # these markers start their own paragraph
    out.append(line)
md = "\n".join(out)
body = markdown.markdown(md, extensions=["tables", "md_in_html", "fenced_code", "toc", "nl2br"])

# wrap each h2 block in a <section> so JS/CSS can scope behaviour per section
title, rest = body.split("<h2", 1)
parts = ("<h2" + rest).split("<h2")[1:]
secs = []
for i, p in enumerate(parts):
    cls = "sec"
    if "概念ドリル" in p[:200]: cls += " drill"
    if "白紙テスト" in p[:200]: cls += " selftest"
    if "模範解答" in p[:200]: cls += " answers"
    if "赤点回避" in p[:200]: cls += " mustsec"
    if i >= 1 and "drill" not in cls and "selftest" not in cls: cls += " recallable"
    secs.append(f'<section class="{cls}"><h2{p}</section>')
body = title + "".join(secs)
# mark competing-rights lines
body = re.sub(r"<(li|p)>🔁", r'<\1 class="rights">🔁', body)
body = body.replace("<p>📌", '<p class="scene">📌').replace("<p>✍", '<p class="en">✍')
# labels are not answers: keep them visible in recall mode
body = re.sub(r"<strong>(状況|何を聞いている？|シナリオの手がかり|対立する権利|反対側の視点|このセクションの読み方|問題：[^<]*)</strong>", r"<b>\1</b>", body)

html = (here / "_template.html").read_text(encoding="utf8").replace("{{BODY}}", body)
(here / "STUDY_GUIDE.html").write_text(html, encoding="utf8")
# docs/index.html = page for GitHub Pages and for "iPadで見る.bat" (folder holds only this file)
(here / "docs").mkdir(exist_ok=True)
(here / "docs" / "index.html").write_text(html, encoding="utf8")
print("wrote STUDY_GUIDE.html")

# `python build_html.py --serve` : let an iPad on the same Wi-Fi open the guide
import sys
if "--serve" in sys.argv:
    import socket, functools, http.server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sk:
        sk.connect(("8.8.8.8", 80))  # no packet is sent; just picks the Wi-Fi address
        ip = sk.getsockname()[0]
    print(f"\niPad の Safari で開く:  http://{ip}:8000\n（PC と同じ Wi-Fi に接続。この画面を閉じると見られなくなります）\n", flush=True)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(here / "docs"))
    http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()
