# 판매용 독자 3D 에셋 팩 상세설계 v1.1

작성: 2026-10-18 · 상태: 구현 착수용 상세설계 · 제품명과 가격은 내부 가안

v1.1 변경: 15~27절에 구체적인 모듈 계약, 42원형 목록, 첫 6모델 레시피, 기하 생성 알고리즘, 팔레트/LOD/충돌체 처리, 검증 사례와 단계별 완료 조건을 추가했다. 앞부분과 세부 규칙이 충돌하면 15절 이후가 우선한다. 모든 ‘합격’ 수치는 설계 기준이며 아직 수행한 테스트 결과가 아니다.

## 1. 제품 결정

첫 제품은 **Trailwood — Modular Forest & Boundaries**(가칭)로 정의한다. 모바일 탑다운 RPG·생존 게임을 만드는 개발자가 숲과 경계를 빠르게 조립할 수 있는 정적 로우폴리 팩이다. 브랜드명 사용 가능성은 아직 확인하지 않았으며 출시 전 확정한다.

핵심 가치는 ‘새로운 모델을 무한 생성’이 아니라 **맞물리는 부품, 일관된 외관, 완성된 재질, 재현 가능한 구성**이다. 공개된 타사 팩의 파일을 편집·리토폴로지·재색칠해 판매하는 방식은 사용하지 않는다. 분석한 무료 팩은 기술적 비교 자료로만 남긴다.

v1 판매물은 완성된 정적 모델과 편집용 Blender 소스다. 내부 생성기와 경로 배치 도구는 제작용으로 유지하며 고객용 플러그인 판매는 v2 이후 별도 결정한다. 이 구분으로 모델 팩과 소프트웨어의 유지보수 부담을 분리한다.

### 범위

| 구분 | v1 결정 |
|---|---|
| 구매자 | 모바일 탑다운 RPG·생존 게임 개발자 |
| 시각 방향 | 둥근 수관, 쐐기형 암석, 오프셋 기둥 장식, 굵은 면 분할, 차분한 색상 |
| 핵심 포맷 | GLB + PNG + .blend |
| 초기 검증 엔진 | Godot 4 계열 한 버전으로 고정 후 테스트 결과 기록 |
| Unity | 원본 포맷 제공과 네이티브 패키지 지원을 구분; URP 어댑터는 후속 범위 |
| 미포함 | 캐릭터, 리깅, 전투 애니메이션, 게임 코드, 동적 바람 셰이더, 고객용 생성기 |
| 첫 판매 채널 | itch.io를 우선 후보로 설계; 업로드·출시는 본 작업 범위 밖 |

## 2. 독자 제작과 이력 원칙

원형은 기본 도형·자체 곡선·자체 알고리즘에서 새로 만든다. 다운로드한 메시·UV·텍스처·소스 코드·프리팹은 빌드 입력으로 허용하지 않는다. 타사 이름, 제품 설명, 아이콘, 데모 장면 배치를 재사용하지 않는다.

제작 프로젝트에는 `source/`, `recipes/`, `palettes/`만 입력 허용 목록으로 둔다. 기존 `research/`는 판매 빌드 경로에서 제외한다. 타사 원본 해시와 동일한 파일을 탐지하는 것은 보조 검사이며, 해시 불일치가 독창성을 증명하지는 않는다. 스케치·원형 수정 이력·코드 커밋·승인 기록으로 제작 경위를 함께 남긴다.

각 원형에는 작성자 또는 도구, 작성일, 코드 버전, 참고 자료 URL과 참고 목적, 수동 편집 내용, AI 사용 여부를 기록한다. 절차적 생성과 생성형 AI 사용을 같은 의미로 표시하지 않는다. 코드 작성 보조·컨셉 이미지·출고 텍스처 등 실제 사용 단계를 기록하고 출시 당시 플랫폼 분류에 맞춰 고지한다. ‘완전 수작업’이나 ‘독점 저작권 보장’ 같은 검증하지 않은 표현은 사용하지 않는다.

## 3. 상품 구성과 수량 정의

모델 수는 **승인된 독립 실루엣/구조를 가진 LOD0 모델**로 센다. LOD, 컬러 테마, 포맷 복사본, 배치 프리셋은 모델 개수에 더하지 않는다. 아래 수치는 제작 목표이며 아직 만들어진 수량이 아니다.

| 카테고리 | 원형 수 | 승인된 형태 변형/원형 | 출고 LOD0 모델 | 구성 기준 |
|---|---:|---:|---:|---|
| 나무 | 6 | 2 | 12 | 둥근 수관 2·층형 수관 2·고목 2 |
| 바위 | 6 | 2 | 12 | 낮은 바위·선돌·무리 바위 등 |
| 덤불·풀 | 6 | 2 | 12 | 덤불 3·풀 군집 3 |
| 숲 소품 | 6 | 2 | 12 | 그루터기·통나무·가지 무리 각 2원형 |
| 목재 경계 | 10 | 2 | 20 | 직선 3·코너 2·끝단 2·기둥 1·문틀 1·문짝 1 |
| 석재 경계 | 8 | 2 | 16 | 직선 3·코너 2·끝단 2·기둥 1 |
| 합계 | 42 | 2 | **84** | 형상 변형 기준 |

색상 테마는 Moss/Dry/Dusk 3종으로 공유 팔레트만 교체한다. 모델 수는 84개이며 252개로 홍보하지 않는다. 문짝은 별도 피벗을 가진 정적 모델이며 작동 애니메이션은 포함하지 않는다.

출고 추가물: 조립 예제 6종, 동일 파일을 사용한 검증용 장면 1종, 중립 조명 카탈로그 장면, PNG 썸네일 84장, 모델 목록 CSV, README·변경 이력·이용 조건. 조립 예제 6종은 숲길·소형 야영 경계·석벽 공터·목재 관문·폐허 경계·작은 숲섬이다.

무료 체험판은 본편의 8모델 부분집합(나무2/바위2/풀1/목재2/석재1)과 1팔레트로 구성한다. 무료와 유료의 모델 품질 규격은 같게 유지한다. 별도 생성물 숫자를 추가하지 않는다.

## 4. 시각 규격

- 카메라: 지면을 내려다보는 45~60도 시점 및 일반 3인칭 시점에서 확인한다.
- 비율: 현실적 비율을 바탕으로 기둥과 수관의 큰 형태를 강조한다. 세부 노이즈로 수량을 채우지 않는다.
- 팔레트: 테마당 32색, 색상 슬롯 의미를 고정(나무껍질·단면·잎·돌·이끼 등). 팔레트 v1에서는 UV 슬롯 번호를 변경하지 않는다.
- 텍스처: 자체 제작한 256×256 PNG 한 장/테마. 셀 경계 번짐 방지 여백과 밉맵 검사를 적용한다.
- 기본 재질: 일반 PBR의 base color·roughness 사용, 금속성 0. 투명 재질·양면 렌더는 기본적으로 쓰지 않는다. 풀도 저비용 입체 메시로 제작한다.
- 스타일 승인은 실제 게임 크기의 48~96px 투영 크기와 확대 이미지에서 각각 수행한다. 작은 화면에서 서로 구별되지 않는 변형은 폐기한다.

## 5. 좌표·모듈·파일 규격

| 항목 | 제작 규격 | 검사 |
|---|---|---|
| 단위 | 1단위=1m | 1m 큐브 기준 장면 |
| 축 | Blender Z-up → GLB Y-up 변환 한 번 | 변환 후 위/앞 방향 테스트 |
| 피벗 | 자연물 지면 중앙, 경계 시작 연결점, 문짝 경첩 | 피벗 마커와 접지 검사 |
| 직선 길이 | 1m/2m/4m | 연결 소켓 간 거리 오차 ≤1mm |
| 스냅 | 0.25m 보조 격자 | 복제·회전 후 연속 배치 |
| 소켓 | `SOCKET_START`, `SOCKET_END`, 문 `HINGE` | 위치·접선 방향 함께 저장 |
| 변환 | 메시 객체 scale=1, 비정상 반전 없음 | 음수 스케일·NaN·Inf 차단 |
| 이름 | `TW_<category>_<family>_<variant>_LOD<n>` | ID 유일성·허용 문자 검사 |
| 출고 단위 | 모델별 LOD0/1/2 별도 GLB | GLB 자체 자동 LOD를 보장하지 않음 |
| 텍스처 | GLB에 기본 테마 포함 + 외부 대체 PNG | 새 폴더에서도 이미지 누락 0 |

공유 팔레트를 써도 GLB를 각각 임포트하면 재질이 중복될 수 있다. Godot 예제에서는 하나의 공유 머티리얼로 교체하고, 별도 포맷 사용자는 교체 절차를 문서로 제공한다. 모델당 재질 하나를 전체 장면 한 드로콜로 표현하지 않는다.

## 6. 생성 시스템 구조

`원형 규칙 → recipe 검증 → 시드 기반 형상 생성 → 사람의 형태 승인 → UV/재질 → LOD/충돌체 → GLB export → 자동 검사 → 엔진 검사 → 패키징`

| 모듈 | 입력 | 출력 | 실패 처리 |
|---|---|---|---|
| RecipeValidator | JSON recipe | 유효 파라미터 | 범위 밖이면 생성 중단 |
| GeometryBuilder | 원형/시드/규칙 | 기본 메시 | 퇴화면·자가 교차 후보 표시 |
| PaletteMapper | 재질 영역 ID | UV/머티리얼 | 누락 영역 차단 |
| VariantSelector | 후보 모델 | 승인 목록 | 실루엣 중복은 재생성 또는 폐기 |
| LODBuilder | 승인 LOD0 | LOD1/LOD2 | 자동 축소 실패 시 수동 단순화 |
| ColliderBuilder | 유형/치수 | 박스·캡슐 또는 단순 볼록체 | 장식물은 no-collision 명시 |
| Exporter | 승인 모델/팔레트 | GLB·메타데이터 | 깨진 참조/미지원 재질 차단 |
| Validator | export 파일 | JSON/CSV 검사 결과 | 오류가 하나라도 있으면 출고 제외 |
| Packager | 승인 manifest | 판매 ZIP·체험 ZIP | manifest 외 파일 유입 차단 |

도구 후보는 Blender Python + Geometry Nodes이며 특정 버전은 구현 시작 시 설치된 안정 버전으로 고정한다. v1에서는 런타임 생성 없이 편집 단계에서 생성·검사·굽기를 수행한다. 원형 수동 편집을 허용하되 변경 시 원형 버전과 파생 모델을 함께 갱신한다.

### 재현성

난수는 카테고리·모델 ID별 독립 시드로 분리해 목록 순서 변경이 다른 모델을 바꾸지 않도록 한다. `generator_version`, `recipe_version`, `Blender_version`, `palette_version`을 고정한다. 같은 환경에서는 메시 지표와 정규화한 지오메트리 해시가 같아야 한다. export 메타데이터 차이 때문에 ZIP 바이트 해시가 항상 같다고 보장하지 않는다.

### recipe 예시(설계용)

```json
{
  "asset_id": "TW_FENCE_RAIL_A02",
  "recipe_version": "1.0.0",
  "generator_version": "0.1.0",
  "family": "offset_rail",
  "seed": 42002,
  "parameters": {
    "length_m": 2.0,
    "height_m": 1.1,
    "post_width_m": 0.14,
    "rail_count": 2,
    "damage_ratio": 0.15
  },
  "palette_id": "TW_MOSS_01",
  "lod_triangle_targets": [600, 300, 120],
  "collision": "compound_boxes",
  "approval_status": "draft"
}
```

시드만 변경한 모델은 자동 승인하지 않는다. 파손은 외형뿐 아니라 연결점과 통행 가능 영역에 영향을 줄 수 있으므로 기능 태그 `decorative_damage`/`passable_gap`을 구분한다.

## 7. 생성기별 알고리즘 요구

### 자연물

나무는 줄기 곡선·굵기 감소·가지 분기·수관 덩어리를 별도 규칙으로 만든다. 저사양용은 수관을 면 덩어리로 구성하며 잎 카드에 의존하지 않는다. 바위는 기본 다면체의 제한된 변형과 지면 절단으로 만들고 작은 노이즈만으로 다른 모델이라 판단하지 않는다. 풀·덤불의 군집은 밀도 상한을 고정한다.

### 경계 부품 및 내부 배치 도구

경로를 일정 구간으로 분해하고 4m→2m→1m 순서로 채우되, 잔여 길이는 끝단 조정 또는 사용자 선택으로 처리한다. 전 구간을 무조건 늘려 텍스처와 기둥 간격을 왜곡하지 않는다. 급한 코너는 전용 코너 부품으로 전환한다.

지형 높이는 기둥 위치에서 샘플링한다. 수직 기둥+단차형 레일과 경사형 레일을 선택할 수 있게 한다. v1 시험 범위는 평지와 15도 이내 경사이며, 초과 구간은 경고 후 수동 조립한다. 문 주변은 파손·랜덤 누락 금지 영역이다. 시드 변형이 소켓 위치를 바꾸지 않게 한다.

내부 도구의 기능은 승인된 부품 ID 선택, 경로 배치, 높이 맞춤, deterministic seed, 결과 굽기, 재생성 전 이전 결과 보존까지다. 고객에게 이 도구가 제공되는 것처럼 상품 페이지에 표시하지 않는다.

## 8. 품질 예산과 출고 기준

아래 수치는 초기 설계 목표이며 실제 성능 보장값이 아니다.

| 유형 | LOD0 최대 삼각형 | LOD 정책 | 충돌체 |
|---|---:|---|---|
| 나무 | 1,200 | 약 50%/20%부터 시작, 실루엣 보존 | 줄기 캡슐 |
| 바위 | 800 | 약 50%/20% | 단순 볼록체 또는 박스 |
| 풀·덤불 | 400 | 작은 군집은 거리 제거 가능 | 기본 없음 |
| 숲 소품 | 800 | 약 50%/20% | 용도별 단순체 |
| 일반 경계 | 1,000 | 약 50%/20% | 복합 박스 |
| 문틀·코너 | 1,500 | 예외 사유 기록 | 복합 박스 |

LOD 비율은 목표이지 합격을 대신하지 않는다. 얇은 기둥·연결점·문 경첩이 사라지면 실패다. 아주 작은 메시를 불필요하게 3벌로 만들지 않고 LOD 생략 사유를 manifest에 기록한다.

### 자동 출고 차단 조건

- 미승인 모델, 출처 이력 누락, manifest 외 파일, 중복 asset_id.
- 누락된 텍스처/외부 경로, UV 영역 미할당, 잘못된 축/단위, 음수 스케일.
- 비유한 좌표, 면적 0의 삼각형, 잘못된 인덱스, 의도하지 않은 뒤집힌 면.
- 연결점 허용 오차 초과, 파일별 재질 2개 초과(명시 승인 없는 경우), 삼각형 예산 초과.
- 문서 모델 수와 실제 manifest 수 불일치, 무료 체험판에 유료 전용 파일 유입.

열린 메시 자체는 무조건 오류로 분류하지 않는다. 지면에 묻히는 바닥 등 허용된 열린 경계는 원형 규칙에 기록한다.

### 사람이 확인할 항목

각 모델 정면·측면·탑다운, 팔레트 3종, 밝은/어두운 배경, LOD 전환에서 읽히는 형태, 파손의 자연스러움, 타사 고유 외형·장식과 혼동 가능성. 과도하게 유사한 후보는 기하 수치를 통과하더라도 반려한다.

### 엔진/기기 시험

첫 엔진의 정확한 버전·렌더러·임포트 설정을 기록한다. 100/500/1,000개 오브젝트로 구성한 고정 시드 테스트 장면에서 빈 장면 대비 CPU/GPU 프레임 시간, p50/p95, 드로콜, 메모리, 로딩 시간을 측정한다. 장치 모델·OS·해상도·그림자 설정·워밍업 60초·측정 120초를 함께 기록한다. 미측정 장치에 대한 FPS 보장은 하지 않는다. ‘모바일 최적화 완료’는 최소 실제 Android 및 iOS 각 1기기 시험 후에만 사용한다. 장치 미확보 시 ‘저폴리곤’과 검증된 기술 사양만 표시한다.

## 9. 판매 패키지

```text
Trailwood_v1.0/
  README.md
  LICENSE.txt
  CHANGELOG.md
  manifest.csv
  models/glb/lod0/
  models/glb/lod1/
  models/glb/lod2/
  textures/{moss,dry,dusk}.png
  source/Trailwood.blend
  examples/
  previews/
  docs/import-guide.md
  docs/specifications.md
```

내부 recipe·생성 코드·타사 연구 자료·계정 정보·절대 로컬 경로·임시 캐시·자동 저장 파일은 판매 ZIP에서 제외한다. `.blend`에 포함된 텍스처와 경로도 확인한다. 소스 제공은 모델 편집 소스 제공이며 생성기 코드 제공을 뜻하지 않는다.

썸네일은 실제 출고 모델과 재질을 렌더링해 만든다. 대표 이미지 1장, 전체 모델 시트, 와이어프레임, 세 가지 테마, 조립 예시, 실제 엔진 화면을 준비한다. 포함되지 않는 조명/후처리/엔진 기능은 설명한다. AI 컨셉 이미지를 완성 상품 스크린샷으로 사용하지 않는다.

## 10. 판매·지원 정책 설계

아래는 사업 운영 선택안이며 최종 계약 문구가 아니다. 출시 전 배포 플랫폼과 사용 범위에 맞춰 실제 이용 조건을 확정한다.

- 허용하려는 사용: 구매자의 상업·비상업 게임/영상/이미지 제작 및 프로젝트 내 수정.
- 제한하려는 사용: 원본 또는 변형 모델을 에셋 팩·다운로드 라이브러리 형태로 재판매/재배포.
- 팀 공유: 구매한 한 조직의 프로젝트 참여자 범위로 제한하는 안. 외주자 접근 종료와 파일 관리도 안내.
- 소유권 표현: 고객에게 독점 자산이라고 약속하지 않는다. 원형 소스와 사용권 범위를 구분한다.
- 무료 체험판에도 별도 명시된 조건을 동봉하며, 무료라는 이유로 CC0라고 표시하지 않는다.
- 버전: 호환되는 추가·수정은 minor/patch, asset_id 삭제·좌표/소켓 변경은 major 또는 신규 ID.
- 초기 지원 범위: 다운로드/파일 누락/표시된 엔진 버전의 임포트 문제. 개별 게임 구현과 사용자 개조 디버깅은 제외.
- 지원 응답 목표는 출시 후 실제 운영 가능한 일정으로 정한다. 무제한 업데이트나 평생 지원을 약속하지 않는다.

가격은 시장 확정값이 아닌 실험안으로 체험판 $0, 본편 $12~18을 검토한다. 모델·소스·예제·지원에 필요한 작업량을 산정한 후 확정한다. 원형 생성 도구를 내부에서 쓰는 가치를 고객용 도구 판매가격으로 포함시키지 않는다. 할인을 전제로 정가를 부풀리지 않는다.

## 11. 구현 백로그와 완료 조건

| 순서 | 작업 | 산출물 | 완료 조건 |
|---|---|---|---|
| P0 | 스타일·ID·팔레트 확정 | 스타일 보드·규격 | 탑다운/근접 예시 승인 |
| P0 | 독자 원형 6개 | 나무2·바위2·울타리2 | 타사 파일 입력 없이 생성·수정 기록 |
| P0 | Export/검증 최소 경로 | GLB 6개·검사 결과 | 새 폴더에서 재질 누락 0 |
| P0 | 엔진 수직 검증 | 소규모 조립 장면 | 축/피벗/소켓/색상 정상 |
| P1 | 자연물 24원형 | 48모델 후보 | 실루엣 승인 및 성능 예산 |
| P1 | 경계 18원형 | 36모델 후보 | 코너/문/경사 연결 검사 |
| P1 | LOD·충돌·3팔레트 | 최종 리소스 | 전환/접지/머티리얼 검사 |
| P1 | 6예제·기기 측정 | 예제·성능 기록 | 재현 가능한 시험 절차 |
| P1 | 상품 문서·이용 조건·이미지 | 판매 ZIP 초안 | 목록 일치·권리 이력·출시 체크 |
| P2 | 고객용 생성기/Unity 어댑터 | 별도 설계 | 수요와 유지보수 비용 평가 후 진행 |

계획용 작업량은 수직 검증 3~5일, 본 제작 8~12일, 최적화/엔진/패키징 5~8일로 총 16~25 작업일이다. 숙련 담당자 1명을 가정한 추정이며 장치 확보·브랜드 검토·고객 테스트 대기는 제외한다. 6모델 수직 검증 결과로 재산정한다.

## 12. 실패 시 조정

| 문제 | 대응 |
|---|---|
| 원형 6개에서 품질 불충분 | 수량 확대 중지, 스타일과 생성 규칙 수정 |
| 색상만 다른 변형이 많음 | 독립 모델 숫자를 줄이고 구조 변형 추가 |
| GLB 재질 누락 | 기본 테마 내장과 깨끗한 환경 임포트 검사 강화 |
| 자동 LOD가 형태를 훼손 | 원형별 수동 LOD/단순 원형 재생성 |
| 경사 배치가 불안정 | 도구는 내부 전용 유지, 평지 예제 먼저 출고 |
| 엔진 지원 부담 과다 | 검증된 한 엔진과 범용 포맷으로 한정 |
| 타사 원형/텍스처 혼입 | 해당 계열 출고 중지, 독자 입력에서 재생성 |
| FPS 목표 미달 | 배치 밀도·재질·그림자·컬링을 측정 후 조정 |

## 13. 출시 게이트

설계 완료는 판매 가능 상태가 아니다. 다음 조건을 모두 충족한 후 출시 여부를 결정한다.

1. 승인 LOD0 모델 84개와 문서 수량 일치.
2. 출처 기록 완비, 허용 입력만으로 빌드, 타사 파일 혼입 없음.
3. 새 환경에서 텍스처/소스/예제 정상, 검증 엔진 버전 명시.
4. 모바일 성능 문구는 실제 측정 범위 내에서 작성.
5. 실제 모델 기반 상품 이미지, AI 사용 과정에 맞는 분류, 이용 조건 확정.
6. 무료 체험판/유료 ZIP 구분, 새 구매자 관점의 다운로드·임포트 절차 검증.
7. 상품명·가격·지원 범위를 최종 확정한 후 게시.

## 14. 근거와 남은 검증

이 설계는 이전 대화의 무료 GLB 표본 140개 분석을 문제 발견 근거로 사용했다. 이 표본의 모델·텍스처·UV를 판매물로 재사용하도록 설계하지 않았다. 모든 수량·예산·제작 일정은 신규 제품의 계획값이다.

itch.io 공식 품질 가이드는 정확한 상품 설명, 오해를 유발하지 않는 이미지와 분류, 과도한 자동 생성 콘텐츠/소규모 변경의 반복 게시 회피, 생성형 AI 사용의 정확한 태그를 요구하는 항목을 포함한다. 출시는 단일한 검수된 팩으로 준비하고, 게시 직전에 최신 내용을 다시 확인한다.

공식 출처(2026-10-18 확인): https://itch.io/docs/creators/quality-guidelines

Blender 내보내기 세부 설정과 지원 엔진 버전은 구현 시 실제 설치 환경에서 검증한다. 본 설계 단계에서 모델 생성, 엔진 임포트, 모바일 벤치마크, 판매 등록은 실행하지 않았다.

## 15. 구현 경계와 주요 결정

### 15.1 이번 상세설계에서 고정한 사항

1. P0는 나무 2·바위 2·울타리 2, 총 6개의 독자 원형 검증이다. P1의 84모델 중 해당 원형의 A형이 되며 별도 상품 수량으로 추가하지 않는다.
2. 형상 생성은 Blender Python을 기준으로 하고, Geometry Nodes는 초기 필수 의존성에서 제외한다. 원형 수정과 디버깅을 코드/recipe 한 경로로 추적한다. 이후 노드 기반 제작을 도입해도 같은 출력 계약을 지킨다.
3. 고객용 패키지는 정적 메시 팩이다. Godot 예제의 재질·충돌·LOD 구성은 제공하지만 내부 생성 CLI와 경로 배치 코드는 포함하지 않는다.
4. 자동 생성 후보와 사람이 승인한 모델을 구분한다. 84개는 출시 목표이며, 미달 시 숫자를 숨기거나 비슷한 후보로 채우지 않고 제작 상태를 유지한다.
5. 핵심 GLB는 baseColor 텍스처를 내장한다. normal map·specular/ior 확장·압축 확장은 v1 필수가 아니다. 기본 파일을 단순하게 유지하고 엔진 압축은 어댑터 단계에서 처리한다.
6. 판매 ZIP은 타사 원본이 없는 새 staging 디렉터리에서 manifest 허용 목록으로만 구성한다. 연구 디렉터리 전체 복사와 파일 확장자만으로 수집하는 방법은 금지한다.

### 15.2 아직 구현 시 확정해야 하는 사항

| 결정 | 확정 시점 | 진행 가능한 기본값 |
|---|---|---|
| Blender/Godot 정확한 버전 | P0 시작 | 설치 후 `toolchain.lock.json`에 고정; 최신 버전 자동 추종 안 함 |
| 실제 브랜드명 | 상품 이미지 제작 전 | 내부 코드 `TW`, 공개 이름은 미확정 |
| 실기기 모델·지원 범위 | P1 성능 시험 전 | 데스크톱 임포트와 파일 검사는 먼저 수행 |
| 가격·이용 조건 최종본 | 출시 검토 | 기존 문서의 사업 가안 유지 |
| P0 미술 승인 | 6모델 미리보기 완성 후 | 본 상세 파라미터를 첫 후보로 제작 |

## 16. 내부 프로젝트 구조와 실행 계약

```text
trailwood_factory/
  pyproject.toml
  toolchain.lock.json
  schemas/{recipe,asset_manifest,approval,build_result}.schema.json
  config/{quality_profiles,render_profiles,engine_profiles}.json
  catalog/families.json
  recipes/{p0,release}/
  palettes/{moss,dry,dusk}.json
  provenance/                    # 원형 제작 이력
  approvals/                     # 파일 해시에 연결된 승인 기록
  src/trailwood/
    cli.py
    contracts.py
    random_streams.py
    generators/{tree,rock,vegetation,props,wood,stone}.py
    geometry/{rings,frames,hull,box,triangulate}.py
    materials/{palette,uv,assign}.py
    lod/{tree,rock,boundary}.py
    collision.py
    export/{gltf,blend,manifest}.py
    validate/{structure,geometry,sockets,materials,provenance}.py
    render/{catalog,contact_sheet,silhouette}.py
    adapters/godot.py
    packaging.py
  tests/{fixtures,unit,integration}/
  runs/<build_id>/{work,artifacts,reports,logs}/
  releases/<version>/
```

이는 예정 구조이며 코드가 구현되었다는 의미는 아니다. `src/config/schemas/toolchain.lock.json`은 실행 도구 입력이며, `recipes/palettes/provenance/승인된 자체 source`는 콘텐츠 입력이다. 두 종류를 모두 해시 목록에 기록한다. 임의 외부 파일을 `source`에 넣는 것만으로 승인된 입력이 되지는 않는다.

### 실행 인터페이스(향후 구현 명세)

| 명령 | 역할 | 외부 변경 |
|---|---|---|
| `tw validate-recipes --set p0` | recipe/schema/ID 검증 | 없음 |
| `tw build --set p0 --build-id <id>` | 새 실행 폴더에 후보 생성 | 새 로컬 파일만 생성 |
| `tw inspect --build-id <id>` | 수치·미리보기·오류 보고서 | reports만 생성 |
| `tw export-godot --build-id <id>` | 공유 재질·충돌·LOD 예제 생성 | 새 예제 폴더 |
| `tw package --build-id <id> --channel preview` | 검토용 묶음 | preview ZIP |
| `tw package --build-id <id> --channel release` | 승인된 모델만 판매 묶음 | release ZIP |

미술 승인은 별도 `approval.json`으로 입력한다. 생성기가 자신의 결과를 자동으로 `approved`로 변경하는 명령은 제공하지 않는다. 승인 주체가 사용자일 경우 미리보기와 평가 항목을 제시한 후 결과를 기록한다.

### 빌드 상태 전이

`PLANNED → VALIDATED → GENERATED → CHECKED → REVIEW_READY → APPROVED → EXPORTED → RELEASE_CHECKED → PACKAGED`

`CHECKED`는 형상과 원본 재질 검사, `RELEASE_CHECKED`는 내보낸 GLB·엔진·패키지 검사다. 각 단계에서 오류 발생 시 `FAILED`와 원인을 기록한다. 반려는 `REJECTED`로 남기고 수정 결과는 새 content revision으로 생성한다. geometry/UV/palette/LOD 변경은 관련 시각 승인을 무효화한다. 문서 오탈자만 고친 경우에는 해당 문서 검증만 다시 한다.

파일 저장은 `<asset_id>.tmp`에 완료 후 같은 파일시스템에서 rename한다. 단일 원자적 rename만 이용하며 여러 파일 전체가 원자적이라고 가정하지 않는다. `build_result.json`에 단계별 완료 체크포인트를 둔다. 기존 release 경로가 있으면 덮어쓰지 않고 실패한다. 중단된 work는 원인을 남긴 뒤 재사용 가능성 검사 후 재개한다.

## 17. 데이터 계약

### 17.1 Recipe

설정 JSON은 UTF-8, 거리 m, 각도 deg, 색상 sRGB hex로 입력한다. 실행 시 내부 각도는 rad로 변환한다. `additionalProperties=false`를 기본으로 하고, family별 `parameters`를 분리하여 잘못된 필드 이름을 즉시 검출한다.

| 필드 | 형식/제약 | 의미 |
|---|---|---|
| `schema_version` | `1.0.0` | 레시피 스키마 버전 |
| `asset_id` | `^TW_[A-Z]+_[A-Z0-9_]+_[AB]$` | 출시 자산 ID; LOD와 팔레트 제외 |
| `family_id` | catalog에 있는 값 | 원형 규칙 |
| `variant` | `A` 또는 `B` | 승인된 구조 변형 |
| `seed` | 0~4294967295 정수 | 원형별 기준 시드 |
| `generator_version` | SemVer | 생성 규칙 버전 |
| `palette_id` | `MOSS_01/DRY_01/DUSK_01` | 기본 preview 테마 |
| `parameters` | family별 object | 형상·구조 파라미터 |
| `quality_profile` | `P0_STATIC` 또는 `RELEASE_STATIC` | LOD/예산 정책 참조 |
| `provenance_id` | 존재하는 이력 ID | 원형 제작 이력 |

치수는 유한한 양수, 손상 비율은 0~0.35로 제한한다. socket을 변경하는 파라미터는 형태 변형 seed와 분리한다. 승인 상태는 recipe에 저장하지 않는다. 이전 6절의 `approval_status` 예시는 본 계약으로 대체한다.

### 17.2 생성 결과 인터페이스

`generate(recipe, context) -> AssetBuild`를 공통 계약으로 사용한다. `context`는 도구 버전, 팔레트, 독립 난수 스트림, 출력 경로를 포함한다. `AssetBuild`는 모델 ID, LOD별 메시, face별 semantic slot, socket transform, collider descriptor, measurements, input hashes를 반환한다. 메시 구조에는 정점·삼각형·face semantic ID만 의무화하고 Blender 객체 이름에 업무 상태를 숨기지 않는다.

### 17.3 Manifest와 승인

| 기록 | 필수 내용 |
|---|---|
| `asset_manifest.json` | ID, family, variant, revision, LOD별 파일/삼각형/정점/재질/이미지/바운딩박스, 팔레트 해시, socket, collider, source와 export SHA-256 |
| `approval.json` | 승인 주체, 시각, 판정, 지적 사항, 승인 대상 geometry/palette/recipe 해시, 사용한 preview profile |
| `provenance.json` | 생성 방법, 도구/코드, 자체 원형 근거, 참고 자료의 목적, 수동 편집, AI 사용 단계, 관련 라이선스 검토 상태 |
| `build_result.json` | build_id, 도구 버전, 시작/종료, 단계별 상태, 성공/실패 ID, 오류 코드, 산출 경로 |
| `release_manifest.json` | package_version, 판매/체험 대상 ID, 파일 경로/크기/해시, 모델 수, 문서/예제 버전 |

CSV는 사람이 읽기 위한 JSON manifest 파생물로만 생성한다. CSV를 고쳐도 원본 데이터는 바뀌지 않는다. geometry hash는 1µm 격자에 양자화한 좌표, semantic IDs, 정규화한 삼각형 목록으로 계산한다. 원시 GLB SHA-256도 별도로 보관한다. 해시 일치만으로 육안 품질 또는 독창성 합격을 결정하지 않는다.

### 17.4 시드 재현

각 random stream 키는 `schema_version|asset_id|seed|channel`을 SHA-256에 넣어 만든다. channel은 `trunk/canopy/stone/damage`처럼 고정한다. 런타임의 기본 `hash()`는 사용하지 않는다. 샘플 i는 `SHA256(key|i)`의 앞 53비트를 정수로 읽어 2^53으로 나눈 값으로 정의한다. 정수 선택은 `floor(u*n)`이며 `n>0`이어야 한다. 소비 순서가 바뀌어도 다른 channel에 영향을 주지 않는다.

## 18. 42개 원형 카탈로그

아래 각 family에서 A/B 2개를 만들므로 총 84개다. B는 카테고리별로 구조적 차이가 있어야 한다. 같은 길이/소켓은 유지하되, 나무는 가지/수관, 바위는 종횡비/큰 면, 경계는 레일/돌 배치/파손 위치가 달라야 한다.

| 범주 | family ID 목록 | 원형 수 |
|---|---|---:|
| 나무 | `TREE_ROUND_SMALL`, `TREE_ROUND_BROAD`, `TREE_TIERED_SLIM`, `TREE_TIERED_WIDE`, `TREE_DEAD_FORK`, `TREE_DEAD_LEAN` | 6 |
| 바위 | `ROCK_LOW_WEDGE`, `ROCK_UPRIGHT`, `ROCK_FLAT_SLAB`, `ROCK_SPLIT_MASS`, `ROCK_CLUSTER_SMALL`, `ROCK_CLUSTER_LARGE` | 6 |
| 덤불/풀 | `VEG_BUSH_ROUND`, `VEG_BUSH_LONG`, `VEG_BUSH_SPARSE`, `VEG_GRASS_LOW`, `VEG_GRASS_FAN`, `VEG_GRASS_TUFT` | 6 |
| 숲 소품 | `PROP_STUMP_ROUND`, `PROP_STUMP_SPLIT`, `PROP_LOG_STRAIGHT`, `PROP_LOG_BROKEN`, `PROP_BRANCH_FORK`, `PROP_BRANCH_PILE` | 6 |
| 목재 경계 | `WOOD_RAIL_1M`, `WOOD_RAIL_2M`, `WOOD_RAIL_4M`, `WOOD_CORNER_L90`, `WOOD_CORNER_R90`, `WOOD_END_CAP`, `WOOD_END_BROKEN`, `WOOD_POST`, `WOOD_GATE_FRAME`, `WOOD_GATE_LEAF` | 10 |
| 석재 경계 | `STONE_WALL_1M`, `STONE_WALL_2M`, `STONE_WALL_4M`, `STONE_CORNER_L90`, `STONE_CORNER_R90`, `STONE_END_CAP`, `STONE_END_RUIN`, `STONE_POST` | 8 |

`*_CORNER_L90/R90`는 경로 진행 방향 기준 좌/우 90도 회전이다. 단순 거울 복사라면 서로 다른 독립 원형으로 승인하지 않는다. 양쪽 코너에 실제 돌/지지대 구조 차이를 주고도 소켓은 규격에 맞춘다. 조립 경로에서 두 유형이 필요하다는 이유만으로 독립 미술 수량을 자동 인정하지 않는다.

초기 무료 체험 8개 ID: `TW_TREE_ROUND_SMALL_A`, `TW_TREE_TIERED_SLIM_A`, `TW_ROCK_LOW_WEDGE_A`, `TW_ROCK_UPRIGHT_A`, `TW_VEG_GRASS_LOW_A`, `TW_WOOD_RAIL_2M_A`, `TW_WOOD_POST_A`, `TW_STONE_WALL_1M_A`. 체험판은 Moss만 제공하며 체험 manifest로 허용 목록을 제한한다.

## 19. 첫 6개 모델의 정확한 레시피

아래 JSON은 실행용 코드가 아닌 초기 입력 명세다. 모든 모델의 LOD0 삼각형 상한은 목표이며 생성 후 실제 수치로 검증한다. 소켓 설명은 21절 좌표 규칙을 따른다.

```json
{
  "schema_version": "1.0.0",
  "generator_version": "0.1.0",
  "palette_id": "MOSS_01",
  "quality_profile": "P0_STATIC",
  "assets": [
    {
      "asset_id": "TW_TREE_ROUND_SMALL_A",
      "family_id": "TREE_ROUND_SMALL",
      "variant": "A",
      "seed": 11001,
      "provenance_id": "PROV_TREE_ROUND_SMALL_001",
      "parameters": {
        "height_m": 2.8,
        "trunk_height_m": 1.85,
        "trunk_radius_m": 0.14,
        "trunk_sides": 8,
        "trunk_rings": 5,
        "bend_deg": 7,
        "branch_count": 3,
        "canopy_lobes": 3,
        "canopy_width_m": 1.8,
        "canopy_height_m": 1.65
      },
      "triangle_caps": [1200, 600, 260],
      "collider": "trunk_capsule"
    },
    {
      "asset_id": "TW_TREE_TIERED_SLIM_A",
      "family_id": "TREE_TIERED_SLIM",
      "variant": "A",
      "seed": 11003,
      "provenance_id": "PROV_TREE_TIERED_SLIM_001",
      "parameters": {
        "height_m": 3.8,
        "trunk_height_m": 3.55,
        "trunk_radius_m": 0.12,
        "trunk_sides": 8,
        "trunk_rings": 6,
        "bend_deg": 3,
        "branch_count": 0,
        "tier_count": 3,
        "tier_sides": 9,
        "canopy_width_m": 1.7,
        "tier_overlap_ratio": 0.18
      },
      "triangle_caps": [1200, 600, 260],
      "collider": "trunk_capsule"
    },
    {
      "asset_id": "TW_ROCK_LOW_WEDGE_A",
      "family_id": "ROCK_LOW_WEDGE",
      "variant": "A",
      "seed": 21001,
      "provenance_id": "PROV_ROCK_LOW_WEDGE_001",
      "parameters": {
        "size_m": [1.3, 0.9, 0.65],
        "radial_segments": 9,
        "height_rings": 4,
        "radial_jitter_ratio": 0.12,
        "lean_deg": 11,
        "base_inset_ratio": 0.08
      },
      "triangle_caps": [800, 400, 160],
      "collider": "convex_proxy"
    },
    {
      "asset_id": "TW_ROCK_UPRIGHT_A",
      "family_id": "ROCK_UPRIGHT",
      "variant": "A",
      "seed": 21002,
      "provenance_id": "PROV_ROCK_UPRIGHT_001",
      "parameters": {
        "size_m": [0.8, 0.65, 1.55],
        "radial_segments": 8,
        "height_rings": 5,
        "radial_jitter_ratio": 0.1,
        "lean_deg": 6,
        "base_inset_ratio": 0.06
      },
      "triangle_caps": [800, 400, 160],
      "collider": "convex_proxy"
    },
    {
      "asset_id": "TW_WOOD_RAIL_2M_A",
      "family_id": "WOOD_RAIL_2M",
      "variant": "A",
      "seed": 31002,
      "provenance_id": "PROV_WOOD_RAIL_2M_001",
      "parameters": {
        "length_m": 2,
        "height_m": 1.1,
        "post_width_m": 0.14,
        "rail_count": 2,
        "rail_width_m": 0.08,
        "rail_height_m": 0.12,
        "rail_center_heights_m": [0.4, 0.8],
        "damage_ratio": 0,
        "include_start_post": true,
        "include_end_post": false
      },
      "triangle_caps": [1000, 500, 200],
      "collider": "compound_boxes"
    },
    {
      "asset_id": "TW_WOOD_RAIL_1M_A",
      "family_id": "WOOD_RAIL_1M",
      "variant": "A",
      "seed": 31001,
      "provenance_id": "PROV_WOOD_RAIL_1M_001",
      "parameters": {
        "length_m": 1,
        "height_m": 1.1,
        "post_width_m": 0.14,
        "rail_count": 2,
        "rail_width_m": 0.08,
        "rail_height_m": 0.12,
        "rail_center_heights_m": [0.4, 0.8],
        "damage_ratio": 0.15,
        "include_start_post": true,
        "include_end_post": false
      },
      "triangle_caps": [1000, 500, 200],
      "collider": "compound_boxes"
    }
  ]
}
```

묶음 상위 공통값은 읽을 때 각 모델로 복사하며 개별 값이 있으면 개별 값을 우선한다. 실제 스키마 검증은 이 확장 결과에 수행한다. 삼각형 상한을 맞추기 위해 원래 낮은 폴리곤 모델을 불필요하게 세분화하지 않는다.

## 20. 기하 생성 알고리즘

### 20.1 둥근 나무

1. t∈[0,1]의 중심선 C(t)를 만든다. 시작점은 (0,0,0), 끝 높이는 trunk_height. 굽힘은 높이에 따른 완만한 곡선이며 bend_deg 범위 안으로 제한한다.
2. 각 링에서 중심선 접선과 직교하는 프레임을 만든다. 첫 축은 접선과 거의 평행하지 않은 기준축을 선택하고 이후는 평행 운반으로 이어 회전 뒤집힘을 줄인다.
3. 반지름은 `r(t)=r0*(1-0.7*t)`를 시작값으로 사용한다. 인접 링의 급격한 반지름 차이는 r0의 20% 이내로 제한한다.
4. 링당 8정점을 연결하고 윗면/아랫면을 닫는다. winding과 법선을 확인한다. 가지 접합은 제한된 겹침을 허용하되 별도 폐곡면 구성 요소이며 작은 틈과 접합부 z-fighting을 확인한다. v1 메시를 3D 프린팅용 단일 수밀체로 광고하지 않는다.
5. 가지는 줄기 상부 45~85% 구간에서 3개 분기한다. 수관 덩어리 내부로 끝점을 넣어 분리되어 떠 보이지 않게 한다.
6. 수관은 저분할 폐곡면 다면체를 종횡으로 변형하고 큰 덩어리 3개로 조합한다. 목표 총 높이 2.8m, 폭 1.8m에 맞게 수관 그룹만 정규화한다. 줄기까지 통째로 스케일해 그립/충돌 규격을 바꾸지 않는다.
7. face semantic은 줄기/단면/잎 밝음·중간·어두움으로 지정한다. 랜덤 색상은 인접 큰 면의 연속성이 유지되는 범위로 제한한다.

### 20.2 층형 나무

3개의 낮은 원뿔형 폐곡면 수관을 수직 배치한다. 각 층은 9면으로 시작하고 아래→위 반지름 비율을 1.0/0.72/0.45로 둔다. 층 높이와 겹침은 전체 높이 3.8m 안에서 계산한다. 층 중심을 약간 어긋나게 하되 줄기와 분리되지 않게 한다. 단순 원뿔 중첩 외에 가장자리 실루엣을 제한적으로 변화시키고 확대/탑다운 두 시점에서 승인한다.

### 20.3 바위

1. 각 높이 링에 일정 각도의 점을 만들고 각도·반지름을 시드로 변형한다. 높이는 정렬된 링 순서를 유지한다.
2. family별 너비 프로파일로 쐐기형 또는 선돌형 점 구름을 구성한다. 지면보다 아래에 있는 임시 점은 바닥 평면으로 자른다.
3. convex hull로 외피를 생성하고 최종 크기 `size_m=[X,Y,Z]`에 맞춘다. hull이 생성되지 않거나 모든 점이 평면이면 입력 오류로 처리한다.
4. 바닥은 z=0으로 정리하고 닫는다. 정상 위쪽 면의 노멀을 보존하면서 triangulate한다. 기준점은 바닥 투영 범위 중앙이다.
5. 단일 바위는 convex를 유지한다. 갈라진 바위/군집은 여러 convex 구성 요소를 조합하고 collider도 그에 맞춰 단순체를 선택한다. 임의 boolean으로 미세 면을 대량 만들지 않는다.
6. 색상은 큰 면별 stone slot에 배정한다. UV 없이 재질만 회색으로 내보내는 경로는 허용하지 않는다.

### 20.4 목재 경계

1. 규격 중심선은 +X 방향이다. 첫 기둥 중심은 x=0, 다음 연결점 x=L이며 기둥의 실제 두께는 중심선 밖으로 반폭만큼 나올 수 있다.
2. 각 모듈은 시작 기둥을 소유하고 끝 기둥은 소유하지 않는다. 열린 경로 끝에는 전용 POST/END를 추가한다. 닫힌 경로에서는 마지막 END를 추가하지 않는다. 이 규칙으로 기둥 중복을 방지한다.
3. 레일은 기둥 두께를 고려해 start_face부터 end_face까지 만들고, 높이는 0.4/0.8m다. 접합부에 최대 2mm 겹침을 허용하되 눈에 보이는 틈은 1mm 이내다.
4. 지지 장식은 두께를 유지한 쐐기·캡으로 자체 제작한다. 모서리 bevel은 LOD0에서만 선택적으로 사용한다.
5. `damage_ratio=0.15`는 레일 중앙의 장식적 파임에만 적용한다. 양쪽 socket에서 0.15m 이내와 지지부는 보호한다. P0에서 통행 가능한 틈은 만들지 않는다.
6. 파손 폭·깊이의 합으로 단면이 50% 미만 남는 후보는 반려한다. 장식적 파손 collider는 레일 박스를 유지하되 문서에 단순화임을 표시한다.

### 20.5 석재/식생/소품 확장

석벽은 높이 층별 돌 덩어리를 엇갈리게 배치하고 양끝 socket 보호 영역을 유지한다. 풀은 폐곡면 쐐기 blade를 3~7개 묶는다. 덤불은 수관 원형의 저상형 조합, 통나무와 그루터기는 줄기 링 생성기를 재사용하되 단면과 접지 규칙을 별도로 가진다. 원형 라이브러리의 공통 함수 재사용은 허용하지만 결과 카테고리의 검증 예산은 별도로 적용한다.

## 21. 좌표·소켓·배치 수학

### 21.1 축과 변환

모델 제작 좌표는 X=길이/오른쪽, Y=깊이, Z=위다. glTF 출력은 `(x_g,y_g,z_g)=(x_b,z_b,-y_b)`로 정의한다. 실제 export가 이 변환을 처리하면 추가 변환을 하지 않는다. 1m 축 마커를 이용해 이중 변환을 검사한다. 변환 행렬의 determinant는 +1이어야 한다.

socket은 `position_m`, `outward_axis`, `up_axis`를 기록한다. 직선 시작은 `(0,0,0)`, outward `(-1,0,0)`이고 끝은 `(L,0,0)`, outward `(1,0,0)`이다. 두 모듈을 붙일 때 위치는 일치하고 outward 축은 반대 방향이어야 한다. 단순히 두 socket transform을 동일하게 복사하지 않는다.

각 소켓에서 z축은 up으로, x축은 outward로 두고 y축은 z×x로 만든 직교 frame F를 사용한다. 이전 끝 frame을 F_end, 새 시작 frame을 F_start라 할 때 새 모델 world transform은 `F_end * Rz(180°) * inverse(F_start)`다. 이 식의 축은 제작 좌표 기준이며 export 뒤에는 동일 변환을 적용한 frame을 사용한다.

### 21.2 경로 분할

P0는 직선만 검증한다. P1에서 90도 코너/열린 경로/닫힌 경로/15도 이내 경사를 추가한다. 입력 polyline의 1mm 미만 연속 점은 병합하고, 길이 0인 경로는 오류다. 90도 외 코너는 자동 확정하지 않고 수동 구간으로 표시한다.

직선 길이는 mm 정수로 다룬다. `{1000,2000,4000}` 모듈의 조합을 동적 계획으로 탐색하여 (잔여 길이, 모듈 개수) 순서로 최소화한다. 잔여 1mm 이내는 허용, 1~250mm는 `NEEDS_CUSTOM_END`, 그 이상은 `UNSUPPORTED_LENGTH`를 반환한다. 판매 모델 전체를 임의 스케일하여 맞추지 않는다. 사용자 선택으로 경로 끝을 스냅하는 것은 별도 조작이며 기본으로 실행하지 않는다.

### 21.3 경사와 코너

기둥은 수직으로 두고 연결점 높이를 지형 샘플에서 구한다. 단차형은 수평 레일과 층별 기둥으로 배치하고, 경사형은 내부 도구가 자체 원형 파라미터에서 레일을 다시 생성한다. 경사 모델은 원본 판매 모델 수에 포함하지 않는 예제 전용 파생물이며 메타데이터에 명시한다. 고객에게 자동 변형 기능을 약속하지 않는다.

닫힌 경로의 마지막 연결은 첫 점과 위치 1mm, 방향 0.1도 이내여야 한다. 문틀 구간은 사전에 예약하고 끝단/파손/임의 누락이 침범하지 못하게 한다. world transform은 recipe와 분리된 scene placement 데이터에 저장한다.

## 22. 팔레트·UV·색상 상세

256×256 PNG를 8열×4행, 셀 32×64px로 나누어 32개 semantic slot을 배치한다. 모든 face의 세 UV를 해당 셀 중심에 두는 상수색 UV 방식을 사용한다. 면의 조명은 normal로 결정하며 색면에 텍스처 노이즈를 추가하지 않는다. 이는 일반 텍스처 페인팅용 UV가 아니므로 상품 설명에 palette UV라고 명시한다.

| 슬롯 | 의미 | Moss 기본값(설계 후보) |
|---|---|---|
| 00~03 | bark dark/base/light, cutwood | `#3B3028`, `#66503B`, `#8C7251`, `#C8A875` |
| 04~07 | leaf dark/base/light, new leaf | `#253D31`, `#456044`, `#6F8752`, `#A3AE6D` |
| 08~11 | stone dark/base/light, warm stone | `#424A4B`, `#69716B`, `#929A87`, `#8E816C` |
| 12~15 | moss dark/base/light, dry plant | `#394A2D`, `#657C3C`, `#90A24F`, `#A59B6C` |
| 16~19 | wood dark/base/light, broken edge | `#493A2D`, `#796045`, `#A18762`, `#C0A17B` |
| 20~23 | soil/shadow/neutral dark/neutral light | `#51483A`, `#292D2C`, `#565E59`, `#C4C5AD` |
| 24~27 | accent muted/light/dark/neutral | `#8C6A4E`, `#B7966B`, `#574539`, `#8A8D72` |
| 28~31 | 예약 영역 | 초기에는 20~23과 같은 색, 사용하지 않음 |

슬롯 28~31은 초기에는 20~23의 색을 복제한 예약 영역이며 의미를 부여하기 전 새 모델에서 참조하지 않는다. Dry/Dusk도 같은 slot 의미를 유지한다. Dry는 식생의 황갈색 범위를, Dusk는 청회색·자주색 저채도 범위를 늘리되 순수 검정으로 형태를 숨기지 않는다. 자동 hue shift만으로 최종 승인하지 않는다.

색상 PNG는 sRGB로 기록한다. 셰이더의 선형 색상 입력에 hex값을 그대로 대입하지 않는다. GLB baseColorFactor는 [1,1,1,1], metallic=0, roughness=0.85를 기본으로 사용한다. UV가 한 점에 모이는 특성상 미분값이 작지만, 모든 엔진에서 밉맵 색 섞임이 없다고 가정하지 않는다. P0는 base-level 중심 샘플링을 시험하고 Godot 공유 재질은 nearest/no-mipmap 프로파일을 우선 검증한다. 필터·밉맵 지원은 임포터 설정을 확인해 명시한다.

기본 PNG는 GLB 안에 bufferView로 포함한다. 각 GLB의 텍스처 복제는 자립 임포트를 위한 선택이며, Godot에서는 외부 공유 팔레트/머티리얼로 연결해 중복 리소스를 줄인다. 컬러 테마 변경은 geometry/UV 변경 없이 같은 슬롯을 교체한다. `TW_PALETTE_BASE_V1` 재질명을 고정해 엔진 재연결을 안정화한다.

## 23. LOD·충돌체·Godot 어댑터

### 23.1 LOD 생성

우선순위는 카테고리별 구조 단순화 → 제한된 메시 축소 → 수동 수정이다. 나무는 작은 가지 제거/수관 면 수 감소, 바위는 점 샘플 수를 줄여 hull 재생성, 경계는 bevel/장식 제거를 사용한다. 소켓·바닥·문 경첩은 잠금 대상이다. LOD0가 이미 100삼각형 미만이면 단순화 이득을 확인한 후 LOD1만 제공하거나 생략하고 이유를 적는다.

정규화된 동일 카메라의 256×256 실루엣에서 LOD0 대비 IoU 목표를 LOD1≥0.95, LOD2≥0.88로 둔다. 정면·측면·45도·탑다운 네 시점 모두 검사한다. 이 기준은 초기 가설이며 P0 시각 결과로 조정할 수 있다. 접합점 1mm 기준은 LOD별로 그대로 적용한다.

### 23.2 엔진 LOD 방식

출고 GLB는 수동 제작 LOD를 별도 파일로 제공한다. Godot 예제는 검증된 visibility range 구성으로 LOD0/1/2를 교체하며 동일 메시의 자동 LOD 생성은 끈다. 자동 LOD와 수동 LOD를 동시에 켜서 겹치거나 의도치 않게 두 번 단순화하지 않는다. Godot 공식 문서는 자동 mesh LOD와 artist-authored mesh의 visibility range 방식을 구분한다.[S2]

예제 초기 전환 거리는 자연물 12/28m, 경계 18/40m, 풀 컬링 25m다. 이것은 예제 카메라용 시작값이고 판매 호환성 보장값이 아니다. 기본 mesh LOD와 visibility range의 엔진 설정 방식은 구현 버전에서 확인한다. 정사영 카메라는 거리에 따른 화면 크기 감소가 없으므로 P0 탑다운 예제에서는 고정 LOD0를 사용하고 줌 변화별로 별도 평가한다. 원근용 거리 설정을 그대로 적용하지 않는다.

### 23.3 충돌체 계약

충돌체는 glTF core가 자동으로 범용 물리체를 전달한다고 가정하지 않는다. 별도 JSON descriptor와 Godot wrapper scene으로 제공한다. GLB에는 충돌 메시를 일반 렌더 메시로 넣지 않는다.

| 종류 | descriptor | 제약 |
|---|---|---|
| 나무 | capsule 중심/반지름/전체높이 | 높이≥2r, 수관 제외, 기울어진 줄기는 최대 2개 capsule |
| 바위 | 16정점 이하 convex proxy | 심하게 밖으로 튀는 부분 3cm 초과 시 검토 |
| 울타리 | 기둥/레일 box 목록 | 중심·회전·full extents 명시; 열린 끝 기둥 제외 |
| 장식 식생 | `none` | 엔진에도 자동 collision 생성 안 함 |
| 문틀/문짝 | 각각 별도 body descriptor | 문틀 aperture에 solid box를 덮지 않음 |

collider는 모든 LOD에서 같은 고정 기준을 사용한다. 시각 LOD 전환으로 충돌이 달라지지 않는다. Godot adapter가 m 단위/축을 한 번 변환하여 StaticBody3D와 CollisionShape3D를 만든다. 동적 문 제어는 고객 구현이며 예제에는 정적 닫힘/열림 상태만 제공한다.

### 23.4 Godot 어댑터 입력/출력

입력은 `release_manifest.json`과 외부 팔레트다. 출력은 `assets/`, `materials/`, `scenes/`, `examples/`, `project.godot`이며 검사 결과에 정확한 Godot 버전을 기록한다. 각 모델 wrapper는 하나의 Root Node3D, LOD별 visual 노드, sockets, 선택적 collision을 가진다. glTF 자체 재질로 최초 로드가 성공한 후 공통 외부 재질로 재연결한다. 자동 importer 물리 생성과 descriptor 생성은 둘 중 하나만 사용하며 기본은 descriptor다.

재임포트 시험에서는 파일 수정 후 외부 머티리얼과 socket 이름의 연결을 확인한다. Godot는 외부 머티리얼 연결을 지원하지만 원본 재질명 변경 시 연결이 깨질 수 있으므로 이름을 고정한다.[S1] 엔진별로 설정 키가 달라질 수 있어 키를 추측해 파일에 쓰지 않고 고정 버전의 실제 import 설정을 확인한다.

## 24. 검증 명세와 오류 코드

| 코드 | 검사 | 판정/동작 |
|---|---|---|
| R001 | 필수값/허용 범위/알 수 없는 키 | error, 생성 전 중단 |
| R002 | ID/family 불일치 또는 중복 | error |
| G001 | NaN/Inf/잘못된 인덱스 | error |
| G002 | 면적≤1e-10m²인 삼각형 | error; 조용히 삭제하지 않음 |
| G003 | 비의도적 역면/열린 경계 | error 또는 명시된 원형 예외 |
| G004 | 삼각형 예산 초과 | error; 예외 승인은 별도 budget revision |
| M001 | 이미지/UV/semantic slot 누락 | error |
| M002 | 미승인 양면/투명/추가 재질 | error |
| S001 | socket 위치 오차>1mm/방향 오차>0.1도 | error |
| L001 | silhouette IoU 목표 미달 | review required; 자동 출고 불가 |
| C001 | collider 치수/축/통행 구멍 오류 | error |
| P001 | provenance 또는 연결된 승인 없음 | release 차단; preview 허용 |
| P002 | 승인 해시와 현재 결과 불일치 | 승인 무효화 |
| X001 | export 후 깨진 참조/이미지 누락 | error |
| K001 | 패키지에 manifest 외 파일 | error |
| K002 | 모델 수/체험 subset/파일 해시 불일치 | error |

임의 self-intersection 검사는 완전한 자동 증명을 목표로 하지 않는다. 구성 요소 간 허용된 겹침과 실제 오류를 구분하며, 접합부 시각 검사를 추가한다. UV를 상수색 샘플로 쓰므로 UV 면적 0은 이 제품에서 오류가 아니지만, 형상 삼각형 면적 0은 오류다.

### 반드시 실행할 수락 시험

| 시험 ID | 입력/상황 | 기대 결과 |
|---|---|---|
| AT01 | P0 recipe 6개 | 유일한 ID 6개, provenance 6개, 생성 성공 또는 원인 명시 |
| AT02 | 2m 모듈 5개와 끝 기둥 | 소켓 경로 10m, 중복 기둥 0, 틈≤1mm |
| AT03 | 1m+2m+4m | 규격 경로 7m, 스케일 변경 없음 |
| AT04 | 경로 2.13m | NEEDS_CUSTOM_END, 임의 늘림 없음 |
| AT05 | 열린/닫힌 경로 | 열린 경로에만 마지막 끝 기둥 1개 |
| AT06 | 모듈 전체 회전 90도 | 소켓·법선·collider가 함께 회전 |
| AT07 | 같은 recipe/도구 버전 2회 | normalized geometry hash와 측정값 일치 |
| AT08 | recipe 목록 순서 변경 | 각 모델 hash 불변 |
| AT09 | texture 제거/외부 절대경로 삽입 | M001 또는 X001로 출고 차단 |
| AT10 | Moss→Dry→Dusk | geometry/socket hash 불변, 팔레트만 변경 |
| AT11 | 6모델 새 빈 프로젝트 임포트 | 누락 재질·중복 충돌·축 오류 0 |
| AT12 | LOD0→1→2 | collider 불변, 소켓 오차 기준 충족 |
| AT13 | 승인 후 메시 변경 | P002, release 불가 |
| AT14 | ZIP staging에 타사/임시 파일 추가 | K001, 파일 미포함과 실패 보고 |
| AT15 | PNG 썸네일/문서 수량 | release ID 목록과 정확히 일치 |
| AT16 | 0m 경로/16도 경사 | 입력 오류/경사 범위 초과 경고 |

AT05의 닫힌 경로와 AT16 경사 시험은 P1 범위다. P0에서 미수행을 합격으로 표시하지 않는다. 테스트 보고서는 PASS/FAIL/NOT_RUN/NOT_APPLICABLE 네 상태를 사용하며 NOT_RUN은 합격 수에 포함하지 않는다.

## 25. 미리보기와 상품 검토 화면

P0는 한 장에 6모델의 3/4뷰를 보여주는 시트, 모델별 정면/측면/탑다운/와이어프레임, 연결 시험 장면으로 검토한다. 렌더 표시는 실제 생성 결과만 사용한다. 카메라·조명 프로파일 버전과 색 관리 설정을 저장해 수정 전후 비교가 가능하게 한다.

카탈로그는 1024×1024px, 50도 내려다보는 정사영, 모델 바운딩박스의 긴 변에 15% 여백, 회전 45도를 시작값으로 한다. 미세한 디테일을 감추는 과도한 bloom/안개/피사계 심도는 사용하지 않는다. 조명은 넓은 key/fill과 중립 배경으로 고정한다. 엔진 화면과 오프라인 렌더를 명확히 구분한다.

검토 시트에는 ID·LOD0 삼각형·치수·승인 상태를 표시하되 최종 상품 대표 이미지에는 필요한 사양만 별도 표로 옮긴다. 썸네일에는 타사 로고나 연구용 이미지를 넣지 않는다.

실루엣 변형 후보가 충분히 다른지 보는 기준은 구조 차이 1개 이상과 4방향 비교다. 구조 차이는 가지 분기, 수관 군집 배치, 바위 대면 비율, 레일 지지 구조 등이며 팔레트·회전·미세 노이즈만으로 충족하지 않는다. 완성도가 좋은 A형에 억지로 B를 붙이기보다 B를 재설계한다.

## 26. 제작 순서·완료 판정·인계

### P0: 전체 파이프라인을 작은 규모로 검증

1. Toolchain lock, recipe schema, family catalog, RNG 계약을 구현한다.
2. 팔레트 1종과 바위 2개로 geometry→UV→GLB→새 프로젝트 import를 먼저 연결한다.
3. 나무 2개와 울타리 2개를 추가해 총 6개로 확장한다.
4. 2m×5개 연결, 1m+2m+4m 시험은 P0 소량 fixture 모듈로 수행하며 fixture를 상품 모델 수에 더하지 않는다. 4m 원형 본 제작은 P1에 수행한다.
5. 검증 결과와 미리보기를 생성하고 기술 오류 수정 후 미술 검토용 묶음을 만든다.
6. P0 geometry/재질/소켓/임포트가 합격하고 미술 승인이 기록되면 P1로 진행한다.

P0 산출물: 원형 source, 6개 LOD0 GLB, 필요한 LOD1/2, Moss PNG, 6개 recipe/provenance, measurements/validation, 재현용 lock, Godot 검증 장면, 실제 렌더 시트. 내부 검토 묶음은 생성기 소스를 포함할 수 있으나 판매 묶음과 별도 채널로 만든다.

### P1: 수량 확장과 출시 준비

42원형 카탈로그를 순서대로 구현하되 자연물→목재→석재 순으로 확장한다. A/B 승인 후 테마 3종, 예제 6종, 체험 8개를 구성한다. 모바일 측정, 재임포트, 새 구매자 절차 테스트를 통과한 파일만 release candidate로 만든다.

### P0에서 남길 의사결정 기록

| 항목 | 기록 내용 |
|---|---|
| 시각 승인 | 승인자·6모델 이미지·수정 요구 |
| 품질 예산 | 실제 삼각형/실루엣/재질 결과에 따른 조정 사유 |
| 구현 난점 | hull 실패·팔레트 샘플링·socket export 등 재현 사례 |
| 도구 버전 | 설치 버전·export 옵션·엔진 renderer |
| 범위 조정 | 목표 84 유지/축소 결정의 근거 |

원형 생성·엔진 통합·아트 승인·실기기 시험을 분리해 상태를 보고한다. 예를 들어 6개 GLB가 생성되어도 렌더/엔진 검증이 끝나지 않았다면 ‘P0 완료’로 표시하지 않는다.

## 27. 상세설계 근거와 구현 시 확인할 사항

- [S1] Godot Advanced Import Settings: 외부 머티리얼 연결, physics 생성 옵션과 재질명 변경 시 연결 영향. https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/advanced_import_settings.html
- [S2] Godot Mesh LOD: 자동 생성 LOD와 수동 작성 메시의 visibility range 구분. https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html
- [S3] Khronos glTF 2.0 Specification: 좌표·단위·메시·재질·이미지 구조의 검증 기준. https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

출처 확인일: 2026-10-18. `stable` 문서는 나중에 내용이 바뀔 수 있으므로 구현 시 고정한 엔진 버전과 대조한다. Blender 공식 export 문서는 이번 조회에서 접근 오류가 있어 구체적인 operator 인자나 버전 호환성을 확인했다고 주장하지 않는다. 설치 환경에서 exporter 옵션을 확인하는 작업을 P0에 둔다.

이번 산출물은 상세설계 문서다. 신규 모델, 생성기 코드, 상점 등록 또는 실기기 측정은 아직 수행하지 않았다.
