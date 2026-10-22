# Trailwood Asset Pack — v0.23

독자 제작 저폴리 3D 에셋 개발 검토판입니다. 최종 판매·배포 승인판이 아닙니다.

## 다운로드

GitHub의 Code → Download ZIP으로 전체 파일을 다운로드할 수 있습니다.

압축을 풀고 `START_HERE.md`를 확인하세요. 생성 소스는 `creation/`, 3개 테마 에셋은 `standalone_assets/`, Godot 프로젝트는 `trailwood_godot/`에 있습니다. Godot에서 `trailwood_godot/project.godot`를 열 수 있습니다.

- 정규 모델 후보 84종, 전체 고유 모델 104종
- 3개 테마 GLB 327개, 편집 가능한 Blender 소스 포함
- 84종 제작 근거 연결 및 초기 6종 × 3테마 재생성 일치 확인
- LOD1 제공 4종, LOD2 미제공
- 실제 아트 승인·GPU 화면 검토·모바일 성능 측정·최종 판매 라이선스는 대기

현재 공개 저장소 업로드는 개발 결과 공유이며, 판매 준비 완료나 사용권 허가를 뜻하지 않습니다. 자동 검사 PASS도 사람의 아트 승인을 대신하지 않습니다.


## 브라우저 예제

https://jflakeee.github.io/asset_202610/

- 설치 없이 숲길 조합 예제와 104종 에셋 탐색
- LOD·연결 부품 포함 109개 모델 파일 × 3테마 = 327개 미리보기 이미지
- 이미지 확대, 검색·분류, 테마 변경, 3D 회전·확대, GLB 다운로드
- WebGL을 사용할 수 없는 브라우저는 실제 삼각형을 사용하는 Canvas2D 호환 모드 (그림자 제외)
- GPU 및 실기기 모바일 성능 승인을 뜻하지 않습니다.

갤러리 재생성: `python web/build_gallery.py` (creation/rebuild_requirements.txt 의존성).
웹 의존성 라이선스: web/THIRD_PARTY.md.
