# 2044smile.github.io

이창석(Lee Changseok) 개인 포트폴리오 사이트 — <https://2044smile.github.io/>

## 구조

빌드 도구도, 의존성도, 템플릿 엔진도 없는 **단일 파일 정적 사이트**입니다.
`index.html` 하나에 마크업과 스타일이 함께 들어 있고, GitHub Pages가 그대로 서비스합니다.

```
index.html        사이트 본문 전체 (HTML + <style> 인라인)
404.html          동일한 톤의 404 페이지
assets/img/       index.html이 참조하는 이미지만
robots.txt        크롤러 허용 + sitemap 위치
sitemap.xml       루트 URL 1건
.nojekyll         Jekyll 비활성화 — 삭제하면 빌드가 깨집니다
```

## 작성 규칙

- **순수 정적** — Liquid(`{% %}`, `{{ }}`), npm 패키지, 빌드 스크립트를 쓰지 않습니다. 파일을 열면 보이는 그대로가 배포 결과입니다.
- **색상은 CSS 변수로만** — `:root`의 `--bg` `--text` `--muted` `--faint` `--accent` 등을 쓰고, 색상 리터럴을 규칙 안에 직접 넣지 않습니다.
- **섹션 단위 구성** — `<section id="…">` + `<h2>` 하나가 한 섹션입니다. 구분선·여백은 `section` 공통 규칙이 처리합니다.
- **항목 추가는 블록 복사** — 프로젝트는 `.project`(또는 대표 항목은 `.activity.featured`), 자격증은 `.cert`, 글 목록은 `.post` 블록을 복사해 내용만 바꿉니다. 새 CSS를 만들지 않습니다.
- **이미지** — `assets/img/<슬러그>.png`. `index.html`이 참조하지 않는 이미지는 커밋하지 않습니다.
- **폰트** — 제목 `Sora`, 본문 `Noto Sans KR`, 라벨·수치 `IBM Plex Mono`. 새 폰트를 추가하지 않습니다.
- **반응형** — 레이아웃 변경은 `@media (max-width: 640px)` 블록 한 곳에만 모읍니다.
- **사실만 게시** — 자격증·프로젝트 성과처럼 검증이 필요한 내용은 확인된 것만 올리고, 미확정 항목은 주석 템플릿으로 남겨둡니다.
- **커밋 메시지** — 영문 명령형 한 줄 (`Add …`, `Swap …`, `Remove …`).

## 로컬 확인

```bash
python3 -m http.server 8000
# http://localhost:8000
```
