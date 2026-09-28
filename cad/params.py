# CR2025 극성 테스터 공유 치수 (단위: mm)
# 프로브 간격과 홈 폭은 노즈 시험편(docs/coupon.md 결과 기록, 2026-09-28)으로 확정한 값이다.

PROBE_SPACING = 2.2   # 프로브 A·B 끝의 중심 간 거리 (SOD-323 패드 중심 간 거리)
GROOVE_W = 0.5        # 철사 홈 폭 (잘라낸 LED·저항 다리 압입)
GROOVE_DEPTH = 0.7    # 철사 홈 깊이 (Ø0.5 둥근 다리, 0.5mm 네모 다리 모두 묻힘)
WIRE_EXPOSED = 1.5    # 노즈 끝 밖으로 나오는 철사 길이 (조립 치수)

# 배터리와 절연 기준 (본체 모델과 검사가 함께 쓴다)
BATTERY_D = 20.0      # CR2025 지름
BATTERY_T = 2.5       # CR2025 두께
POCKET_CLEAR_D = 0.4  # 배터리 포켓 지름 여유
POCKET_CLEAR_T = 0.3  # 배터리 포켓 두께 여유
NEG_SAFE_R = 6.0      # (−) 면 접점 구멍이 들어가야 하는 반경 (실제 배터리의 평평한 (−) 면을 재서 확인할 것)
NEG_PIN_W = 0.6       # ③ 철사 B 통과 구멍과 천장 접촉 홈의 폭
NEG_PASS_LEN = 1.2    # ③ 통과 구멍 길이 (철사가 비스듬히 꺾여 앞판을 지나간다)
NEG_CONTACT_LEN = 4.4 # ③ 통과 구멍 위쪽으로 이어지는 천장 접촉 홈 길이 (−) 면에 선으로 닿는 구간
INSULATION_MIN = 0.4  # 철사 홈과 배터리 포켓 사이 최소 플라스틱 두께

# 표시 LED (5mm). 플랜지가 다리 쪽에 있어 밖에서 압입할 수 없으므로 플랜지 자리로 받친다.
LED_FLANGE_D = 5.8
LED_CLEAR = 0.3

# 본체 배치 (cad/tester.py와 cad/check_tester.py가 함께 쓴다)
# 좌표: 정면에서 본 X(오른쪽 +) · Y(위 +, LED 쪽) · Z(두께, 뒷면 0 → 앞면 +), 배터리 중심이 원점.
BACK_T = 1.2          # 뒷판 두께
FRONT_T = 1.4         # 앞판 두께 (철사 홈 아래 절연층 포함)
LED_Z = 3.3           # LED 중심의 Z 위치 (다리가 앞뒤로 벌어진다)
BOSS_TOP = 14.3       # LED 받침 윗면의 Y 위치
SEAT_DEPTH = 2.0      # LED 플랜지 자리 깊이
# 케이블 커버 (별도 부품 stl/cover.stl): 노즈 구간 홈 위를 덮어 철사를 누른다
COVER_Y0 = -9.5       # 커버 위쪽 끝 (▶| 각인 바로 아래)
COVER_T = 0.8         # 커버 판 두께
COVER_TIP_GAP = 0.3   # 노즈 끝에서 커버가 물러나는 거리 (철사 끝은 그대로 나온다)
PEG_X = 3.0           # 커버 핀과 본체 고정 구멍의 X 위치 (±)
PEG_Y = -11.5         # 커버 핀과 본체 고정 구멍의 Y 위치 (노즈 윗부분, 포켓 밖)
PEG_D = 1.4           # 커버 핀 지름
PEG_HOLE_D = 1.5      # 본체 고정 구멍 지름 (세로 구멍은 인쇄 시 좁아져 핀이 꽉 낀다)
PEG_LEN = 2.5         # 커버 핀 길이
PEG_HOLE_DEPTH = 3.0  # 본체 고정 구멍 깊이

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # 각인 글꼴 (macOS 기본)
