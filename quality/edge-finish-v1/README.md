# Trailwood 상자·광석 선택적 모서리 마감 검토본

2026-10-28. **근접 화면용 선택안이다. 모바일 기본 모델과 기존 배포 파일은 교체하지 않았다. 판매 품질 승인 전이다.**

## 적용한 마감

상자는 넓은 목재 테두리·측벽·뚜껑에 6mm, 금속 모서리 보호대와 잠금판에 1.5mm의 1단 Bevel을 적용했다. 바닥·벽 판자·얇은 띠 등에는 적용하지 않는다. 광석은 암석에 8mm, 광물 파편에 3.5mm를 적용했다. 이는 현재 모델 스케일에서의 실험값이며 모든 스타일이나 크기에 맞는 규격이 아니다.

|모델|기본 삼각형 → 마감|기본 GLB → 마감 GLB(bytes)|재질/렌더 프리미티브|
|---|---:|---:|---:|
|상자|568 → 1,144|40,976 → 91,940|3 / 6 유지|
|광석|42 → 146|6,180 → 15,556|2 / 2 유지|

상자 전체 모서리를 처리한 시험은 1,688삼각형이었다. 최종 선택안에서는 눈에 띄는 부위로 한정해 1,144개로 줄였다. 증가한 폴리곤 수 자체를 품질 개선 증거로 보지 않는다.

작업자 시각 검토에서는 큰 화면의 테두리와 광석 외곽 음영 차이를 확인했지만, 작은 아이콘에서는 차이가 제한적이다. 이 판단은 외부 사용자 평가 결과가 아니다. 기본 제공안은 `../core6-r3/`를 유지하며, 이번 버전은 근접 보상 연출/큰 소품 화면에서 필요할 때 선택한다. 자동 LOD 전환이나 적합한 전환 거리는 구현·측정하지 않았다.

## 제공 파일

- `blend/`: 마감 모디파이어를 편집할 수 있는 Blender 4.5.9 LTS 원본. 상자는 닫힌 상태로 저장하며 `Chest_Open` 액션 유지.
- `sources/`: 모디파이어를 평가한 부품별 삼각형 데이터. Y-up·미터.
- `models/`: 평가된 메시의 GLB. 상자 힌지/열림 애니메이션 포함.
- `renders/comparison.png`: 이전 Blender 기본 원본과 이번 선택안의 같은 조명·카메라 전후 비교.
- `renders/`: 64/128px 전후 이미지, 512px 마감 렌더, 상자 열린 상태.
- `reports/`, `validation/`: 적용 부품/폭, 재열기 검사 및 공식 glTF 검사 JSON.

## 검증

- Blender 파일을 다시 열고 평가된 삼각형 수와 활성 모디파이어 수 확인. 상자18개, 광석4개.
- 좌표 유한성·퇴화 삼각형 없음, 부품별 닫힌 에지와 방향 검사 통과. 부품 간 관통이나 전체 자기 관통이 없다는 증명은 아니다.
- Three.js GLTFLoader에서 메시/정점 색상/재질/바닥 경계 확인, 상자 0/52.5/105도 자세 검사 통과.
- Khronos 공식 glTF Validator `2.0.0-dev.3.10`: 두 모델 모두 오류·경고·정보·힌트0건. 문제 무시 목록/심각도 변경 없음.

이번 마감 변형은 Godot/Unity에 다시 가져와 검증하지 않았다. 기존 Godot 가져오기 결과는 기본 제공본에만 해당한다. 제공된 정점 색상을 사용하는 재질 설정을 엔진에서 확인해야 한다.

## 재현

형상 생성에는 `../blender-source-v1/`의 기본 원본이 필요하다. 수정 파일 덮어쓰기를 피하려면 복사본에서 실행한다.

```
blender --background --python finish.py -- /absolute/path/to/edge-finish-v1 /absolute/path/to/blender-source-v1
python build.py
python check_geometry.py
blender --background --python check_blends.py -- /absolute/path/to/edge-finish-v1
python review.py
```

Python 단계는 NumPy와 Pillow가 필요하다. 비교 렌더의 원본 위치가 다르면 `review.py --source /path/to/blender-source-v1`로 지정한다. finish.py는 Blender 원본/평가 메시/512px 렌더를 다시 만들고 build.py는 GLB와 manifest를 갱신한다.

공식 검사는 별도 개발 의존성이다:

```
npm install --no-save --package-lock=false --ignore-scripts gltf-validator@2.0.0-dev.3.10
node validate.cjs
```

Three.js 검사는 버전이 맞는 GLTFLoader.js/three.module.js 및 로더 의존 모듈이 있는 런타임 경로를 `node check-three.mjs /path/to/runtime`으로 전달한다.

CPU Cycles 렌더와 이 구조 검사는 실제 모바일 GPU 시간/메모리/그림자 품질이나 판매 선호도를 보장하지 않는다. 앞으로는 더 많은 부위에 일괄 마감을 추가하기보다, 게임 카메라에서 보이는 차이와 비용을 먼저 비교해야 한다.
