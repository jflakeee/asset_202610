# Trailwood 내부 검토 통합팩 v0.21

이 패키지는 판매 승인 전 검토본이다. 원설계의 42원형 × A/B, 84개 ID에 해당하는
LOD0 후보를 모두 생성했다. ID와 파일 존재가 아트 승인이나 전체 기능 완성을 의미하지 않는다.

## 정확한 수량

| 구분 | 수량 | 설명 |
|---|---:|---|
| 원설계 후보 | 84 | 나무12·바위12·식생12·숲소품12·목재경계20·석재경계16 |
| 이전 이름의 자연물 | 8 | 호환성을 위해 보존; 원설계 수량에 중복 포함하지 않음 |
| 확장 소품 | 12 | 표지판·상자·디딤돌·계단·벤치·테이블 |
| 전체 고유 LOD0 | 104 | 84+8+12 |
| LOD1 | 4 | 기존 바위2·나무2 |
| 보조 끝 기둥 | 1 | 모델 수량에서 제외 |
| 독립 GLB | 327 | (104+4+1)×Moss/Dry/Dusk 3테마 |

## 열어보기

- Godot: trailwood_godot/project.godot → Full model catalog. 104종을 Previous/Next로 비교하고 테마를 변경한다.
- Boundary physics examples 버튼: 폐회로4·문 닫힘/90도 열림2·경사3, 총9개 예제를 전환한다.
- 기존 보행/LOD 데모와 소품20종 갤러리도 유지했다.
- 엔진 공용 GLB: standalone_assets/<테마>/models/. PNG 팔레트는 파일에 내장된다.
- Blender: creation/blender_sources_output/Trailwood.blend. 원설계84종의 편집 가능한 메시·UV·재질·소켓을 담았다.
- Blender 파일은 GLB를 가져와 구성한 편집본이다. Geometry Nodes나 생성 파라미터 수정자 원본은 아니다.
- 썸네일84개·중립 비교 이미지6개·CSV: creation/review_media_output/.
- 조립 예제6개: creation/boundary_examples_output/의 scenes JSON과 previews PNG.
- 원설계 ID 추적표: creation/DESIGN_STATUS.md.
- 체험판8종 내부 검토 후보: creation/release_controls_output/trial_review/.
- 승인 연결·허용목록 검사 사용법: creation/RELEASE_CONTROLS.md.

## 구현 및 검사

새 후보78종(목재18·석재16·자연물44)을 추가했다. A/B는 기하 구조가 다르며 색상만 바꾼 복제본이 아니다.
모든 모델은 자체 절차적 생성 코드와 팔레트로 제작했고 외부 무료/유료 에셋의 메시·텍스처를 입력으로 쓰지 않았다.

327개 GLB 규격 오류·경고0, 3테마 기하·소켓 불변, 새 폴더에서15단계 전체 재생성 바이트 일치를 검사했다.
Godot4.5 헤드리스에서104종×3테마 로드·재질 연결·충돌체 생성을 검사했다.
기존20배치 보행/LOD/충돌 검사도 다시 통과했다. 이 검사는 GPU 렌더·실기기 성능 검사가 아니다.

LOD1의 네 시점256px 실루엣 IoU는 바위2·나무2 모두0.95 이상이다.
침엽수형 나무 LOD1은138→184 triangles로 수정해 최소IoU를0.9403→0.9860으로 개선했다.
기존93개 테마GLB 중 이 모델의3테마만 의도적으로 변경됐고 나머지90개는 동일하다.
전체 모델의 LOD1/2 정책은 미완료다. 자세한 수치는 creation/lod_iou_output/report.json을 확인한다.

경계 예제6개는15개 연결점의 위치·반대 방향·스케일 미변경을 검사했다.
7m 분할,2.13m 잔여 처리,90도 변환,0m 오류,15도 허용/16도 수동 전환은
creation/boundary_assembly_report.json에 검사 범위를 기록했다.
v0.18에는 실제 GLB 소켓을 사용한 목재/석재 좌우 폐회로4개와32개 연결 검사가 추가됐다.
closed_boundaries_output에서 소켓 검사 결과를 확인한다. v0.19는9개 예제를 Godot에서 실제 로드하고
반지름0.25m·높이1.6m 캐릭터를120물리프레임씩 전진시켰다. 문 닫힘은 차단,90도 열림은 통과했다.
폐회로4개와경사3개는 각1개 검사 지점에서 차단됐고, 모두 바닥 접촉을 유지했다.
자세한 최종좌표·실행버전·입력해시는 trailwood_godot/boundary_engine_validation.json에 기록했다.
v0.20은4개 폐회로의32개 모듈 연결점 주변과16개 코너 굴곡부에704개 캡슐 이동 경로를 배치했다.
시작 위치가 충돌체와 겹친96개는 합격으로 세지 않고 제외했다. 유효608개는 모두 차단됐다.
소켓 주변은중심과전후0.2m에서양방향/대각선, 코너굴곡은45도간격8방향으로 검사했다.
빈 공간 통과 및 충돌마스크를 끈 동일경로 통과도 확인했다. 이 결과는반지름0.25m·높이1.6m캡슐의
유한개 경로 검사이며 모든 접근각·더 작은 캐릭터·동적 문 작동·GPU렌더는 미검증이다.
slope_examples_output에는 수직 기둥과 새 경사 레일0/±15도 GLB3개가 있다.
이 예제 파생물은327개 본체GLB·104종 수량에서 제외한다. ±16도는 거부한다.
gate_path_output에는7.6m 경로의2m레일+1.6m문틀+4m레일 예약계획과7.73m 잔여처리가 있다.
예약구간 중첩·범위초과·음수·길이0 입력을 거부한다. 문 작동 애니메이션은 없다.

## 편집·충돌 계약

GLB는 미터 단위Y-up, 생성 소스·충돌 명세는Z-up이다. 변환은(x,z,-y).
팔레트 UV는32개 색상 셀의 중심을 샘플링하며 일반 텍스처 페인팅용 펼침UV가 아니다.
충돌체는 GLB 내장 물리가 아니라 JSON descriptor로 제공한다.
경계는 시작 기둥을 소유하고 끝 기둥은 제외한다. 열린 끝에는 POST/END를 추가한다.
문짝은 경첩 피벗의 정적 모델이며 문 작동 애니메이션은 없다.
부품별 충돌체는 배치 수에 따라 비용이 커질 수 있어 실기기 측정과 단순화가 필요하다.
신규 식생의 바람 동작은 검증하지 않았으며 전체 카탈로그 뷰어에는 바람을 적용하지 않는다.
기존 식생4종 갤러리만 선택적 Godot 바람 셰이더를 제공한다.

## 아직 완료되지 않은 항목

- 사람이 수행하는 아트 승인 및 형상·팔레트 해시와 결합된 승인 기록
- GPU 조명·그림자·바람·LOD 전환과 Android/iOS 성능 검사
- 전체 모델 LOD 정책, LOD2, 예외 승인
- 더 작은 캐릭터·추가 접근각·동적 문 작동 및 임포트/재임포트 수락시험 전체
- 판매 이용조건·최종 provenance 검토·체험판8종의 실제 승인 및 공개 배포 구성
- 로컬 승인 연결 검사의 실제 검토 기록 연결·검토자 신원 확인 및 전체 판매용 출고 절차

creation/release_gate_report.json은 내부 검토 가능 여부와 판매 가능 여부를 분리한다.
이 팩은 판매 ZIP이 아니며 내부 생성 코드가 포함된다. 판매 등록·공개는 수행하지 않았다.

## 재생성

creation/REBUILD_README.md의 고정 의존성으로 python rebuild_all.py --out 새폴더를 실행한다.
기존 모델 입력 복사 없이 전체327개GLB를 재생성한다. Blender 파일과 썸네일·예제는 각각의
별도 생성 스크립트와 문서를 사용한다. 다른OS/의존성 버전의 바이트 동일성은 별도 검증 대상이다.

신규 예제는 생성기 build_closed_boundaries.py, build_slope_examples.py, gate_path_planner.py로 재생성한다.
먼저 전체 재생성으로 원본 models 출력 폴더를 준비하고, 신규 스크립트와 build_boundary_examples.py·boundary_assembly.py를
재생성된 creation 폴더에 복사한 뒤 그 폴더에서 실행한다. build_boundary_runtime.py는 신규 예제를 Godot의data/boundary_lab.json과boundary_models로 연결한다.
런타임 내보내기는 전체카탈로그가 먼저 필요하므로 build_catalog.py 실행 후 수행한다.
엔진 검사 명령: godot --headless --path ../trailwood_godot res://boundary_lab.tscn -- --boundary-test.
검사결과는user://boundary_test.json에 저장된다. 검토팩의 보고서는 입력파일SHA-256까지 포함한다.

v0.21은 P001(승인없음),P002(승인해시불일치),K001(허용목록밖파일/경로/링크),
K002(체험판목록/누락/크기/해시)를 검사한다. 실제8종은모두PENDING이므로검사에서P001로차단된다.
시험용 승인 기록은 메모리에서만 사용하고 실제 승인 결과로 저장하지 않았다.
체험판 후보에는 Moss8개GLB와검토용README/manifest만 있으며 최종 배포 라이선스는 미확정이다.

## v0.22 — 84종별 제작 근거 및 LOD 기록

creation/asset_records_output/REVIEW_QUEUE.md에서 모델별 후속 작업을 확인한다.
asset_records.json은 실제 테마 파일의 해시·삼각형·정점·재질·이미지·경계,
소켓·충돌체와 제작 근거 경로를 연결한다. 입력이나 기록이 달라지면 내부 검토 포장도 차단한다.
LOD1은 4종, LOD2는 0종이다. 미제공 LOD는 구현 또는 사유를 기록한 예외 검토가 필요하다.
78종은 포장된 모델별 제작 근거가 연결되며 초기 6종은 모델별 근거 보완 대상으로 남긴다.
기록된 근거는 작성자·권리·입력 허용목록 승인에 해당하지 않는다. 사람의 아트 승인은 모두 대기다.
재생성 순서: source_manifest.json의 실제 소스 해시 갱신 → build_asset_records.py →
release_controls.py → release_gate.py → package_review.py. GPU·모바일 검사는 아직 수행하지 않았다.

## v0.23 — 초기 6종 제작 근거 보완

위 v0.22의 6종 근거 누락은 이번 버전에서 해소했다. build_initial_evidence.py가 현재 생성기로
바위 2종·나무 2종·목재 레일 2종을 다시 생성하고 3개 테마 총 18개 GLB를 바이트 단위로 비교한다.
84종 모두 모델별 recipe·원본 메시 기록·제작 근거가 연결된다. 초기 6종 기록은
creation/initial_evidence_output에 있으며 기록 검증 시 재생성과 파일 비교를 다시 수행한다.
이는 현재 재현 가능성을 확인한 결과다. 과거 작성자·제작일·권리 승인이나 아트 승인을 증명하지 않는다.
재생성 순서는 소스 해시 갱신 → build_initial_evidence.py → build_asset_records.py →
release_controls.py → release_gate.py → package_review.py이다. LOD 제공 수는 이전과 같다.
