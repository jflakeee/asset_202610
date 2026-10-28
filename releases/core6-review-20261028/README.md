# Trailwood 핵심 6종 통합 검토 팩

2026-10-28. **내부 검토용이며 판매 승인본이 아니다.** 이번 묶음은 이미 만든 결과물을 정리한 것으로 새로운 조형 개선이나 엔진 재검증을 의미하지 않는다.

## 어떤 파일을 사용하는가

|목적|위치|상태|
|---|---|---|
|기본 게임 모델|quality/core6-r3/models/|6종 압축 GLB, 공식 형식 검사 통과|
|Godot 테스트 프로젝트|quality/godot4-review-v1/project.godot|4.7.2 Linux headless 검사, 정점 색상 후처리 포함|
|편집 원본|quality/blender-source-v1/blend/|Blender4.5.9 LTS, 부품별 메시와 상자 액션|
|FBX 교환 파일|quality/fbx-review-v1/models/|Blender 왕복 검사, Unity 미검증|
|절차 생성 소스|quality/core6-r2/ 및 core6-r3/|Python 생성 및 압축 내보내기|
|대표 이미지|quality/blender-source-v1/renders/core6_blender.png|Cycles CPU 렌더, 실제 게임 화면 아님|

상자·광석의 모서리 마감 선택안은 기본 팩에 혼합하지 않았다. 별도 저장소 경로: https://github.com/jflakeee/asset_202610/tree/main/quality/edge-finish-v1

기본 GLB 삼각형 수: 상자568, 광석42, 코인192, 밧줄682, 포션260, 통나무160. 합계1,904. 상자는0.6초 열림 클립을 포함한다. 기본 GLB의 좌표는 Y-up·미터·정면-Z다. Blender 원본의 좌표 변환과 FBX 차이는 각 폴더 README를 따른다.

## 파일 검사

압축을 풀고 이 폴더에서 `python verify.py`를 실행한다. Python 표준 라이브러리만 사용한다. 파일 크기/SHA-256, 누락·추가 파일, 기본 GLB와 Godot 자산의 일치, GLB 헤더와 저장된 검사 증거를 확인한다. Blender/Godot/공식 glTF 검증기를 다시 실행하는 명령은 아니다.

manifest.json 자체의 무결성은 압축 파일의 외부 SHA-256(archive.json)으로 확인한다. manifest.json은 자신을 해시하지 않는다. 파일을 수정한 후 CHANGED가 나오는 것은 정상이다.

생성 소스가 포함되어 있어 원본 폴더를 통째로 내려받으면 상대 경로가 유지된다. `build`/`finish` 스크립트는 결과물을 덮어쓸 수 있으므로 수정한 파일은 별도로 보관한다.

## 구매자에게 아직 약속할 수 없는 것

자세한 항목은 QUALITY_STATUS.md 참조. Unity 호환성, 모바일 최적화, 모든 엔진에서 같은 재질 표현, 외부 사용자의 식별률·판매 선호도, 최종 미술 승인은 검증하지 않았다. 미리보기 아이콘에는 배경이 포함되므로 투명 인벤토리 아이콘이라고 표시하지 않는다.

제3자 유료 모델이나 무료 모델의 원본을 이 팩에 합치지 않았으며, 포함된 모델은 이 프로젝트에서 자체 절차 생성한 6종 검토본이다. 이번 내부 검토 팩에는 구매자용 최종 이용약관이나 판매 라이선스를 확정하지 않았다. 엔진·Blender 실행 파일과 외부 검증 도구는 포함하지 않는다.
