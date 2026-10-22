# 전체 모델 재생성

이 폴더에는 바위·나무·울타리·목재 소품·식생·야영 소품·디딤돌·계단·벤치·테이블,
LOD1과 팔레트 3종의 생성 소스가 모두 있다. Blender 원본 파일은 아니다.
Godot 예제와 별개로 Python에서 생성할 수 있다.

## 실행

Python 3.12 환경에서 통합팩 압축을 풀고 creation/ 폴더로 이동한다.

```sh
python -m pip install -r rebuild_requirements.txt
python rebuild_all.py --out ../rebuilt_assets
```

--out에는 아직 존재하지 않는 폴더를 지정한다. 이미 있는 폴더는 덮어쓰지 않고
즉시 종료한다. 다시 실행할 때는 다른 새 폴더 이름을 사용한다.
설치 명령은 예시이며 스크립트가 패키지 설치나 네트워크 다운로드를 수행하지 않는다.

## 생성 순서

바위 → 나무 → 울타리 → 그루터기/통나무 → 관목/풀 → 표지판/상자 → 디딤돌/계단
→ 벤치/테이블 → 목재 모듈 → 석재 모듈 → 자연물 카탈로그 → LOD1 → 통합 배치 → 팔레트 3종 → 바람 정점 검사 순서로 실행한다.
개별 생성기의 고정 경로를 분리하기 위해 새 출력 폴더에 소스만 복사한 후 실행한다.
기존 GLB·메시 JSON·이미지를 생성 입력으로 복사하지 않는다.
레시피와 팔레트 값은 생성기 Python 코드에 포함되어 있다.

주요 결과:

- rebuilt_assets/creation/theme_output/: 3개 테마의 GLB 327개와 팔레트·파일 목록.
- rebuilt_assets/creation/*_output/: 모델별 원본 메시 JSON·레시피·미리보기.
- rebuilt_assets/creation/output/: 바위 결과.
- rebuilt_assets/creation/trees_output_v2/: 나무 결과.
- rebuilt_assets/rebuild_report.json: 누락·추가·변경 파일과 의존성 버전.
- rebuilt_assets/logs/: 단계별 표준 출력·오류 로그.
- rebuilt_assets/trailwood_godot/: 생성기가 쓰는 중간 통합 데이터. 전체 Godot
  프로젝트는 아니므로 실행하려면 배포팩의 trailwood_godot/를 사용한다.

## 실제 검증 결과

2026-10-20, Python 3.12.14와 rebuild_requirements.txt에 기록된 설치 버전에서
15단계가 모두 종료 코드 0으로 완료되었다. 입력 모델 복사 0개, GLB 결과 327개,
기준 해시 대비 누락 0·추가 0·변경 0이었다.
재생성 결과는 결과 파일의 SHA-256으로 비교했다. 코드만 실행해 기존 모델을
바이트 단위까지 동일하게 만든다는 것을 이 환경에서 확인한 것이다.
미리보기 PNG의 바이트 동일성, 다른 OS/라이브러리 버전, GPU 렌더 결과는 보장하지 않는다.

## 수정해서 사용할 때

원하는 생성기의 RECIPES/IDS 또는 generate 함수를 수정한다. 원본을 보관한 복사본에서
작업하는 것이 좋다. 수정 후에는 기준 배포본과 달라지는 것이 정상이다.
rebuild_all.py는 기준 해시가 달라지면 모델이 생성되었어도 FAIL과 종료 코드 1을 반환한다.
그때 changed 목록과 모델 검증 결과를 확인한다. 기존 baseline을 자동 갱신하지 않는다.
의도적 수정의 승인 여부는 생성 성공과 별개로 판단해야 한다.

테마 GLB의 규격 검사를 추가하려면 별도로 gltf-validator를 설치하고 실행한다:

```sh
NODE_PATH=/path/to/node_modules node validate_khronos.cjs ../rebuilt_assets/creation/theme_output/MOSS_01
```

DRY_01, DUSK_01도 같은 방식이다. 이 도구는 배포팩의 검증 보고서에 사용한 검사기이며
rebuild_all.py는 Node 설치 여부와 무관하게 Python 생성·동일성 검사까지 수행한다.
실제 Godot 검사 명령과 GPU·모바일 검증 한계는 프로젝트 README를 참고한다.
