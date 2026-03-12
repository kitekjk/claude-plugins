# {PREFIX}-{DOMAIN}-{번호} {서비스명}

## 기본 정보
- type: service
- domain: {도메인}
- id: {PREFIX}-{DOMAIN}-{번호}
- source: {LLD 문서명} Section {번호}

## 수정 대상 파일
- {Service.java} (수정|신규)
- {ServiceImpl.java} (수정|신규)

## dependsOn

```yaml
dependsOn:
  - spec_id: {PREFIX}-{DOMAIN}-{번호}
    shared_files: ["{Entity.java}"]
    reason: "{엔티티 모델 완성 후 서비스 구현 가능}"
```

## 관련 정책
- POLICY-{DOMAIN}-001 ({정책명}) — {관련 조항}

## 관련 Spec
- {PREFIX}-{DOMAIN}-{번호} ({선행 model Spec})
- {PREFIX}-{DOMAIN}-{번호} ({이 서비스를 사용하는 usecase Spec})

## 관련 모델
- 주 모델: {모델명} — {주요 필드 목록}

## 개요
{서비스의 책임과 역할. 1~3문장.}

## 서비스 책임
- {이 서비스가 담당하는 비즈니스 규칙 1}
- {비즈니스 규칙 2}

## 메서드 설명
- **{메서드명}**: {역할 설명}. {파라미터}를 받아 {반환값}을 반환한다.
- **{메서드명}**: {역할 설명}.

## 입출력 정의
- **{메서드명}**: 입력 — {파라미터 설명}. 출력 — {반환값 설명}.

## 에러 처리
- {에러 상황}: {처리 방식}

## 검증 조건
- {조건 1}
- {조건 2}

## 테스트 시나리오

### TC-{DOMAIN}-{번호}-01: {정상 동작 검증} ({레벨})
- **Given**: {전제 조건}
- **When**: {트리거}
- **Then**: {기대 결과}

### TC-{DOMAIN}-{번호}-02: {에러 처리 검증} ({레벨})
- **Given**: {에러 조건}
- **When**: {트리거}
- **Then**: {에러 처리 결과}
