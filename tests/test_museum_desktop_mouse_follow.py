from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "museum" / "dist" / "museum.js").read_text(encoding="utf-8")
HTML = (ROOT / "museum" / "dist" / "index.html").read_text(encoding="utf-8")


def test_desktop_mouse_follow_is_button_free_and_bounded():
    assert "finePointer=matchMedia('(pointer:fine)').matches" in APP
    assert "e.pointerType!=='mouse'" in APP
    assert "radius<=.12" in APP
    assert "gain=.38+.32*edge" in APP
    assert "dx*gain,dy*gain*.85" in APP
    assert "if(!desktop)c.setPointerCapture(e.pointerId)" in APP


def test_mobile_swipe_turn_remains_available():
    assert "const look=$('look-pad')" in APP
    assert "look.setPointerCapture(e.pointerId)" in APP
    assert "Swipe to turn" in HTML


def test_desktop_help_and_accessibility_describe_mouse_follow():
    assert "MOVE MOUSE TO LOOK" in APP
    assert "无需按住或拖动" in APP
    assert "without holding a button" in APP
    assert "Move the mouse to look on desktop" in HTML
