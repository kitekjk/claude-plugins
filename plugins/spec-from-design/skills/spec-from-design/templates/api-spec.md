# {PREFIX}-API-{DOMAIN}-{번호} {API명}

## 기본 정보
- type: api_spec
- domain: {도메인}
- id: {PREFIX}-API-{DOMAIN}-{번호}
- source: {LLD 문서명} Section 6.x

## 관련 정책
- POLICY-{DOMAIN}-001

## 관련 Spec
- {PREFIX}-{DOMAIN}-{번호} (Use Case)

## API 개요
{엔드포인트 목록}

## 공통 사항

### 인증
{인증 방식}

### 공통 에러 응답
{공통 에러 형식}

## 엔드포인트

### {HTTP Method} {path}
- 역할 제한: {접근 가능 역할}
- 출처: {LLD Section 번호}

**요청**

| 필드 | 타입 | 필수 | 검증 | 설명 |
|------|------|------|------|------|
| {field} | {type} | {Y/N} | {조건} | {설명} |

**응답 ({상태코드})**
```json
{
  "result": "value"
}
```

**에러 응답**

| HTTP 상태 | 에러 코드 | 조건 | 메시지 |
|-----------|----------|------|--------|
| {400} | {ERR_001} | {조건} | {메시지} |
