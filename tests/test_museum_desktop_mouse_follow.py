from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "museum" / "dist" / "museum.js").read_text(encoding="utf-8")
HTML = (ROOT / "museum" / "dist" / "index.html").read_text(encoding="utf-8")


def test_desktop_hover_is_stable_and_drag_turns():
    # A visitor must be able to move the cursor onto artwork without moving it.
    assert "followDesktopMouse" not in APP
    move = APP.split("c.addEventListener('pointermove'", 1)[1].split("c.addEventListener('pointerup'", 1)[0]
    assert "if(drag&&e.pointerId===drag.pointer)" in move
    assert "if(drag.moved>=8)" in move
    assert "else updateHover(e)" in move
    assert "stopTour(" not in move
    assert "c.setPointerCapture(e.pointerId)" in APP


def test_mobile_swipe_turn_remains_available():
    assert "const look=$('look-pad')" in APP
    assert "look.setPointerCapture(e.pointerId)" in APP
    assert "Swipe to turn" in HTML


def test_desktop_help_and_accessibility_describe_click_and_drag():
    assert "DRAG TO LOOK" in APP
    assert "按住左键拖动才转头" in APP
    assert "hold the left mouse button and drag to turn" in APP
    assert "Hold the left mouse button and drag to look on desktop" in HTML
