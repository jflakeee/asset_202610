# 원설계 조립·P0 Godot 검사 — 2026-10-29

원설계 AT02·AT05·AT11의 명시한 범위를 새로 실행했다. 전체 출시 승인이나 GPU/캐릭터 물리 검증이 아니다.

AT02: 실제 2m 목재 모듈5개와 끝 기둥1개로10m를 조립했다. 소켓5쌍, 스케일1, 논리 기둥 중심0/2/4/6/8/10m와 중복0을 확인했다. 각 모듈의 끝면 정점36개에서 다음 실제 메시 삼각형까지의 최대 거리 약5.22e-8m로1mm 이내다. 이는 해당 조립의 끝면 샘플 측정이며 전체 부품 간 자기 관통/모든 표면의 수밀성을 증명하지 않는다.

AT05: 열린10m 경로는 끝 기둥1개, 실제 목재/석재 좌우 닫힌 경로4개는 끝 기둥0개다. 각 닫힌 경로8개 소켓 연결과 위치/방향 폐쇄, 논리 기둥 중복0, 중복 소유자 음성 대조를 검사했다. 캐릭터 이동과 물리 접촉은 미검증이다.

AT11: Godot4.7.2 stable official Linux headless에서 원래 P0 나무2·바위2·울타리2를 빈 프로젝트로 새로 가져왔다.6종 모두 텍스처 참조, 삼각형 수, 경계 오차2mm 이내, 원본 모든 정점의 최근접 가져온 정점 오차2mm 이내, 의도치 않은 충돌 객체0을 확인했다. 이번 측정 정점 오차는 모두0이었다. 원래 원점/방향을 포함한 메시 좌표의 데이터 검증이며 실제 GPU 색상/그림자/물리 통행을 보장하지 않는다.

## 재현

먼저 ../completion-work-v1의 절차로 소스를 재생성하고 폐기 가능한 저장소 사본의 생성 산출물을 복원한다. Python NumPy/SciPy/Pillow 등 기존 생성기 의존성이 필요하다.

```
python check_assembly.py /path/to/disposable/repository
godot --headless --path godot --editor --import
godot --headless --path godot --script res://check.gd
```

check_assembly는 scenes/와 reports/assembly.json을 갱신한다. Godot은 godot/report.json을 갱신한다. 포함한 reports/godot_import.json은 이번 실행 결과의 보존본이다. 저장된 `.glb.import`와 expected.json을 유지하고 `.godot/`는 새로 생성한다. Blender나Godot 실행 파일은 포함하지 않았다.

Godot 최소 검토 프로젝트는 자동 충돌체를 만들지 않는다. 검증된 속성만 기록했으며 원설계 충돌 어댑터/실제 캐릭터 통행 구현 완료로 계산하지 않는다. 이 프로젝트는 판매용 예제가 아닌 엔진 데이터 검사 fixture다.

남은 원설계 AT12 전체84종 LOD, AT15 승인 모델 기반 썸네일/문서 검토, 미술 승인·실제GPU/Android/iOS 측정·판매 조건과 최종 패키징은 ../completion-work-v1/STATUS.md에서 계속 추적한다.
