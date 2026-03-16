# md-to-confluence 플러그인

이 플러그인의 구조와 정책은 `contract.json`이 기준입니다.

## 우선순위

1. `contract.json`
2. `SKILL.md`

## 핵심 계약

- 원본은 항상 Markdown. Confluence는 공유 뷰일 뿐이다.
- 변환: `scripts/md2confluence.py` 사용 (외부 패키지 없음)
- Mermaid: mmdc CLI 불필요. Macro Pack 매크로로 서버 렌더링.
- 인증: `~/.claude.json`에서 자동 읽기. 수동 설정 불필요.
- 100KB+ 문서는 MCP 도구 대신 스크립트 사용.

## 구조

```text
md-to-confluence/
├── .claude-plugin/plugin.json
├── skills/md-to-confluence/
│   ├── SKILL.md              # 스킬 진입점
│   ├── CLAUDE.md             # 이 파일
│   ├── contract.json         # 단일 기준
│   └── references/           # 변환 규칙 레퍼런스
├── scripts/
│   └── md2confluence.py      # 변환 + 업로드 스크립트
└── README.md
```

## 워크플로우

1. 사용자 요청 패턴 판별 (create / update / convertOnly)
2. MD 파일 읽기
3. Confluence URL 파싱 (업로드 시)
4. `scripts/md2confluence.py` 실행
5. 결과 URL 안내
