# 전체 설계 재개·검증 및 투명 아이콘

현재 전체 상태는 STATUS.md와 reports/acceptance_matrix.json을 따른다. 최근6종이 원설계84종 전체를 대체하지 않는다. 전체 설계 완료·판매 승인으로 표시하지 않는다.

icons/64,128,256은 보조6종의 straight-alpha RGBA PNG다. 같은 Blender 기본 원본의 카메라/조명/AgX를 유지하고 필름 배경만 투명하게 렌더했다. master512는 재생성 입력, preview_light.png는 알파 확인용 불투명 비교판이다. 카메라는 각 모델 최대 치수를 기준으로 맞췄으므로 모델 사이 실제 크기 비교는 아니다.

atlas.png는1024×512, atlas.json의 rect는 각248×248 영역이다. 셀256, 패딩4px. standalone256 파일과 atlas의248 영역을 혼동하지 않는다. 알파 보간의 어두운 테두리를 줄이기 위해 premultiplied-alpha로 축소 후 straight-alpha로 저장했다. GPU의 밉맵/블렌딩 모드에서 최종 확인은 남아 있다.

재생성은 Blender4.5.9 LTS에서 `blender --background --python-exit-code 1 --python render_icons.py -- /absolute/path/to/completion-work-v1 /absolute/path/to/blender-source-v1`, 이후 `python build_icons.py`, `python check_icons.py` 순서다. Python 이미지 단계는 Pillow 필요.

reports/initial_failures는 생성 산출물 없는 저장소에서 처음 실행했을 때 실패한 로그다. 이는 숨긴 실패가 아니라 재현 순서 보완 근거다. reports/design_run.json은 복원 후 다시 실행한 최종 결과다. 84종의 미술 승인이나 실기기 성능을 검증한 보고서는 아니다.
