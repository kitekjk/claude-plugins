# feedback_log.jsonl 스키마 정의

`feedback_log.jsonl`의 기준 스키마는 `skills/doc-writing-team/contract.json`을 따릅니다. 이 문서는 사람이 읽기 쉬운 설명 버전입니다.

## 파일 위치

```text
skills/doc-writing-team/memory/feedback_log.jsonl
```

## 필수 규칙

- 한 줄 = 하나의 JSON 객체
- `user_feedback_raw`를 표준 필드로 사용
- `proposed_updates`는 `content` 필드를 기본 필드로 사용
- 상태 전이는 `lifecycle.status`와 `lifecycle.transitions`로 관리
- `application`은 실제 반영 결과가 있을 때만 기록

## 정식 타입

```typescript
interface FeedbackEntry {
  feedback_id: string;
  timestamp: string;
  document_type: "ADR" | "HLD" | "LLD" | "SYSTEM";
  user_feedback_raw: string;

  document_id?: string | null;
  document_path?: string;
  session_id?: string;

  classification: {
    layer: "common" | "adr" | "hld" | "lld" | "both";
    target_files: string[];
    confidence: "high" | "medium" | "low";
    reasoning: string;
  };

  extracted_preferences?: string[];
  extracted_aversions?: string[];

  proposed_updates: ProposedUpdate[];

  immediate_applicable: boolean;
  immediate_apply_reason?: string;

  lifecycle: {
    status: "recorded" | "classified" | "applied" | "verified" | "rejected" | "superseded";
    transitions: StatusTransition[];
  };

  conflicts: ConflictInfo[];

  application?: {
    applied: boolean;
    applied_at?: string;
    applied_to_draft?: boolean;
    applied_to_guide?: boolean;
    applied_by?: string;
    modified_files?: string[];
  };
}

interface ProposedUpdate {
  file: string;
  section: string;
  action: "add" | "modify" | "remove";
  content: string;
  before?: string;
  after?: string;
  rationale?: string;
}

interface StatusTransition {
  from: string;
  to: string;
  at: string;
  by: string;
  reason?: string;
}

interface ConflictInfo {
  conflicting_feedback_id: string;
  conflict_type: "contradictory" | "supersedes" | "partial_overlap";
  description: string;
  resolution?: "keep_new" | "keep_old" | "merge" | "user_decision";
  resolved_at?: string;
}
```

## 예시

### 1. 시스템 이벤트

```json
{
  "feedback_id": "fb_260309_090000_001",
  "timestamp": "2026-03-09T09:00:00Z",
  "document_type": "SYSTEM",
  "user_feedback_raw": "[초기화] feedback loop 활성화",
  "classification": {
    "layer": "common",
    "target_files": [],
    "confidence": "high",
    "reasoning": "시스템 이벤트"
  },
  "proposed_updates": [],
  "immediate_applicable": false,
  "lifecycle": {
    "status": "recorded",
    "transitions": [
      {
        "from": "recorded",
        "to": "recorded",
        "at": "2026-03-09T09:00:00Z",
        "by": "system"
      }
    ]
  },
  "conflicts": []
}
```

### 2. 공통 스타일 피드백

```json
{
  "feedback_id": "fb_260309_091500_001",
  "timestamp": "2026-03-09T09:15:00Z",
  "document_type": "ADR",
  "document_id": "adr-order-cache",
  "user_feedback_raw": "수치에는 항상 출처를 붙여줘",
  "classification": {
    "layer": "common",
    "target_files": [
      "memory/style_guide.md",
      "checklists/common-checklist.md"
    ],
    "confidence": "high",
    "reasoning": "모든 문서 타입에 공통 적용되는 스타일 규칙"
  },
  "extracted_preferences": [
    "수치에 출처 명시"
  ],
  "extracted_aversions": [],
  "proposed_updates": [
    {
      "file": "memory/style_guide.md",
      "section": "Phrase Bank",
      "action": "modify",
      "content": "모든 성능/비용/SLA 수치에는 출처를 포함합니다."
    }
  ],
  "immediate_applicable": true,
  "immediate_apply_reason": "현재 초안과 가이드에 동시에 반영 가능",
  "lifecycle": {
    "status": "classified",
    "transitions": [
      {
        "from": "recorded",
        "to": "classified",
        "at": "2026-03-09T09:15:05Z",
        "by": "style-learner"
      }
    ]
  },
  "conflicts": []
}
```

### 3. 문서 타입별 구조 피드백

```json
{
  "feedback_id": "fb_260309_092000_001",
  "timestamp": "2026-03-09T09:20:00Z",
  "document_type": "HLD",
  "document_id": "hld-order-routing",
  "user_feedback_raw": "Appendix에 참고 표를 더 쉽게 넣을 수 있게 해줘",
  "classification": {
    "layer": "hld",
    "target_files": [
      "specs/hld.md",
      "templates/hld.md",
      "checklists/hld-checklist.md"
    ],
    "confidence": "high",
    "reasoning": "HLD 전용 구조 피드백"
  },
  "proposed_updates": [
    {
      "file": "templates/hld.md",
      "section": "Appendix",
      "action": "add",
      "content": "참고 표와 세부 매핑은 Appendix에 둘 수 있습니다."
    }
  ],
  "immediate_applicable": false,
  "immediate_apply_reason": "구조 계약과 템플릿 업데이트가 먼저 필요",
  "lifecycle": {
    "status": "classified",
    "transitions": [
      {
        "from": "recorded",
        "to": "classified",
        "at": "2026-03-09T09:20:03Z",
        "by": "style-learner"
      }
    ]
  },
  "conflicts": []
}
```

## 운영 메모

- `memory/approved_corpus/*`는 스타일 참고용이므로 기본 `document_path` 대상이 아닙니다.
- 계약 변경이 필요한 피드백은 `contract.json`과 충돌하지 않는지 먼저 확인해야 합니다.
- 스키마를 바꿀 때는 `style-learner`, `style-analyzer`, `merge_style_updates.py`, `validate_repo_contract.py`를 함께 업데이트해야 합니다.
