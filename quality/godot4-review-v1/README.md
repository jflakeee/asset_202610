# Trailwood 6종 Godot 가져오기 검토 프로젝트

2026-10-28. **Godot 4.7.2 stable 공식 Linux x86_64의 headless 검사 통과. GPU 화면·성능·유료 판매 품질 승인은 별도다.** 기존 사이트의 모델은 교체하지 않았다.

## 실제로 확인한 것

- `core6-r3`와 동일한 6개 GLB를 Godot 에디터의 기본 glTF 가져오기 경로로 가져왔다.
- 삼각형: 상자568, 광석42, 코인192, 밧줄682, 포션260, 나무160.
- 13개 표면에 정점 색상 배열이 있으며 모든 재질에서 정점 색상을 기본색에 사용하도록 설정됐다.
- 가져오기 후 위치 경계와 크기를 원본과 비교했다. 경계 시작점/크기 벡터 오차 허용값은 각각 0.002m이며 각 모델이 통과했다. 이 허용값은 내부 테스트 기준이다.
- 상자 `Chest_Open`의 0초/0.3초/0.6초 자세를 검사했다. 실제 힌지 각도 약0°/52.5°/105°.
- 기존 `.godot` 캐시가 없는 새 경로에서 재가져오기를 반복해 동일하게 통과했다.
- 준비한 `review.tscn` 장면은 headless로 로드/짧은 실행을 확인했다. 화면을 실제 렌더링해 눈으로 검수한 것은 아니다.

## 발견한 문제와 수정

처음에는 GLB의 색상 배열이 존재해도 일부 가져온 재질의 `vertex_color_use_as_albedo`가 false였다. 예를 들어 단일 표면인 코인/밧줄/통나무가 이 조건에서 실패했다. 공식 glTF 검사 통과와 실제 엔진의 재질 설정이 별개임을 확인한 사례다.

`post_import.gd`가 색상 배열이 있는 표면의 재질을 복제하고 다음을 명시적으로 설정한다.

- `vertex_color_use_as_albedo = true`
- `vertex_color_is_srgb = false` — 제공 GLB의 COLOR_0는 선형 인코딩이다. 기존 가져온 재질도 이 값은 false였다.

각 `.glb.import`에 후처리 스크립트 경로를 저장했다. **GLB만 다른 프로젝트로 복사하면 이 설정이 따라가지 않는다.** 다른 프로젝트에서는 `post_import.gd`를 함께 옮겨 Import Script에 지정한 후 재가져오기하거나, 재질의 Vertex Color → Use As Albedo를 직접 켜야 한다. 스크립트 위치를 바꾸면 경로도 변경한다. 후처리는 제공된 색상 사용 방식 전용이다.

이번 검사에서 재현한 동작만 기록하며 모든 Godot 버전의 일반적인 버그라고 단정하지 않는다.

## 열기와 사용

이 폴더 전체를 내려받아 `project.godot`를 Godot 4.7.2에서 연다. `prefabs/`에는 각각 GLB를 인스턴스하는 편집 가능한 `.tscn`이 있다. 모델 파일의 재가져오기를 유지하는 얇은 래퍼이며 충돌체·획득 로직 등 게임 동작은 포함하지 않는다.

`review.tscn`에는 같은 프로젝트 내 6종, 카메라·조명·바닥을 배치했다. 원래 모델 크기와 비례를 유지한다. 조명과 카메라는 검토용 초안이며 최종 홍보 화면이 아니다.

CLI 재검증:

```
godot --headless --path . --editor --import
godot --headless --path . --script res://check_import.gd
godot --headless --path . --quit-after 3
```

`.godot/`는 생성 캐시이며 제공하지 않는다. `.glb.import`는 후처리 설정이 들어 있으므로 유지한다. 테스트 스크립트는 실패 시 종료 코드1, 통과 시0을 반환하고 `reports/import.json`을 갱신한다.

## 증거

- `reports/import_before_fix.json`: 수정 전 색상 사용 설정 실패.
- `reports/import.json`: 수정 후 검사 결과.
- `reports/clean_import.json`: 기존 캐시 없이 재가져온 결과.
- `reports/environment.json`: 사용 엔진 다운로드 URL/버전/해시와 GLB별 SHA-256. 엔진 실행 파일은 이 프로젝트에 포함하지 않는다.

참고 공식 문서:
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html

## 아직 검증하지 않은 것

GPU를 통한 실제 화면의 색/금속 반사/그림자, 모바일 기기 프레임 시간·메모리, Windows/macOS/Android 실행, 다른 Godot 버전, Unity 가져오기, 충돌체, 외부 사용자 식별성, 최종 미술 마감과 Blender 편집 원본. 따라서 판매용 완성 팩으로 표시하지 않는다.
