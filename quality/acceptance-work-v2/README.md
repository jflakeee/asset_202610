# P0 입력 순서·원설계 팔레트 출고 차단 검사

2026-10-29. 전체 완료나 미술 승인으로 표시하지 않는다.

AT01: 기존 P0의 유일한 레시피6개를 실제로 생성하고 기록된 레시피/제작 근거 파일 해시 및 테마 출력과 대조했다. 작성자 신원·권리·미술을 승인한 것이 아니다.

AT08: 나무/바위/경계 각 생성기의 레시피 목록을 역순으로 실행하고 ID별 GLB/원본 메시 해시가 동일함을 확인했다. P0의6개 레시피 범위이며 모든84개 생성기의 순서 독립성까지 보장하지 않는다.

AT09: 원설계 v1의 'PNG 팔레트가 내장된 GLB' 전용 사전 검사를 출고 게이트에 연결했다. 327개 정상 파일을 검사하고 누락/손상/범위 초과 팔레트는 M001, 외부 URI는 X001, 파일 해시 변경은 H001로 차단한다. 이 프로필에서는 상대경로·data URI도 허용하지 않는다. 일반 glTF의 유효성을 정의하는 검사는 아니다. 정점 색상을 쓰는 보조6종 core6-r3에 적용하면 안 된다.

누락 모델만 있는 불완전한 저장소를 입력한 통합 시험에서 기존 게이트를 실행하기 전에 종료코드2로 차단했다. 정상 내부 검토는0, 아직 미승인인 판매 게이트는2를 반환했다. 검사기는 승인 기록을 생성하거나 판매 상태를 허용으로 바꾸지 않는다.

폐기 가능한 저장소 사본에서 재생성/복원을 끝낸 후:

```
python check_recipe_order.py /path/to/repository
python preflight.py /path/to/repository
python test_preflight.py /path/to/repository
python gated_check.py /path/to/repository --channel review
python gated_check.py /path/to/repository --channel sales
```

마지막 명령은 미술 승인·LOD·실기기 등 기존 출시 조건이 미완료이면2로 실패하는 것이 정상이다. 원설계용 출고 검사는 gated_check.py를 진입점으로 사용한다. 기존 creation/release_gate.py 자체를 대체하거나 보안 우회가 불가능한 서비스로 제공하는 것은 아니다.

Python NumPy/SciPy/Pillow 및 기존 저장소 생성기들이 필요하다. 기존 모델은 completion-work-v1의 prepare_checkout.py 절차로 복원한다. 새 실행 결과가 reports에 저장되며 현재 reports는 이번 검사에서 생성했다. 전체 진행표는 ../completion-work-v1/STATUS.md를 따른다. 미실행 AT02/05/11/12/15 및 84종 LOD·실기기·미술 승인·판매 패키징이 여전히 남아 있다.
