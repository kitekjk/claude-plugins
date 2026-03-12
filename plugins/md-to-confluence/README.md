# md-to-confluence

Markdown 설계문서(HLD, LLD, 아키텍처 문서)를 Confluence wiki에 발행하는 Claude Code 플러그인.

## 핵심 원칙

**원본은 항상 Markdown이다.** Confluence는 사람들이 보는 공유 뷰일 뿐이다.

## 기능

- Markdown → Confluence Storage Format(XHTML) 변환
- Mermaid 다이어그램 → Macro Pack 매크로 (서버사이드 렌더링, mmdc 불필요)
- 코드블록 → Confluence Code 매크로 (언어 하이라이팅)
- GFM callout (`> [!NOTE]`) → Confluence 패널 매크로
- 테이블, 리스트, 이미지, 체크리스트 등 주요 Markdown 요소 지원
- Confluence REST API v2로 페이지 생성/업데이트
- `~/.claude.json`에서 인증 정보 자동 읽기

## 사용법

Claude Code에서 자연어로 요청:

```
이 HLD.md를 https://mycompany.atlassian.net/wiki/spaces/ARCH/pages/12345 하위에 올려줘
```

```
이 문서 수정했어, wiki에 반영해줘
```

```
이 MD를 Confluence 형식으로 변환만 해줘
```

## 의존성

**없음** — Python 3.9+ 표준 라이브러리만 사용합니다.

Mermaid 다이어그램은 Confluence의 [Macro Pack](https://marketplace.atlassian.com/apps/1227846) 앱이 서버에서 렌더링합니다.

## 라이선스

Apache-2.0
