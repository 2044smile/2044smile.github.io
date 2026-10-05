#!/usr/bin/env python3
"""Tistory(newbiecs.tistory.com) 글을 광고 없는 정적 페이지로 변환한다.

사용법:
  python3 scripts/sync_blog.py            # POST_IDS 전체 동기화
  python3 scripts/sync_blog.py 443 442    # 특정 글만

글 본문만 추출하므로 광고·댓글·사이드바는 포함되지 않는다.
본문 이미지는 assets/posts/<id>/ 에 내려받아 함께 커밋한다 (티스토리 이미지
URL은 서명이 걸려 있어 핫링크하면 만료 후 깨진다).
결과: posts/<id>/index.html, posts.json 갱신.
"""

import json
import pathlib
import re
import subprocess
import sys
import html as htmllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = "https://newbiecs.tistory.com"

# 큐레이션: 포트폴리오에 싣는 글 (id: 탭 분류)
# 탭: ai = AI · Vision, devops = DevOps, backend = Backend
POST_IDS = {
    # AI · Vision
    442: "ai", 441: "ai", 440: "ai", 438: "ai", 435: "ai", 434: "ai", 430: "ai",
    # DevOps · Infra
    443: "devops", 437: "devops", 433: "devops", 432: "devops", 423: "devops",
    417: "devops", 416: "devops", 411: "devops", 414: "devops", 415: "devops",
    362: "devops", 361: "devops", 360: "devops", 359: "devops",
    357: "devops", 330: "devops", 326: "devops", 324: "devops", 322: "devops", 280: "devops",
    # Backend · Python/Django
    436: "backend", 431: "backend", 427: "backend", 373: "backend", 363: "backend",
    353: "backend", 332: "backend", 331: "backend", 323: "backend", 316: "backend",
    271: "backend", 267: "backend", 266: "backend", 262: "backend",
}

TAB_LABEL = {"ai": "AI · Vision", "devops": "DevOps", "backend": "Backend"}

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — 이창석</title>
  <link rel="canonical" href="{origin}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #13161d; --border: #262c38; --text: #edebe3; --text-soft: #c9c7be;
      --muted: #a3a8b0; --faint: #737a84; --accent: #4fd1c0; --chip: #1b1f29;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Noto Sans KR', sans-serif; line-height: 1.85; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 760px; margin: 0 auto; padding: 0 22px; }}
    header .wrap {{ padding: 24px 22px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }}
    header a {{ color: var(--muted); }}
    h1 {{ font-family: 'Sora', 'Noto Sans KR', sans-serif; font-size: 30px; line-height: 1.35; margin: 36px 0 10px; }}
    .meta {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: var(--faint); margin-bottom: 36px; }}
    .meta .cat {{ color: var(--accent); }}
    article {{ font-size: 16px; color: var(--text-soft); padding-bottom: 24px; }}
    article h2, article h3, article h4 {{ font-family: 'Sora', 'Noto Sans KR', sans-serif; color: var(--text); line-height: 1.4; margin: 40px 0 12px; }}
    article h2 {{ font-size: 24px; }} article h3 {{ font-size: 20px; }} article h4 {{ font-size: 17px; }}
    article p {{ margin: 14px 0; }}
    article img {{ max-width: 100%; height: auto; border-radius: 10px; border: 1px solid var(--border); display: block; margin: 20px auto; }}
    article figure {{ margin: 20px 0; text-align: center; }}
    article figcaption {{ font-size: 13px; color: var(--faint); }}
    article pre {{ background: #0d1016; border: 1px solid var(--border); border-radius: 10px; padding: 18px; overflow-x: auto; font-size: 13.5px; line-height: 1.6; }}
    article code {{ font-family: 'IBM Plex Mono', monospace; }}
    article p code, article li code {{ background: var(--chip); border-radius: 5px; padding: 2px 7px; font-size: 13.5px; color: var(--accent); }}
    article pre code {{ background: none; padding: 0; color: var(--text-soft); }}
    article blockquote {{ margin: 20px 0; padding: 4px 20px; border-left: 3px solid var(--accent); background: var(--chip); border-radius: 0 10px 10px 0; color: var(--muted); }}
    article table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; display: block; overflow-x: auto; }}
    article th, article td {{ border: 1px solid var(--border); padding: 9px 13px; text-align: left; }}
    article th {{ background: var(--chip); color: var(--text); }}
    article hr {{ border: none; border-top: 1px solid var(--border); margin: 36px 0; }}
    article ul, article ol {{ padding-left: 24px; }}
    article li {{ margin: 6px 0; }}
    article span {{ color: inherit !important; }}
    .origin {{ margin: 48px 0 0; padding: 18px 22px; background: var(--chip); border: 1px solid var(--border); border-radius: 12px; font-size: 14px; color: var(--muted); }}
    footer {{ border-top: 1px solid var(--border); margin-top: 48px; }}
    footer .wrap {{ padding: 28px 22px 40px; font-size: 13px; color: var(--faint); }}
    footer a {{ color: var(--faint); }}
  </style>
</head>
<body>
<header>
  <div class="wrap">
    <a href="/posts/">← 글 목록</a>
    <a href="/" style="font-family: 'IBM Plex Mono', monospace;">2044smile.github.io</a>
  </div>
</header>
<main class="wrap">
  <h1>{title}</h1>
  <div class="meta"><span class="cat">{cat_label}</span> · {date}</div>
  <article>
{body}
  </article>
  <div class="origin">이 글은 제 티스토리 블로그에서 옮겨온 글입니다. <a href="{origin}">원문 보기 →</a></div>
</main>
<footer>
  <div class="wrap">© 2026 Lee Changseok · <a href="/">홈</a> · <a href="https://newbiecs.tistory.com/">티스토리</a></div>
</footer>
</body>
</html>
"""


def fetch(url: str) -> str:
    return subprocess.run(["curl", "-sL", url], capture_output=True, text=True, check=True).stdout


def fetch_bin(url: str, dest: pathlib.Path) -> bool:
    r = subprocess.run(["curl", "-sL", "-o", str(dest), url], capture_output=True)
    if r.returncode != 0 or not dest.exists() or dest.stat().st_size < 100:
        return False
    head = dest.read_bytes()[:16]
    return not head.lstrip()[:1] in (b"<", b"{")  # HTML/JSON 오류 응답 배제


def extract(page: str):
    title = htmllib.unescape(re.search(r'property="og:title" content="([^"]*)"', page).group(1))
    m = re.search(r'"published_time"[^>]*content="([^"]+)"', page) or re.search(
        r'property="article:published_time" content="([^"]+)"', page
    )
    date = m.group(1)[:10] if m else ""
    body = re.search(
        r'<div class="tt_article_useless_p_margin[^"]*"[^>]*>(.*?)<div class="container_postbtn',
        page, re.S,
    )
    if not body:
        raise RuntimeError("본문 추출 실패")
    return title, date, body.group(1)


def clean(body: str) -> str:
    # 광고·스크립트·댓글 위젯 제거
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<ins[^>]*>.*?</ins>", "", body, flags=re.S)
    body = re.sub(r"<iframe[^>]*>.*?</iframe>", "", body, flags=re.S)
    body = re.sub(r'<div class="revenue_unit_wrap.*?</div>\s*</div>', "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    # 글자색 인라인 스타일 제거 (다크 테마에서 검정 글씨 방지)
    body = re.sub(r'style="[^"]*color:[^"]*"', "", body)
    # srcset/onerror가 만료되는 원격 URL을 다시 가리키지 않도록 제거 (src만 남긴다)
    body = re.sub(r'\s(?:srcset|onerror|data-origin-src)="[^"]*"', "", body)
    return body.strip()


def localize_images(body: str, pid: int) -> str:
    img_dir = ROOT / "assets" / "posts" / str(pid)
    urls = re.findall(r'<img[^>]+src="(https://(?:blog\.kakaocdn\.net|img1\.daumcdn\.net|t1\.daumcdn\.net|tistory\d*\.daumcdn\.net)[^"]+)"', body)
    for i, url in enumerate(dict.fromkeys(urls), 1):
        raw = htmllib.unescape(url)
        ext = ".gif" if ".gif" in raw.lower() else ".jpg" if (".jpg" in raw.lower() or ".jpeg" in raw.lower()) else ".png"
        img_dir.mkdir(parents=True, exist_ok=True)
        dest = img_dir / f"{i:02d}{ext}"
        if not dest.exists():
            if not fetch_bin(raw, dest):
                dest.unlink(missing_ok=True)
                continue
            try:  # 폭 1200px 초과 시 축소 (저장소 용량 관리, GIF 제외)
                from PIL import Image
                if ext != ".gif":
                    im = Image.open(dest)
                    if im.width > 1200:
                        im = im.resize((1200, int(im.height * 1200 / im.width)))
                        im.save(dest)
            except Exception:
                pass
        body = body.replace(url, f"/assets/posts/{pid}/{dest.name}")
    return body


def main():
    ids = [int(a) for a in sys.argv[1:]] or sorted(POST_IDS, reverse=True)
    index_path = ROOT / "posts.json"
    index = {str(p["id"]): p for p in json.loads(index_path.read_text())} if index_path.exists() else {}

    for pid in ids:
        tab = POST_IDS[pid]
        page = fetch(f"{BLOG}/{pid}")
        title, date, body = extract(page)
        body = localize_images(clean(body), pid)
        out = ROOT / "posts" / str(pid)
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            TEMPLATE.format(title=htmllib.escape(title), cat_label=TAB_LABEL[tab],
                            date=date, body=body, origin=f"{BLOG}/{pid}"),
            encoding="utf-8",
        )
        index[str(pid)] = {"id": pid, "title": title, "date": date, "tab": tab}
        print(f"ok {pid} | {date} | {title[:50]}")

    posts = sorted(index.values(), key=lambda p: -p["id"])
    index_path.write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"posts.json: {len(posts)}편")


if __name__ == "__main__":
    main()
