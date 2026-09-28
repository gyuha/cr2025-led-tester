# 노즈 시험편: 프로브 간격 변형 3종 + 홈 폭 띠 4종 → stl/nose-coupon.stl
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/coupon.py
# freecadcmd는 예외가 나도 종료 코드 0을 돌려주므로, 결과는 "BUILD OK" / "BUILD FAIL" 줄로 판단한다.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App
import MeshPart
import Part

from params import FONT, GROOVE_DEPTH

V = App.Vector
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "stl", "nose-coupon.stl")

SPACING_VARIANTS = (2.2, 2.4, 2.6)          # 노즈 두 홈의 중심 간 거리
GROOVE_W_VARIANTS = (0.4, 0.5, 0.6, 0.7)    # 홈 폭 띠
NOSE_GROOVE_W = 0.6  # 노즈 변형의 홈 폭 (시험 당시 값으로 고정, params.GROOVE_W와 분리)
PLATE_T = 2.0        # 시험편 두께 (바닥에 눕혀 인쇄)
TAB_W = 12.0         # 손잡이 폭
TAB_LEN = 10.0       # 손잡이 길이
NOSE_LEN = 12.0      # 손잡이 끝에서 노즈 끝까지
TIP_WALL = 0.8       # 노즈 끝에서 홈 바깥쪽 벽 두께
GROOVE_START = 6.0   # 홈이 시작하는 위치 (그 앞은 라벨 자리)
LABEL_H = 3.5        # 각인 글자 높이
LABEL_DEPTH = 0.4    # 각인 깊이
PIECE_PITCH = 16.0   # 노즈 조각 사이 간격
STRIP_PITCH = 9.0    # 홈 폭 띠의 홈 사이 간격 (라벨끼리 붙지 않게)
STRIP_LEN = 16.0     # 홈 폭 띠 길이
STRIP_Y = -22.0      # 홈 폭 띠 위치 (노즈 조각들 아래)


def label(text, cx, cy):
    """윗면에 새길 글자 솔리드 (중심 cx, cy)."""
    chars = Part.makeWireString(text, FONT, LABEL_H, 0)
    faces = [Part.makeFace(wires, "Part::FaceMakerBullseye") for wires in chars]
    comp = Part.makeCompound(faces)
    bb = comp.BoundBox
    comp.translate(V(cx - (bb.XMin + bb.XMax) / 2, cy - (bb.YMin + bb.YMax) / 2, PLATE_T - LABEL_DEPTH))
    return comp.extrude(V(0, 0, LABEL_DEPTH + 1))


def groove(cx, w, y0, y1):
    """윗면에서 파 내려가는 철사 홈."""
    return Part.makeBox(w, y1 - y0, GROOVE_DEPTH + 1, V(cx - w / 2, y0, PLATE_T - GROOVE_DEPTH))


def nose(spacing, x0):
    """손잡이 + 끝으로 갈수록 좁아지는 노즈, 홈 두 줄은 노즈 끝으로 열려 있다."""
    cx = x0 + TAB_W / 2
    tip_w = spacing + NOSE_GROOVE_W + 2 * TIP_WALL
    y_tip = TAB_LEN + NOSE_LEN
    tab = Part.makeBox(TAB_W, TAB_LEN, PLATE_T, V(x0, 0, 0))
    outline = Part.makePolygon([V(x0, TAB_LEN, 0), V(x0 + TAB_W, TAB_LEN, 0),
                                V(cx + tip_w / 2, y_tip, 0), V(cx - tip_w / 2, y_tip, 0),
                                V(x0, TAB_LEN, 0)])
    body = tab.fuse(Part.Face(outline).extrude(V(0, 0, PLATE_T))).removeSplitter()
    for dx in (-spacing / 2, spacing / 2):
        body = body.cut(groove(cx + dx, NOSE_GROOVE_W, GROOVE_START, y_tip + 1))
    return body.cut(label(f"{spacing:.1f}", cx, GROOVE_START / 2))


def strip():
    """홈 폭 띠: 폭이 다른 홈 4줄, 각 홈 앞에 폭을 새긴다."""
    body = Part.makeBox(len(GROOVE_W_VARIANTS) * STRIP_PITCH, STRIP_LEN, PLATE_T, V(0, STRIP_Y, 0))
    for i, w in enumerate(GROOVE_W_VARIANTS):
        cx = (i + 0.5) * STRIP_PITCH
        body = body.cut(groove(cx, w, STRIP_Y + GROOVE_START, STRIP_Y + STRIP_LEN + 1))
        body = body.cut(label(f"{w:.1f}", cx, STRIP_Y + GROOVE_START / 2))
    return body


try:
    pieces = [nose(s, i * PIECE_PITCH) for i, s in enumerate(SPACING_VARIANTS)] + [strip()]
    for p in pieces:
        if not p.isValid() or len(p.Solids) != 1:
            raise RuntimeError("유효하지 않은 형상")
    mesh = MeshPart.meshFromShape(Shape=Part.makeCompound(pieces), LinearDeflection=0.01, AngularDeflection=0.1)
    if not mesh.isSolid():
        raise RuntimeError("STL 메시가 닫혀 있지 않음")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    mesh.write(OUT)
    print(f"BUILD OK {OUT} ({mesh.CountFacets} facets)", flush=True)
except Exception as e:
    print(f"BUILD FAIL: {e!r}", flush=True)
    sys.exit(1)
sys.exit(0)
