# 노즈 시험편 치수 검사: stl/nose-coupon.stl 을 단면으로 잘라 홈 위치와 폭을 직접 잰다.
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/check_coupon.py
# 통과하면 "CHECK OK", 실패하면 "CHECK FAIL: <이유>" 를 출력하고 종료 코드 1.
# (freecadcmd는 잡히지 않은 예외에도 0을 돌려주므로 판정은 출력 줄로 한다.)
# 기대값 덮어쓰기: EXPECT_SPACINGS=2.2,2.4,2.6  EXPECT_STRIP_WIDTHS=0.4,0.5,0.6,0.7  EXPECT_NOSE_GROOVE_W=0.6
import os
import sys

import Mesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "nose-coupon.stl")
TOL = 0.01
PROBE_BACK = 1.0    # 끝(YMax)에서 이만큼 안쪽 단면을 잰다
PROBE_DOWN = 0.2    # 윗면에서 이만큼 아래 높이를 따라 잰다


def floats(name, default):
    return [float(v) for v in os.environ.get(name, default).split(",")]


def gaps(mesh, y, z):
    """y 단면에서 높이 z를 따라 재료가 끊긴 구간(홈)의 (중심, 폭) 목록, 왼쪽부터."""
    xs = []
    for poly in mesh.crossSections([((0, y, 0), (0, 1, 0))], 1e-6, True)[0]:
        for a, b in zip(poly, poly[1:]):
            if (a.z - z) * (b.z - z) < 0:
                xs.append(a.x + (z - a.z) * (b.x - a.x) / (b.z - a.z))
    xs.sort()
    if not xs or len(xs) % 2:
        raise AssertionError(f"단면이 닫혀 있지 않음 (y={y:.2f}, z={z:.2f})")
    spans = list(zip(xs[0::2], xs[1::2]))
    return [((l + r) / 2, r - l) for (_, l), (r, _) in zip(spans, spans[1:])]


def expect(what, got, want):
    if abs(got - want) > TOL:
        raise AssertionError(f"{what}: {got:.3f} (기대 {want:.3f} ±{TOL})")


try:
    if not os.path.isfile(STL):
        raise AssertionError(f"STL 없음: {STL}")
    mesh = Mesh.Mesh(STL)
    if mesh.CountFacets == 0 or not mesh.isSolid() or mesh.hasNonManifolds():
        raise AssertionError("STL 메시가 닫힌 솔리드가 아님")

    want_spacings = floats("EXPECT_SPACINGS", "2.2,2.4,2.6")
    want_strip = floats("EXPECT_STRIP_WIDTHS", "0.4,0.5,0.6,0.7")
    want_nose_w = floats("EXPECT_NOSE_GROOVE_W", "0.6")[0]
    parts = mesh.getSeparateComponents()
    strips = [p for p in parts if p.BoundBox.YMax < 0]
    noses = sorted((p for p in parts if p.BoundBox.YMin > -1e-6), key=lambda p: p.BoundBox.XMin)
    if len(noses) != len(want_spacings) or len(strips) != 1:
        raise AssertionError(f"조각 수: 노즈 {len(noses)}개, 홈 폭 띠 {len(strips)}개")

    report = []
    for i, (p, want) in enumerate(zip(noses, want_spacings), 1):
        bb = p.BoundBox
        g = gaps(p, bb.YMax - PROBE_BACK, bb.ZMax - PROBE_DOWN)
        if len(g) != 2:
            raise AssertionError(f"노즈 {i}: 홈 {len(g)}개 (기대 2개)")
        spacing = g[1][0] - g[0][0]
        expect(f"노즈 {i} 간격", spacing, want)
        for _, w in g:
            expect(f"노즈 {i} 홈 폭", w, want_nose_w)
        report.append(f"노즈{i} 간격 {spacing:.3f}")

    bb = strips[0].BoundBox
    g = gaps(strips[0], bb.YMax - PROBE_BACK, bb.ZMax - PROBE_DOWN)
    if len(g) != len(want_strip):
        raise AssertionError(f"홈 폭 띠: 홈 {len(g)}개 (기대 {len(want_strip)}개)")
    for (_, w), want in zip(g, want_strip):
        expect(f"홈 폭 띠 {want}", w, want)
    report.append("띠 " + "/".join(f"{w:.3f}" for _, w in g))

    print("CHECK OK " + " · ".join(report), flush=True)
except Exception as e:
    print(f"CHECK FAIL: {e}", flush=True)
    sys.exit(1)
sys.exit(0)
