# 체험판 선별과 승인 연결 검사

release_controls.py는 원설계의8개ID를 Moss LOD0로 선별한다. 결과는
release_controls_output/trial_review/이며 공개 체험판이 아닌 내부 검토 후보이다.
최종 이용조건을 임의로 작성하거나 승인된 것으로 표시하지 않는다.

## 실행

전체 모델과 theme_output, source_manifest.json이 준비된 creation폴더에서:

```sh
python release_controls.py
python release_controls.py --check-approvals release_controls_output/approval_requests.json
```

두 번째 명령은 기본 PENDING 기록에서 종료코드2와 P001을 반환하는 것이 정상이다.
검토자는 approval_requests.json의 복사본을 외부에서 검토해 실제 판정·이름·시간대 포함 시각·
preview profile·지적사항을 기록할 수 있다. 원본 요청파일은 재생성 시 갱신되므로
실제 검토 기록은 별도 approval.json에 보관하고 --check-approvals로 검사한다.
도구는 승인 주체의 신원을 인증하지 않는다. 로컬 판정 기록과 현재 내용의 연결만 검사한다.
검사에 통과해도 판매용 전체 품질·라이선스·출고 검사를 대신하지 않는다.

## 오류와 보호 범위

- P001: 승인 없음, PENDING, 대상 ID/검토정보 부족.
- P002: geometry/palette/recipe/export 해시 중 하나라도 변경됨.
- K001: 허용되지 않은 파일, 상위 경로 탈출, 심볼릭 링크.
- K002:8종목록·테마·검토상태·파일크기·해시 불일치 또는 누락.

기하 해시는1µm 양자화 좌표·면별 팔레트 슬롯과 정규화한 삼각형을 사용한다.
삼각형 순서는 무시하지만 winding은 유지한다. export해시도 별도로 연결한다.
recipe해시는 사용 가능한 레시피와 전체 생성 소스 목록을 보수적으로 묶으므로
일부 다른 모델의 생성 코드 변경도 재검토를 요구할 수 있다.

검토 후보를 다시 만들 때 기존 staging이 오염돼 있으면 중단한다. 알 수 없는 파일을
조용히 삭제하거나 새 허용목록에 자동 편입하지 않는다. 음성시험은 임시폴더와
메모리 안의 TEST_FIXTURE_ONLY 기록에서만 수행하며 실제 승인 결과로 저장하지 않는다.

이 단계는 자동 출판·판매 ZIP 생성을 하지 않는다. 전체 통합팩은 내부 검토용이다.
