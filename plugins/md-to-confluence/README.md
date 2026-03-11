# md-to-confluence

Markdown 설계문서(HLD, LLD, 아키텍처 문서)를 Confluence wiki에 발행하는 Claude Code 플러그인.

## 핵심 원칙

**원본은 항상 Markdown이다.** Confluence는 사람들이 보는 공유 뷰일 뿐이다.

## 기능

- Markdown → Confluence Storage Format(XHTML) 변환
- Mermaid 다이어그램 → PNG 이미지 자동 렌더링
- 코드블록 → Confluence Code 매크로 (언어 하이라이팅)
- GFM callout (`> [!NOTE]`) → Confluence 패널 매크로
- 테이블, 리스트, 이미지 등 주요 Markdown 요소 지원
- wiki URL에서 자동 파싱하여 업로드 스크립트 생성

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

변환 시 자동 설치:

```bash
pip install markdown pymdown-extensions
```

Mermaid 다이어그램 렌더링 시 추가:

```bash
npm install -g @mermaid-js/mermaid-cli
```

## 라이선스

Apache-2.0
