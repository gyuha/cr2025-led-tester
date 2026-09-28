# 테스터 본체 치수 검사: stl/tester.stl 에 광선을 쏴서 재료 구간을 직접 잰다.
# 실행: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd cad/check_tester.py
# 통과하면 "CHECK OK", 실패하면 "CHECK FAIL: <이유>" 를 출력하고 종료 코드 1.
# (freecadcmd는 잡히지 않은 예외에도 0을 돌려주므로 판정은 출력 줄로 한다.)
# 기대값 덮어쓰기: EXPECT_PROBE_SPACING=2.2
#
# 애노드(②) 경로는 배터리 (+) 캔에 닿는 것이 정상이라 절연 검사 대상이 아니다.
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import Mesh

from params import (BACK_T, BATTERY_D, BATTERY_T, BOSS_TOP, FRONT_T, GROOVE_DEPTH, GROOVE_W,
                    INSULATION_MIN, LED_CLEAR, LED_FLANGE_D, LED_Z, NEG_CONTACT_LEN, NEG_PASS_LEN,
                    NEG_PIN_W, NEG_SAFE_R, POCKET_CLEAR_D, POCKET_CLEAR_T, PROBE_SPACING, SEAT_DEPTH)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "tester.stl")
TOL = 0.01          # 평면끼리 잰 치수
TOL_CURVED = 0.05   # 원을 가로지르는 치수 (다각형 근사 오차)
JIT = 0.0123        # 광선이 삼각형 모서리를 정확히 지나지 않게 살짝 비킨다
AXES = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


def spans(mesh, x, y, z, axis):
    """(x, y, z)를 지나는 axis 방향 직선이 재료 안을 지나는 구간 목록 [(시작, 끝)]."""
    k = "xyz".index(axis)
    o = [x, y, z]
    o[k] = -100.0
    ts = sorted({round(p[k], 7) for p in mesh.foraminate(tuple(o), AXES[axis]).values()})
    if len(ts) % 2:
        raise AssertionError(f"닫히지 않은 교차 ({axis}축, {x:.2f},{y:.2f},{z:.2f})")
    return list(zip(ts[0::2], ts[1::2]))


def gaps(sp):
    return [(a[1], b[0]) for a, b in zip(sp, sp[1:])]


def gap_at(sp, t):
    for g in gaps(sp):
        if g[0] < t < g[1]:
            return g
    raise AssertionError(f"{t:.2f} 위치에 빈 공간 없음")


def expect(what, got, want, tol=TOL):
    if abs(got - want) > tol:
        raise AssertionError(f"{what}: {got:.3f} (기대 {want:.3f} ±{tol})")


def at_least(what, got, want, tol=TOL):
    if got < want - tol:
        raise AssertionError(f"{what}: {got:.3f} (기대 ≥ {want:.3f})")


try:
    if not os.path.isfile(STL):
        raise AssertionError(f"STL 없음: {STL}")
    mesh = Mesh.Mesh(STL)
    if mesh.CountFacets == 0 or not mesh.isSolid() or mesh.hasNonManifolds():
        raise AssertionError("STL 메시가 닫힌 솔리드가 아님")
    if len(mesh.getSeparateComponents()) != 1:
        raise AssertionError(f"조각 {len(mesh.getSeparateComponents())}개 (기대 1개)")
    bb = mesh.BoundBox
    report = []

    # 배터리 포켓: 지름(Y 방향 현)과 두께(Z)
    pocket_mid = BACK_T + (BATTERY_T + POCKET_CLEAR_T) / 2
    g = gap_at(spans(mesh, -JIT, 0, pocket_mid, "y"), 0)
    at_least("포켓 지름", g[1] - g[0], BATTERY_D + POCKET_CLEAR_D, TOL_CURVED)
    report.append(f"포켓 Ø{g[1] - g[0]:.2f}")
    g = gap_at(spans(mesh, -5 - JIT, -5 - JIT, 0, "z"), pocket_mid)
    at_least("포켓 두께", g[1] - g[0], BATTERY_T + POCKET_CLEAR_T)
    pocket_top = g[1]
    report.append(f"두께 {g[1] - g[0]:.2f}")

    # 노즈 끝: 앞면 높이를 재고, 그 바로 아래에서 두 홈의 간격과 폭을 잰다
    want_spacing = float(os.environ.get("EXPECT_PROBE_SPACING", PROBE_SPACING))
    y_tip = bb.YMin + 0.5 + JIT
    front = spans(mesh, JIT, y_tip, 0, "z")[-1][1]
    g = gaps(spans(mesh, 0, y_tip, front - 0.2, "x"))
    if len(g) != 2:
        raise AssertionError(f"노즈 끝 홈 {len(g)}개 (기대 2개)")
    (a0, a1), (b0, b1) = g
    spacing = (b0 + b1) / 2 - (a0 + a1) / 2
    expect("끝 A–B 간격", spacing, want_spacing)
    expect("끝 A 홈 폭", a1 - a0, GROOVE_W)
    expect("끝 B 홈 폭", b1 - b0, GROOVE_W)
    report.append(f"끝 A–B {spacing:.3f}")

    # 철사 A·B 홈 아래 절연층, 그리고 (−) 접점 구멍의 위치
    xa, xb = -PROBE_SPACING / 2, PROBE_SPACING / 2
    lines = {"철사 A": xa + JIT, "철사 A 이음부": xa - GROOVE_W + JIT, "철사 B": xb + JIT}
    r_in = (BATTERY_D + POCKET_CLEAR_D) / 2 - 0.3
    thinnest, windows = 99.0, []
    for name, x in lines.items():
        for i in range(int(2 * r_in / 0.25)):
            y = -r_in + i * 0.25 + JIT
            if x * x + y * y > r_in * r_in:
                continue
            sp = spans(mesh, x, y, 0, "z")
            above = [s for s in sp if s[0] >= pocket_top - 0.05]
            if not above or above[0][0] > pocket_top + 0.05:
                windows.append((name, x, y))       # 포켓 천장이 열린 곳 (철사 B의 통과 구멍·접촉 홈)
                continue
            thinnest = min(thinnest, above[0][1] - above[0][0])
            at_least(f"{name} 절연층 (y={y:.2f})", above[0][1] - above[0][0], INSULATION_MIN)
    report.append(f"절연 최소 {thinnest:.2f}")
    if any(n != "철사 B" for n, _, _ in windows):
        raise AssertionError(f"철사 A 선에서 포켓이 드러남: {[w for w in windows if w[0] != '철사 B'][:3]}")

    # ③ 철사 B 경로의 두 부분을 따로 잰다.
    #  (1) 앞판을 관통하는 구멍: 철사 B 선 위의 통과 구멍 하나뿐, 폭 NEG_PIN_W, 길이 ≤ NEG_PASS_LEN
    #      (큰 창에 V자로 꺾으면 붙잡을 곳이 없어 고정되지 않는다)
    #  (2) 포켓 천장의 열린 곳: 전부 (−) 안전 반경 안, 철사 B 선을 따라 길이 NEG_PASS_LEN + NEG_CONTACT_LEN
    #      (꽂힌 끝 한 점이 아니라 선으로 (−) 면에 닿아야 접촉이 충분하다)
    groove_floor = pocket_top + FRONT_T - GROOVE_DEPTH
    through = []
    for i in range(int(2 * r_in / 0.1)):
        y = -r_in + i * 0.1 + JIT
        for x0, x1 in gaps(spans(mesh, 0, y, groove_floor - 0.1, "x")):
            if abs(x0) > r_in or abs(x1) > r_in:
                continue
            if max(math.hypot(x0, y), math.hypot(x1, y)) > NEG_SAFE_R:
                raise AssertionError(f"앞판 관통 구멍이 (−) 안전 반경 밖: ({x0:.2f}~{x1:.2f}, {y:.2f})")
            if not x0 < xb < x1:
                raise AssertionError(f"철사 B 선이 아닌 곳에 앞판 관통 구멍: ({x0:.2f}~{x1:.2f}, {y:.2f})")
            expect(f"통과 구멍 폭 (y={y:.2f})", x1 - x0, NEG_PIN_W)
            through.append(y)
    if not through:
        raise AssertionError("철사 B 선 위에 통과 구멍이 없음")
    if max(through) - min(through) > NEG_PASS_LEN:
        raise AssertionError(f"통과 구멍 길이가 {NEG_PASS_LEN}mm보다 김: {min(through):.2f}~{max(through):.2f}")

    ceiling = pocket_top + 0.1
    for i in range(int(2 * r_in / 0.2)):
        y = -r_in + i * 0.2 + JIT
        for x0, x1 in gaps(spans(mesh, 0, y, ceiling, "x")):
            if abs(x0) > r_in or abs(x1) > r_in:
                continue
            if max(math.hypot(x0, y), math.hypot(x1, y)) > NEG_SAFE_R:
                raise AssertionError(f"포켓 천장 열린 곳이 (−) 안전 반경 밖: ({x0:.2f}~{x1:.2f}, {y:.2f})")
    run = max((g for g in gaps(spans(mesh, xb + JIT, 0, ceiling, "y")) if abs(g[0]) < r_in and abs(g[1]) < r_in),
              key=lambda g: g[1] - g[0], default=(0, 0))
    at_least("(−) 면 접촉 홈 길이 (통과 구멍 포함)", run[1] - run[0], NEG_PASS_LEN + NEG_CONTACT_LEN)
    report.append(f"통과 구멍 {NEG_PIN_W:g}mm · (−) 접촉 {run[1] - run[0] - NEG_PASS_LEN:.1f}mm ≤ r{NEG_SAFE_R:g}")

    # LED 플랜지 자리 지름
    g = gap_at(spans(mesh, 0, BOSS_TOP - SEAT_DEPTH / 2 + JIT, LED_Z + JIT, "x"), xa)
    expect("LED 자리 지름", g[1] - g[0], LED_FLANGE_D + LED_CLEAR, TOL_CURVED)
    report.append(f"LED 자리 Ø{g[1] - g[0]:.2f}")

    print("CHECK OK " + " · ".join(report), flush=True)
except Exception as e:
    print(f"CHECK FAIL: {e}", flush=True)
    sys.exit(1)
sys.exit(0)
