# Trailwood 설계 대응 현황

원설계 v1.1의 42원형 × A/B = 84종을 현재 테마 manifest와 대조한 결과다.
파일 존재·해시는 검사하지만 아트 승인, 별칭 확정, 판매 준비 완료를 판정하지 않는다.

현재 LOD0 104종: 정확한 설계 ID 84종, 기존 이름 매핑 후보 8종, 별도 확장 12종, 기타 미매핑 0종.
**전체 제작 수를 원설계 84종의 완료 수로 사용하지 않는다.** 승인 완료 수는 별도 승인 기록으로 검증해야 한다.

| 범주 | 설계 목표 | 정확 ID 출력 | 매핑 검토 슬롯 | 미출력 슬롯 |
|---|---:|---:|---:|---:|
| 나무 | 12 | 12 | 0 | 0 |
| 바위 | 12 | 12 | 0 | 0 |
| 덤불/풀 | 12 | 12 | 0 | 0 |
| 숲 소품 | 12 | 12 | 0 | 0 |
| 목재 경계 | 20 | 20 | 0 | 0 |
| 석재 경계 | 16 | 16 | 0 | 0 |

## 기존 이름 매핑 후보

이 목록은 검토 제안이며 파일 이름이나 참조를 자동 변경하지 않는다. 후보가 있는 설계 슬롯도 구현 완료로 세지 않는다.

| 기존 ID | 제안 설계 ID | 상태·검토 사유 |
|---|---|---|
| TW_SHRUB_ROUND_A | TW_VEG_BUSH_ROUND_A | PROPOSED_NOT_APPROVED; present=True; round shrub; silhouette and source-ID migration review needed |
| TW_SHRUB_SPREAD_A | TW_VEG_BUSH_LONG_A | PROPOSED_NOT_APPROVED; present=True; wide shrub; elongated family suitability needs review |
| TW_GRASS_TUFT_A | TW_VEG_GRASS_TUFT_A | PROPOSED_NOT_APPROVED; present=True; radial solid-blade tuft; variant distinction needs review |
| TW_STUMP_CUT_SMALL_A | TW_PROP_STUMP_ROUND_A | PROPOSED_NOT_APPROVED; present=True; cut round stump; final shape approval needed |
| TW_STUMP_BROKEN_A | TW_PROP_STUMP_SPLIT_A | PROPOSED_NOT_APPROVED; present=True; broken rim does not establish split-stump structure; redesign may be needed |
| TW_LOG_CUT_2M_A | TW_PROP_LOG_STRAIGHT_A | PROPOSED_NOT_APPROVED; present=True; straight log; final shape approval needed |
| TW_LOG_BROKEN_15M_A | TW_PROP_LOG_BROKEN_A | PROPOSED_NOT_APPROVED; present=True; 1.5 m broken log; legacy ID must not imply 15 m |
| TW_GRASS_TALL_A | 미정 | UNRESOLVED; present=True; 9-blade radial tall grass; neither LOW nor FAN is demonstrated; select or redesign family |

## 별도 확장

TW_BENCH_BACKREST_A, TW_BENCH_SIMPLE_A, TW_CRATE_LONG_A, TW_CRATE_SMALL_A, TW_PAVER_LONG_A, TW_PAVER_ROUND_A, TW_SIGN_ARROW_A, TW_SIGN_FORK_A, TW_STEPS_LOW3_A, TW_STEPS_WIDE4_A, TW_TABLE_LONG_A, TW_TABLE_SQUARE_A

표지판·상자·디딤돌·계단·벤치·테이블은 원설계 84종에 더하지 않는다.

## 84개 설계 ID

| 설계 ID | 출력 상태 | 대응 후보 |
|---|---|---|
| TW_TREE_ROUND_SMALL_A | EXACT_ID_EXPORTED | — |
| TW_TREE_ROUND_SMALL_B | EXACT_ID_EXPORTED | — |
| TW_TREE_ROUND_BROAD_A | EXACT_ID_EXPORTED | — |
| TW_TREE_ROUND_BROAD_B | EXACT_ID_EXPORTED | — |
| TW_TREE_TIERED_SLIM_A | EXACT_ID_EXPORTED | — |
| TW_TREE_TIERED_SLIM_B | EXACT_ID_EXPORTED | — |
| TW_TREE_TIERED_WIDE_A | EXACT_ID_EXPORTED | — |
| TW_TREE_TIERED_WIDE_B | EXACT_ID_EXPORTED | — |
| TW_TREE_DEAD_FORK_A | EXACT_ID_EXPORTED | — |
| TW_TREE_DEAD_FORK_B | EXACT_ID_EXPORTED | — |
| TW_TREE_DEAD_LEAN_A | EXACT_ID_EXPORTED | — |
| TW_TREE_DEAD_LEAN_B | EXACT_ID_EXPORTED | — |
| TW_ROCK_LOW_WEDGE_A | EXACT_ID_EXPORTED | — |
| TW_ROCK_LOW_WEDGE_B | EXACT_ID_EXPORTED | — |
| TW_ROCK_UPRIGHT_A | EXACT_ID_EXPORTED | — |
| TW_ROCK_UPRIGHT_B | EXACT_ID_EXPORTED | — |
| TW_ROCK_FLAT_SLAB_A | EXACT_ID_EXPORTED | — |
| TW_ROCK_FLAT_SLAB_B | EXACT_ID_EXPORTED | — |
| TW_ROCK_SPLIT_MASS_A | EXACT_ID_EXPORTED | — |
| TW_ROCK_SPLIT_MASS_B | EXACT_ID_EXPORTED | — |
| TW_ROCK_CLUSTER_SMALL_A | EXACT_ID_EXPORTED | — |
| TW_ROCK_CLUSTER_SMALL_B | EXACT_ID_EXPORTED | — |
| TW_ROCK_CLUSTER_LARGE_A | EXACT_ID_EXPORTED | — |
| TW_ROCK_CLUSTER_LARGE_B | EXACT_ID_EXPORTED | — |
| TW_VEG_BUSH_ROUND_A | EXACT_ID_EXPORTED | TW_SHRUB_ROUND_A |
| TW_VEG_BUSH_ROUND_B | EXACT_ID_EXPORTED | — |
| TW_VEG_BUSH_LONG_A | EXACT_ID_EXPORTED | TW_SHRUB_SPREAD_A |
| TW_VEG_BUSH_LONG_B | EXACT_ID_EXPORTED | — |
| TW_VEG_BUSH_SPARSE_A | EXACT_ID_EXPORTED | — |
| TW_VEG_BUSH_SPARSE_B | EXACT_ID_EXPORTED | — |
| TW_VEG_GRASS_LOW_A | EXACT_ID_EXPORTED | — |
| TW_VEG_GRASS_LOW_B | EXACT_ID_EXPORTED | — |
| TW_VEG_GRASS_FAN_A | EXACT_ID_EXPORTED | — |
| TW_VEG_GRASS_FAN_B | EXACT_ID_EXPORTED | — |
| TW_VEG_GRASS_TUFT_A | EXACT_ID_EXPORTED | TW_GRASS_TUFT_A |
| TW_VEG_GRASS_TUFT_B | EXACT_ID_EXPORTED | — |
| TW_PROP_STUMP_ROUND_A | EXACT_ID_EXPORTED | TW_STUMP_CUT_SMALL_A |
| TW_PROP_STUMP_ROUND_B | EXACT_ID_EXPORTED | — |
| TW_PROP_STUMP_SPLIT_A | EXACT_ID_EXPORTED | TW_STUMP_BROKEN_A |
| TW_PROP_STUMP_SPLIT_B | EXACT_ID_EXPORTED | — |
| TW_PROP_LOG_STRAIGHT_A | EXACT_ID_EXPORTED | TW_LOG_CUT_2M_A |
| TW_PROP_LOG_STRAIGHT_B | EXACT_ID_EXPORTED | — |
| TW_PROP_LOG_BROKEN_A | EXACT_ID_EXPORTED | TW_LOG_BROKEN_15M_A |
| TW_PROP_LOG_BROKEN_B | EXACT_ID_EXPORTED | — |
| TW_PROP_BRANCH_FORK_A | EXACT_ID_EXPORTED | — |
| TW_PROP_BRANCH_FORK_B | EXACT_ID_EXPORTED | — |
| TW_PROP_BRANCH_PILE_A | EXACT_ID_EXPORTED | — |
| TW_PROP_BRANCH_PILE_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_RAIL_1M_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_RAIL_1M_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_RAIL_2M_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_RAIL_2M_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_RAIL_4M_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_RAIL_4M_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_CORNER_L90_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_CORNER_L90_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_CORNER_R90_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_CORNER_R90_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_END_CAP_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_END_CAP_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_END_BROKEN_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_END_BROKEN_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_POST_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_POST_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_GATE_FRAME_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_GATE_FRAME_B | EXACT_ID_EXPORTED | — |
| TW_WOOD_GATE_LEAF_A | EXACT_ID_EXPORTED | — |
| TW_WOOD_GATE_LEAF_B | EXACT_ID_EXPORTED | — |
| TW_STONE_WALL_1M_A | EXACT_ID_EXPORTED | — |
| TW_STONE_WALL_1M_B | EXACT_ID_EXPORTED | — |
| TW_STONE_WALL_2M_A | EXACT_ID_EXPORTED | — |
| TW_STONE_WALL_2M_B | EXACT_ID_EXPORTED | — |
| TW_STONE_WALL_4M_A | EXACT_ID_EXPORTED | — |
| TW_STONE_WALL_4M_B | EXACT_ID_EXPORTED | — |
| TW_STONE_CORNER_L90_A | EXACT_ID_EXPORTED | — |
| TW_STONE_CORNER_L90_B | EXACT_ID_EXPORTED | — |
| TW_STONE_CORNER_R90_A | EXACT_ID_EXPORTED | — |
| TW_STONE_CORNER_R90_B | EXACT_ID_EXPORTED | — |
| TW_STONE_END_CAP_A | EXACT_ID_EXPORTED | — |
| TW_STONE_END_CAP_B | EXACT_ID_EXPORTED | — |
| TW_STONE_END_RUIN_A | EXACT_ID_EXPORTED | — |
| TW_STONE_END_RUIN_B | EXACT_ID_EXPORTED | — |
| TW_STONE_POST_A | EXACT_ID_EXPORTED | — |
| TW_STONE_POST_B | EXACT_ID_EXPORTED | — |

## 아직 별도로 확인해야 할 출고 조건

- geometry/palette/recipe 해시에 연결된 사람의 아트 승인과 변경 시 승인 무효화.
- 원설계 AT01~AT16 상태를 PASS/FAIL/NOT_RUN/NOT_APPLICABLE로 구분한 실행 보고서.
- 1/2/4m·코너·열린/닫힌 경로·문 통행구멍·경사에 대한 조립 검증.
- 모델별 LOD 정책, 4방향 실루엣 평가, 생략 또는 기준 변경 근거.
- 편집용 .blend, 조립 예제 6종, 체험 8종 허용목록, 모델별 썸네일, CSV, 이용조건.
- 실제 렌더·재임포트·Android/iOS 측정. 헤드리스 성공으로 대체할 수 없다.

재생성: `python design_traceability.py` (build_themes.py 이후).
승인 검증 기능이 없는 이 보고서의 verified_art_approvals=0은 승인 기록 부재의 확정 판정이 아니다.
