"""오패금융연구소 사이트 빌드 스크립트.

src/*.html + guides.md + CHANGELOG.md  ->  _site/ (배포용)
- 공통 head(메타·GA4·애드센스), 상단 메뉴, 하단(버전 표시) 자동 삽입
- 가이드 글, 업데이트 내역, sitemap.xml, robots.txt, ads.txt, CNAME 자동 생성

형이 손대는 파일: guides.md(가이드 원고), CHANGELOG.md(버전 기록), 아래 설정값.
"""
import datetime
import html
import os
import re
import shutil

import markdown

# ── 설정 (여기만 고치면 됨) ─────────────────────────────
SITE_URL = "https://opae.kr"
SITE_NAME = "오패금융연구소"
DOMAIN = "opae.kr"
GA_ID = "G-Q543DWEBBW"
ADSENSE_CLIENT = "ca-pub-1957248819245044"  # 반드시 ca-pub- 로 시작
CONTACT_FORM_URL = ""  # 구글폼 링크를 넣으면 문의 페이지에 버튼이 생김
NAVER_VERIFY = "f8540d2140e4c6e55cce45bfc34e45ad827bb4c9"  # 네이버 서치어드바이저 소유 확인
GOOGLE_VERIFY = ""  # 구글 서치콘솔 HTML 태그 인증을 쓸 때만 입력
# ────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "_site")
TODAY = datetime.date.today().isoformat()

# 계산기 목록: 홈 화면 카드 순서 = 이 순서
CALCULATORS = [
    ("loan", "💰", "대출 상환 vs 투자 계산기", "원리금 조기상환 vs 미국주식·배당 투자 손익분기 역산"),
    ("whisky", "🥃", "위스키·주류 세금 계산기", "면세 범위 자동 판정 & 해외 직구 예상 관부가세 역산"),
    ("retire", "🛡️", "퇴직금 절세 비교기", "퇴직금 IRP 이전 vs 일시 수령 실질 수령액 및 절세율 비교"),
    ("isa", "📈", "ISA 만기 연금전환 시뮬레이터", "3년 만기 자금 연금계좌 전환 시 10% 추가 세액공제 최적화"),
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_front(text):
    """<!-- key: value --> 형식의 머리말과 본문 분리."""
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def get_version():
    m = re.search(r"^##\s*(v[\d.]+)", read(os.path.join(ROOT, "CHANGELOG.md")), re.M)
    return m.group(1) if m else "v0.0.0"


VERSION = get_version()


def layout(path, meta, body):
    """모든 페이지 공통 틀."""
    title = meta.get("title", SITE_NAME)
    desc = meta.get("description", "")
    ogt = meta.get("og_title", title)
    ogd = meta.get("og_description", desc)
    url = SITE_URL + path
    noindex = '<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    verify = ""
    if NAVER_VERIFY:
        verify += f'<meta name="naver-site-verification" content="{NAVER_VERIFY}">'
    if GOOGLE_VERIFY:
        verify += f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">'
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{e(ogt)}">
  <meta property="og:description" content="{e(ogd)}">
  {noindex}
  {verify}
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    input[type=number]::-webkit-inner-spin-button,input[type=number]::-webkit-outer-spin-button{{-webkit-appearance:none;margin:0}}
    .prose-opae h2{{font-size:1.05rem;font-weight:800;color:#fff;margin:1.4em 0 .5em}}
    .prose-opae h3{{font-weight:700;color:#e2e8f0;margin:1.2em 0 .4em}}
    .prose-opae p,.prose-opae li,.prose-opae td,.prose-opae th{{word-break:keep-all}}
    .prose-opae p,.prose-opae li{{font-size:.875rem;line-height:1.75;color:#cbd5e1}}
    .prose-opae ul{{list-style:disc;padding-left:1.2em;margin:.5em 0}}
    .prose-opae ol{{list-style:decimal;padding-left:1.2em;margin:.5em 0}}
    .prose-opae a{{color:#60a5fa;text-decoration:underline}}
    .prose-opae table{{width:100%;font-size:.8rem;margin:.8em 0;border-collapse:collapse}}
    .prose-opae th,.prose-opae td{{border:1px solid #334155;padding:.4em .5em;color:#cbd5e1}}
  </style>
</head>
<body class="bg-slate-900 text-slate-100 antialiased min-h-screen p-4 flex flex-col items-center">
  <nav class="w-full max-w-lg flex items-center justify-between text-xs text-slate-400 py-1">
    <a href="/" class="font-bold text-slate-200 hover:text-white">📊 {SITE_NAME}</a>
    <span class="space-x-3"><a href="/#calculators" class="hover:text-white">계산기</a><a href="/guide/" class="hover:text-white">가이드</a></span>
  </nav>
{body}
  <footer class="w-full max-w-lg pt-6 pb-4 text-center text-xs text-slate-500 space-y-2">
    <p class="space-x-3"><a href="/about/" class="hover:text-slate-300">소개</a><a href="/contact/" class="hover:text-slate-300">문의</a><a href="/privacy/" class="hover:text-slate-300">개인정보처리방침</a><a href="/changelog/" class="hover:text-slate-300">업데이트 내역</a></p>
    <p>계산 결과는 참고용이며 법률·세무 자문이 아닙니다.</p>
    <p>© {TODAY[:4]} {SITE_NAME} · {VERSION}</p>
  </footer>
</body>
</html>
"""


def card(href, icon, name, sub):
    return f"""      <a href="{href}" class="block p-4 rounded-2xl bg-[#161b22] border border-slate-800 hover:border-blue-500/60 transition group shadow-md">
        <div class="flex items-center justify-between"><div class="flex items-center gap-3">
          <span class="text-2xl p-2 rounded-xl bg-slate-900 border border-slate-800">{icon}</span>
          <div><h2 class="text-sm font-bold text-white group-hover:text-blue-400 transition">{html.escape(name)}</h2>
          <p class="text-xs text-slate-400">{html.escape(sub)}</p></div></div>
          <span class="text-slate-600 group-hover:text-blue-400 transition text-sm font-bold">→</span></div>
      </a>"""


def load_guides():
    """guides.md를 '====='(5개 이상) 줄로 나눠 글 목록으로 만든다."""
    path = os.path.join(ROOT, "guides.md")
    if not os.path.exists(path):
        return []
    guides = []
    for chunk in re.split(r"^={5,}\s*$", read(path), flags=re.M):
        chunk = chunk.strip()
        if not chunk or chunk.startswith("<!--"):
            continue
        meta, lines, body_start = {}, chunk.splitlines(), 0
        for i, line in enumerate(lines):
            m = re.match(r"^(title|slug|date|description|calc|draft):\s*(.*)$", line)
            if m:
                meta[m.group(1)] = m.group(2).strip()
            elif line.strip():
                body_start = i
                break
        if meta.get("draft", "").lower() in ("yes", "true", "1") or "slug" not in meta:
            continue
        meta["body"] = "\n".join(lines[body_start:])
        guides.append(meta)
    guides.sort(key=lambda g: g.get("date", ""), reverse=True)
    return guides


def md(text):
    return markdown.markdown(text, extensions=["tables"])


def build():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    urls = []
    guides = load_guides()

    # 1) src/*.html 페이지
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".html"):
            continue
        slug = name[:-5]
        meta, body = parse_front(read(os.path.join(SRC, name)))
        path = "/" if slug == "index" else f"/{slug}/"
        cards = "\n".join(card(f"/{s}/", i, n, d) for s, i, n, d in CALCULATORS)
        glist = "\n".join(
            f'<li><a href="/guide/{g["slug"]}/" class="hover:text-blue-400">{html.escape(g["title"])}</a></li>'
            for g in guides[:5]) or '<li class="text-slate-500">가이드 글 준비 중입니다.</li>'
        body = (body.replace("{{CALCULATOR_CARDS}}", cards)
                    .replace("{{GUIDE_LIST}}", glist)
                    .replace("{{CONTACT_FORM_URL}}", CONTACT_FORM_URL))
        if slug == "contact" and not CONTACT_FORM_URL:
            body = re.sub(r"<!--FORM-->.*?<!--/FORM-->", '<p class="text-sm text-slate-400">문의 양식을 준비 중입니다.</p>', body, flags=re.S)
        write(("" if slug == "index" else slug + "/") + "index.html", layout(path, meta, body))
        if slug != "404" and not meta.get("noindex"):
            urls.append(path)
    if os.path.exists(os.path.join(OUT, "404", "index.html")):
        shutil.move(os.path.join(OUT, "404", "index.html"), os.path.join(OUT, "404.html"))
        os.rmdir(os.path.join(OUT, "404"))

    # 2) 가이드 글
    items = []
    for g in guides:
        calc = ""
        if g.get("calc"):
            calc = f'<a href="{g["calc"]}" class="block mt-6 p-3 rounded-xl bg-blue-600/20 border border-blue-500/40 text-center text-sm font-bold text-blue-300 hover:bg-blue-600/30">→ 계산기로 바로 계산해보기</a>'
        body = f"""  <main class="w-full max-w-lg bg-slate-800/90 rounded-2xl shadow-xl border border-slate-700 p-5 my-3">
    <p class="text-xs text-slate-500"><a href="/guide/" class="hover:text-slate-300">가이드</a> · {g.get('date', '')}</p>
    <h1 class="text-xl font-extrabold text-white mt-1">{html.escape(g['title'])}</h1>
    <article class="prose-opae mt-4">{md(g['body'])}</article>
    {calc}
  </main>"""
        p = f"/guide/{g['slug']}/"
        write(f"guide/{g['slug']}/index.html", layout(p, {"title": f"{g['title']} | {SITE_NAME}", "description": g.get("description", "")}, body))
        urls.append(p)
        items.append(f'<li class="py-2 border-b border-slate-700"><a href="{p}" class="text-sm font-bold text-white hover:text-blue-400">{html.escape(g["title"])}</a><p class="text-xs text-slate-400">{html.escape(g.get("description", ""))}</p></li>')
    body = f"""  <main class="w-full max-w-lg bg-slate-800/90 rounded-2xl shadow-xl border border-slate-700 p-5 my-3">
    <h1 class="text-xl font-extrabold text-white">가이드</h1>
    <p class="text-xs text-slate-400 mt-1">계산기 뒤에 있는 원리와 실제 사례를 정리합니다.</p>
    <ul class="mt-4">{''.join(items) or '<li class="text-sm text-slate-500">가이드 글 준비 중입니다.</li>'}</ul>
  </main>"""
    write("guide/index.html", layout("/guide/", {"title": f"가이드 | {SITE_NAME}", "description": "절세·재테크·급여 계산의 원리와 실제 사례를 정리한 가이드 모음"}, body))
    urls.append("/guide/")

    # 3) 업데이트 내역 (첫 줄 제목은 빼고 렌더링)
    log = md(read(os.path.join(ROOT, "CHANGELOG.md")).split("\n", 1)[1])
    body = f"""  <main class="w-full max-w-lg bg-slate-800/90 rounded-2xl shadow-xl border border-slate-700 p-5 my-3">
    <h1 class="text-xl font-extrabold text-white">업데이트 내역</h1>
    <article class="prose-opae mt-2">{log}</article>
  </main>"""
    write("changelog/index.html", layout("/changelog/", {"title": f"업데이트 내역 | {SITE_NAME}", "description": f"{SITE_NAME} 계산기 수정·추가 기록"}, body))
    urls.append("/changelog/")

    # 4) 검색엔진·광고용 파일
    sm = "\n".join(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write("ads.txt", f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n")
    write("CNAME", DOMAIN + "\n")
    write(".nojekyll", "")
    print(f"built {VERSION}: {len(urls)} pages -> _site/")


if __name__ == "__main__":
    build()
