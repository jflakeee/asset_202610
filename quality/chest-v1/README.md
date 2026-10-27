# Trailwood 상자 — 품질 개선 실험본

상태: 판매용 승인 전 검토본. 기존 배포 모델을 교체하지 않는다.

- `reward_chest_animated.glb`: 몸체와 힌지 분리, `Chest_Open` 0–105도/0.6초, Y-up·미터, 정면 -Z. 금속/목재 재질 값 조정.
- `reward_chest_quality.glb` / `_open.glb`: 정적 닫힘/열림 참고본. 정적 파일의 재질 값은 애니메이션 파일과 다르다.
- PNG: 검토용 간이 렌더. 깊이 정렬 및 조명은 최종 게임 렌더와 다를 수 있다.
- Python: 원본 생성기. 실행에 Python 3, NumPy, SciPy, Matplotlib, Pillow 필요.

## 재현 및 검증

```
python build.py
python export_animated.py
python check_sweep.py
```

메시 568 삼각형, 유한 좌표와 퇴화 삼각형, 힌지 계층을 검사했다. `check_sweep.py`는 몸체/뚜껑의 직육면체 부품만 0–105도를 1도 간격으로 검사한다. 경첩 핀과 리벳은 제외하며 연속적인 충돌 부재를 증명하지 않는다. 이산 샘플 외 각도, 장식 간 관통, 음영 및 실제 충돌체는 수동 검토가 필요하다.

별도 Three.js GLTFLoader/AnimationMixer에서 로드와 0·52.5·105도 포즈를 확인했다. Unity/Godot 실기기, glTF 공식 검증기, 외부 식별성 평가와 미술 승인은 아직 수행하지 않았다. 최종 상업 판매 품질을 보장하지 않는다.
