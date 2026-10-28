# Trailwood 철광석 품질 개선 초안

2026-10-28. 상태: 검토용, 기존 배포 모델 미교체.

원래의 작은 광물 부분을 전후면에서 보이는 큰 철 함유 덩어리 3개로 재구성했다. 독자적인 절차 생성 형상이며 외부 모델 입력은 없다. 삼각형 수는 14 → 54, 재질은 2개다. 증가한 수량 자체를 품질 점수로 취급하지 않는다.

- `resource_iron_ore_quality.glb`: Y-up, 미터, 정면 -Z, 바닥 중심 원점. 암석 roughness .9, 광물 metallic .65 / roughness .55.
- `resource_iron_ore_quality.json`: 부품 단위 편집 데이터.
- `comparison.png`: 기존/개선본, 동일 월드 스케일·카메라·광원, 색/회색조/실루엣.
- `six_views.png`: 정면/후면/좌/우/상/3분의4 방향.
- `iron_ore_64.png`, `iron_ore_128.png`, `iron_ore_256.png`: 검토용 아이콘.
- `before.json`: 자체 제작한 이전 버전, 비교 재현용.

## 재현

Python 3, NumPy, SciPy, Pillow 필요.

```
python build.py
python render_review.py
```

좌표 유한성·퇴화 삼각형 없음 검사 통과. 별도 Three.js GLTFLoader에서 54삼각형, 2재질 프리미티브, 금속 재질 값, 바닥 높이와 경계 크기를 확인했다.

간이 렌더는 깊이 버퍼와 면 조명을 사용하되 PBR/반사/금속 효과를 재현하지 않는다. 배경은 고정이며 접지 그림자와 안티앨리어싱 외 후처리는 없다. 이미지 확인은 모델의 형태와 명도 검토용이다.

실제 사용자의 철광석 인식률, 모바일 GPU 비용, Unity/Godot 가져오기, glTF 공식 검증은 아직 수행하지 않았다. 광물 덩어리는 암석에 의도적으로 묻혀 있으며 단일 수밀 메시가 아니다. 편집 가능한 Blender 원본과 엔진 프리팹도 미제공 상태다. 판매 품질 승인은 보류한다.
