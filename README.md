# opae.kr — 오패금융연구소

무료 절세·재테크 계산기 사이트. main 브랜치에 올리면 GitHub Actions가 자동으로 빌드·배포한다.

## 형이 고치는 파일
| 파일 | 용도 |
|---|---|
| `guides.md` | 가이드 글 원고 (파일 맨 위 설명 참고) |
| `CHANGELOG.md` | 버전 기록. 맨 위 `## v버전` 이 사이트 하단 버전으로 표시됨 |
| `build.py` 맨 위 설정 | 도메인, GA4, 애드센스, 구글폼 링크 |
| `src/*.html` | 계산기·페이지 본문 (파일 1개 = 페이지 1개) |

## 자동으로 만들어지는 것
공통 상단·하단, 광고·통계 코드, 가이드 페이지, 업데이트 내역 페이지, sitemap.xml, robots.txt, ads.txt, CNAME

## 새 계산기 추가
1. `src/새이름.html` 추가 (맨 위 `<!-- title/description -->` 머리말 + `<main>` 본문)
2. `build.py`의 `CALCULATORS` 목록에 한 줄 추가 → 홈 화면 카드 자동 생성
3. `CHANGELOG.md`에 버전 추가

## 로컬 확인
```
pip install markdown
python build.py   # _site/ 폴더에 결과 생성
```
