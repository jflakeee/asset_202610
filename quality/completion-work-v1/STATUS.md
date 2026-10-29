# 전체 설계 작업 현황 — 2026-10-29

범위: 원설계 숲·경계84종과 최근 자원/보상6종을 별도 관리한다. 파일 존재를 미술 승인으로 계산하지 않는다. 전체 완료가 아니다.

## 이번에 직접 실행한 결과

- 소스 재생성15단계 성공. 후보104종/테마 GLB327개, 기준 해시와 동일.
- GLB327개 공식 검증 오류·경고0. 각 결과에 파일 SHA-256 기록.
- 경로·닫힌 경계·경사·문 예약·변경 감지·84종 근거 목록·내부 게이트 검사 성공.
- 미완료 상태에서 판매 게이트 종료코드2로 차단되는 음성 대조 성공.
- 원설계84종의3테마 위치/인덱스/UV/소켓 노드 동일성 검사 성공.
- 보조6종 투명 아이콘18장과 아틀라스 생성, 알파/여백/영역 동일성 검사 성공.

## AT01–AT16

|항목|상태|확인 범위/남은 조건|
|---|---|---|
|AT01|PASS|P0 six unique recipes generate successfully; recorded recipe/provenance hashes verified; not human authorship approval|
|AT02|PASS|Five actual2m modules plus terminal post form10m; no duplicate posts; endpoint vertices within1mm of following mesh surface|
|AT03|PASS|Actual 1/2/4m 7m socket chain|
|AT04|PASS|2.13m residual preserved without scale|
|AT05|PASS|Open10m assembly has one terminal; four actual closed loops have none; unique logical post ownership checked, not character physics|
|AT06|PASS|Actual exported sockets, normals and collider descriptors rotated90deg|
|AT07|PASS|Two fresh source builds:327 byte-identical GLBs,84 normalized geometry hashes and bounds match|
|AT08|PASS|Six P0 recipes reversed per generator; GLB and source hashes identical|
|AT09|PASS|327 original-v1 palette GLBs pass required preflight; missing/corrupt PNG M001 and external URI X001 blocked before existing gate|
|AT10|PASS|84 canonical models positions/indices/UV/nodes identical across3 themes|
|AT11|PASS|Original P0 six GLBs newly imported in Godot4.7.2 headless; textures/counts/bounds/source vertices verified; no unexpected collision objects|
|AT12|NOT_RUN|Only4 LOD1 pairs; full84 LOD1/2 policies pending|
|AT13|PASS|Synthetic approval fixture rejects changed content hashes P002; no real approvals issued|
|AT14|PASS|Trial staging extra file/mutation/missing/symlink/path controls reject; sales-wide staging pending|
|AT15|NOT_RUN|Approved84 thumbnail/document exactness pending|
|AT16|PASS|Zero-length and +/-16deg rejection checked|

NOT_RUN은 미실행 또는 일부 증거만 있는 상태이며 합격으로 세지 않는다. 이번 PASS도 명시한 fixture/범위에 한정한다.

## 아직 구현·검토할 항목

1. 원설계84종의 LOD1/2 또는 근거 있는 개별 생략 정책. 현재 LOD1은4종뿐이다.
2. 원설계6예제의 실제 통행/접촉·엔진 물리 검사와 미술 검토.
3. 원설계AT12/15의 미실행 부분.
4. 모델별 제작자/도구/날짜/참고 목적/AI 보조 단계 및 입력 허용목록 검토.
5. 구매자용 문서·체험8종/본편 허용목록·최종 판매 조건. 내부 생성 코드를 판매 ZIP에 넣지 않는다.
6. 사람의 미술 승인, 실제 GPU 화면, Android/iOS 기기 측정. 테스트 성공으로 대체할 수 없다.

## 새 저장소에서 재현

기존 저장소에는 생성 산출물이 생략되어 일부 검사만 바로 실행하면 실패한다. 폐기 가능한 저장소 사본에서 다음 순서로 진행한다.

```
python creation/rebuild_all.py --out /new/empty/rebuild-folder
python quality/completion-work-v1/prepare_checkout.py /disposable/repository /new/empty/rebuild-folder
node quality/completion-work-v1/validate_catalog.cjs /path/to/gltf-validator /disposable/repository/creation
python quality/completion-work-v1/run_design_checks.py /disposable/repository --commit <checked-commit>
python quality/completion-work-v1/check_theme_invariance.py /disposable/repository
```

공식 validator2.0.0-dev.3.10과 Python NumPy/SciPy/Pillow/Matplotlib가 필요하다. prepare는 생성 폴더만 복원하고 기준 해시/소스가 다르면 중단한다. 실제 승인 기록을 작성하거나 판매 게이트를 우회하지 않는다.
