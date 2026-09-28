# CR2025 극성 테스터 본체 → stl/tester.stl, cad/tester.FCStd
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/tester.py
# freecadcmd는 예외가 나도 종료 코드 0을 돌려주므로, 결과는 "BUILD OK" / "BUILD FAIL" 줄로 판단한다.
#
# 좌표는 params.py 참고. 인쇄는 뒷면(Z=0)을 바닥에 두고 눕혀서 한다.
# 전류 경로: 배터리 뒷면(+) → ② 애노드 다리 → LED → ① 철사 A → 끝 A → 측정 대상 다이오드
#            → 끝 B → 철사 B → ③ 창 → 배터리 앞면(−)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import MeshPart
import Part

from params import (BACK_T, BATTERY_D, BATTERY_T, BOSS_TOP, FRONT_T, GROOVE_DEPTH, GROOVE_W,
                    LED_CLEAR, LED_FLANGE_D, LED_Z, POCKET_CLEAR_D, POCKET_CLEAR_T, PROBE_SPACING,
                    SEAT_DEPTH)

V = App.Vector
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_STL = os.path.join(ROOT, "stl", "tester.stl")
OUT_FCSTD = os.path.join(ROOT, "cad", "tester.FCStd")

# 두께 방향: 뒷판 | 배터리 포켓 | 앞판
POCKET_T = BATTERY_T + POCKET_CLEAR_T
POCKET_Z0 = BACK_T
POCKET_Z1 = BACK_T + POCKET_T            # 포켓 천장
TOTAL_T = POCKET_Z1 + FRONT_T
GROOVE_Z = TOTAL_T - GROOVE_DEPTH        # 앞면 철사 홈 바닥

POCKET_R = (BATTERY_D + POCKET_CLEAR_D) / 2
CASE_R = POCKET_R + 1.6                  # 옆벽 1.6mm
WIRE_A_X = -PROBE_SPACING / 2            # 철사 A 선 (왼쪽, ▶ 쪽)
WIRE_B_X = PROBE_SPACING / 2             # 철사 B 선 (오른쪽, | 쪽)

# 상단 LED 받침: LED는 철사 A 선 위에 서고, 다리는 앞(캐소드)·뒤(애노드)로 벌어진다
BOSS_R = 4.0
BOSS_Y0 = 9.0
SEAT_R = (LED_FLANGE_D + LED_CLEAR) / 2
SEAT_Y0 = BOSS_TOP - SEAT_DEPTH
FUNNEL_Y0 = 11.0         # 다리가 앞뒤로 꺾여 들어가는 깔때기 (포켓 위쪽 끝에서 0.8mm 이상 떨어짐)

SPLICE_Y = (-1.0, 7.0)   # ① 압착 이음부: LED 캐소드 다리와 연장 다리가 나란히 눕는 구간
ANODE_W = 0.8            # ② 애노드 다리 홈 폭
ANODE_DEPTH = 0.45       # ② 뒷벽 안쪽 홈 깊이 (다리가 0.05mm 튀어나와 배터리를 누른다)
ANODE_Y_END = -4.0
WINDOW_W = 1.2           # ③ (−) 접점 창
WINDOW_Y = (-3.0, 1.0)
WIRE_B_Y_TOP = 4.0       # 철사 B 홈 위쪽 끝 (창 위 3mm에서 철사 끝을 붙잡는다)

NOSE_BASE_Y = -9.0
NOSE_BASE_W = 10.0
NOSE_LEN = 8.0
Y_TIP = -(CASE_R + NOSE_LEN)
TIP_WALL = 0.8
NOSE_TIP_T = 2.0         # 노즈 끝 두께 (시험편과 같음). 뒷면은 45°로 깎아 서포트 없이 인쇄된다.

TONGUE_X0 = 5.0          # 걸림턱 혀: 뒷판을 두 줄로 갈라 만든 외팔보
TONGUE_HALF_W = 2.0
SLIT_W = 0.6
DETENT_H = 0.5           # 혀 위의 턱 높이 (배터리 가장자리 바로 바깥)
DETENT_X = (POCKET_R + 0.05, POCKET_R + 1.05)

MARK_Y = -6.0            # ▶| 각인 (삼각형은 A 왼쪽, 막대는 B 오른쪽)
MARK_DEPTH = 0.4


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def prism_xy(points, z0, z1):
    """XY 다각형을 z0~z1로 돌출."""
    pts = [V(x, y, z0) for x, y in points]
    return Part.Face(Part.makePolygon(pts + pts[:1])).extrude(V(0, 0, z1 - z0))


def build():
    case = Part.makeCylinder(CASE_R, TOTAL_T)
    boss = Part.makeCylinder(BOSS_R, BOSS_TOP - BOSS_Y0, V(WIRE_A_X, BOSS_Y0, LED_Z), V(0, 1, 0))
    boss = boss.common(box(-50, 50, -50, 50, 0, 50))  # 뒷면은 평평하게

    tip_w = PROBE_SPACING + GROOVE_W + 2 * TIP_WALL
    nose = prism_xy([(-NOSE_BASE_W / 2, NOSE_BASE_Y), (NOSE_BASE_W / 2, NOSE_BASE_Y),
                     (tip_w / 2, Y_TIP), (-tip_w / 2, Y_TIP)], 0, TOTAL_T)
    zc = TOTAL_T - NOSE_TIP_T
    chamfer = Part.Face(Part.makePolygon([V(-10, Y_TIP - 1, zc + 1), V(-10, Y_TIP - 1, -1),
                                          V(-10, Y_TIP + zc + 1, -1), V(-10, Y_TIP - 1, zc + 1)]))
    nose = nose.cut(chamfer.extrude(V(20, 0, 0)))

    body = case.fuse([boss, nose])

    hw = GROOVE_W / 2
    cuts = [
        Part.makeCylinder(POCKET_R, POCKET_T, V(0, 0, POCKET_Z0)),               # 배터리 포켓
        box(0, CASE_R + 1, -POCKET_R, POCKET_R, POCKET_Z0, POCKET_Z1),           # 옆 슬롯 (오른쪽)
        Part.makeCylinder(SEAT_R, SEAT_DEPTH + 1, V(WIRE_A_X, SEAT_Y0, LED_Z), V(0, 1, 0)),  # LED 플랜지 자리
        # ① 철사 A: 앞면 홈 (LED 받침 앞쪽까지 열린 슬롯), 이음부는 두 가닥 폭, 캐소드 깔때기
        box(WIRE_A_X - hw, WIRE_A_X + hw, Y_TIP - 1, SEAT_Y0 + 0.01, GROOVE_Z, 20),
        box(WIRE_A_X - hw - GROOVE_W, WIRE_A_X + hw, SPLICE_Y[0], SPLICE_Y[1], GROOVE_Z, 20),
        box(WIRE_A_X - 0.5, WIRE_A_X + 0.5, FUNNEL_Y0, SEAT_Y0 + 0.01, LED_Z + 0.8, 20),
        # 철사 B: 앞면 홈 + ③ (−) 접점 창
        box(WIRE_B_X - hw, WIRE_B_X + hw, Y_TIP - 1, WIRE_B_Y_TOP, GROOVE_Z, 20),
        box(WIRE_B_X - WINDOW_W / 2, WIRE_B_X + WINDOW_W / 2, WINDOW_Y[0], WINDOW_Y[1], POCKET_Z1 - 0.1, 20),
        # ② 애노드: 깔때기 → 위쪽 벽 속 터널 → 뒷벽 안쪽 홈
        box(WIRE_A_X - 0.5, WIRE_A_X + 0.5, FUNNEL_Y0, SEAT_Y0 + 0.01, 0.55, LED_Z - 0.7),
        box(WIRE_A_X - ANODE_W / 2, WIRE_A_X + ANODE_W / 2, BOSS_Y0 + 0.5, FUNNEL_Y0 + 0.01, 0.55, 1.35),
        box(WIRE_A_X - ANODE_W / 2, WIRE_A_X + ANODE_W / 2, ANODE_Y_END, POCKET_R,
            BACK_T - ANODE_DEPTH, BACK_T + 0.01),
        # 걸림턱 혀를 만드는 두 줄 틈
        box(TONGUE_X0, CASE_R + 1, TONGUE_HALF_W, TONGUE_HALF_W + SLIT_W, -1, BACK_T + 0.01),
        box(TONGUE_X0, CASE_R + 1, -TONGUE_HALF_W - SLIT_W, -TONGUE_HALF_W, -1, BACK_T + 0.01),
        # ▶| 각인
        prism_xy([(-4.6, MARK_Y - 1), (-4.6, MARK_Y + 1), (-2.6, MARK_Y)], TOTAL_T - MARK_DEPTH, TOTAL_T + 1),
        box(2.6, 3.1, MARK_Y - 1, MARK_Y + 1, TOTAL_T - MARK_DEPTH, TOTAL_T + 1),
    ]
    body = body.cut(cuts)

    x0, x1 = DETENT_X
    bump = Part.Face(Part.makePolygon([V(x0, -1.5, BACK_T - 0.01), V(x1, -1.5, BACK_T - 0.01),
                                       V((x0 + x1) / 2, -1.5, BACK_T + DETENT_H), V(x0, -1.5, BACK_T - 0.01)]))
    return body.fuse(bump.extrude(V(0, 3.0, 0))).removeSplitter()


try:
    shape = build()
    if not shape.isValid() or len(shape.Solids) != 1:
        raise RuntimeError(f"유효하지 않은 형상 (솔리드 {len(shape.Solids)}개)")
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.05)
    if not mesh.isSolid():
        raise RuntimeError("STL 메시가 닫혀 있지 않음")
    os.makedirs(os.path.dirname(OUT_STL), exist_ok=True)
    mesh.write(OUT_STL)
    doc = App.newDocument("tester")
    doc.addObject("Part::Feature", "Tester").Shape = shape
    doc.recompute()
    doc.saveAs(OUT_FCSTD)
    bb = shape.BoundBox
    print(f"BUILD OK {OUT_STL} ({mesh.CountFacets} facets, "
          f"{bb.XLength:.1f}x{bb.YLength:.1f}x{bb.ZLength:.1f}mm) + {OUT_FCSTD}", flush=True)
except Exception as e:
    print(f"BUILD FAIL: {e!r}", flush=True)
    sys.exit(1)
sys.exit(0)
