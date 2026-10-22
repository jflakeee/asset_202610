# Blender 편집 소스

`build_blender_sources.py`는 원설계 84개 canonical ID의 Moss LOD0 GLB를
Blender로 가져와 `blender_sources_output/Trailwood.blend`에 저장한다.
전체 canonical 테마 빌드가 먼저 완료되어야 하며 누락·해시 불일치 시 중단한다.

이 파일은 실제 메시·UV·재질·소켓을 편집할 수 있는 Blender 소스다.
절차적 생성기의 매개변수와 수정자를 복원한 Geometry Nodes 파일은 아니다.
기존 이름 후보 8종과 확장 소품 12종, LOD1, 다른 테마는 이 파일에 넣지 않는다.
다른 테마 팔레트는 통합팩 PNG를 사용한다.

## 실행

Blender 4.5.3의 Python/bpy 런타임으로 실행한다.

```sh
blender --background --python build_blender_sources.py -- --root . --out blender_sources_output
```

공식 PyPI의 `bpy==4.5.3`을 설치한 Python 3.11에서도 실행할 수 있다.
실제 실행 결과와 Blender 버전은 `blender_sources_output/validation.json`이 근거다.
보고서가 없거나 PASS가 아니면 Blender 파일 검증 완료로 표시하지 않는다.

## 편집 방법과 보존 규칙

- `Trailwood_Canonical_84` 아래에 모델 ID별 컬렉션이 있다.
- 좌표와 피벗을 유지하기 위해 모델은 원래 위치에 놓이고 첫 컬렉션만 표시한다.
  Outliner에서 원하는 컬렉션의 viewport/render 표시를 전환한다.
- GLB의 Y-up 좌표를 Blender glTF importer가 Z-up으로 변환한다. 추가 회전하지 않는다.
- Palette UV는 각 색상 셀의 중심을 샘플링한다. 일반적인 텍스처 페인팅 UV가 아니다.
- 각 이미지가 .blend에 내장되어 외부 이미지 경로 없이 열린다.
- 소켓 오브젝트 이름에는 모델 ID 접두사를 붙이고 원래 역할은 `socket_role`에 보존한다.
- 원본 형상을 변경하면 이전 GLB와 해시가 달라진다. 기존 아트 승인으로 간주하지 않는다.

## 검사 범위

저장 후 실제 .blend를 다시 열어 84개 컬렉션, 편집 메시, 삼각형 수, UV/재질,
소켓 역할, 내장 이미지 존재를 검사한다. 최종 파일 SHA-256도 기록한다.
이 검사는 GPU 렌더 품질·아트 승인·다른 Blender 버전 호환성 검증을 대체하지 않는다.

## 이번 실행 결과

2026-10-21, Blender 4.5.3 LTS 공식 bpy 런타임에서 실제 파일을 생성하고 다시 열었다.
84개 모델 컬렉션과 편집 메시, GLB와 동일한 삼각형 수, UV·재질 및 소켓 역할 검사를 통과했다.
동일한 Moss 팔레트를 공유 이미지 1개로 통합해 파일 안에 내장했으며, 재열기 후 내장 PNG의
SHA-256이 배포 팔레트와 일치하는지 확인했다. 모델별 입력 GLB 해시와 최종 .blend 해시는
validation.json에 기록돼 있다. 런타임 설치 파일은 모델팩에 포함하지 않는다.
