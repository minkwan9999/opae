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
CONTACT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfINdHSM97Jn05XQp2uCRth2RIzM_aa36knb4_o6uJGJmRRTQ/viewform"  # 구글폼 링크를 넣으면 문의 페이지에 버튼이 생김
NAVER_VERIFY = "f8540d2140e4c6e55cce45bfc34e45ad827bb4c9"  # 네이버 서치어드바이저 소유 확인
GOOGLE_VERIFY = ""  # 구글 서치콘솔 HTML 태그 인증을 쓸 때만 입력
# ────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "_site")
# 한국 시간 기준 오늘 날짜 (예약 발행 판단에 사용)
TODAY = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date().isoformat()

# 계산기 목록: 홈 화면 카드 순서 = 이 순서
CALCULATORS = [
    ("leave-tax", "🍼", "휴직한 해 연말정산 계산기", "육아휴직·무급휴직 환급 예상 + IRP 헛방 체크 + 부부 공제 배분"),
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
  <meta property="og:image" content="{SITE_URL}/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/logo.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  {noindex}
  {verify}
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body{{word-break:keep-all;overflow-wrap:anywhere}}
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
    .prose-opae blockquote{{border-left:3px solid #f59e0b;background:#f59e0b14;padding:.5em .8em;margin:.8em 0;border-radius:.4em}}
  </style>
</head>
<body class="bg-slate-900 text-slate-100 antialiased min-h-screen p-4 flex flex-col items-center">
  <nav class="w-full max-w-lg flex items-center justify-between text-xs text-slate-400 py-1">
    <a href="/" class="flex items-center gap-1.5 font-bold text-slate-200 hover:text-white"><img src="/logo.svg" alt="" width="20" height="20" class="rounded-md">{SITE_NAME}</a>
    <span class="space-x-3"><a href="/#calculators" class="hover:text-white">계산기</a><a href="/guide/" class="hover:text-white">가이드</a></span>
  </nav>
{body}
  <footer class="w-full max-w-lg pt-6 pb-4 text-center text-xs text-slate-500
