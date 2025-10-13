import flet as ft
import random
from pathlib import Path
from typing import Optional


ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"
WHITE_CARDS_PATH = ASSETS_PATH / "images" / "cards" / "white"


def get_file_names(path: Path) -> list[str]:
    return [f.name for f in path.iterdir() if f.is_file()]

def format_card(src: str) -> str:
    return (WHITE_CARDS_PATH / src).as_posix()

def pick_random_src(list: list) -> str:
    rnd_card: str = random.choice(list)
    print(f"Picked {rnd_card} from deck.")
    return format_card(rnd_card)

def pick_then_del(list: list) -> Optional[str]:
    deck_size = len(list)
    if not deck_size > 0:
        print("Deck already exhausted.")
        return None
    rnd_card: str = random.choice(list)
    print(f"Picked {rnd_card} from deck of size {deck_size}.", end=" ")
    list.remove(rnd_card)
    print(f"Deck is now {deck_size} cards after removal.")
    return format_card(rnd_card)

def error_container(text: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, color=ft.Colors.ERROR),
        bgcolor=ft.Colors.ERROR_CONTAINER,
        border=ft.Border.all(2, ft.Colors.ON_ERROR_CONTAINER),
        padding=5, border_radius=15, width=655/4, height=930/4,
        alignment=ft.Alignment.CENTER
    )

def empty_card_container() -> ft.Container:
    return ft.Container(
        bgcolor=ft.Colors.SECONDARY,
        border=ft.Border.all(2, ft.Colors.ON_SECONDARY),
        border_radius=15, width=655/4, height=930/4,
        alignment=ft.Alignment.CENTER
    )

def simple_anim_con(content: ft.Control) -> ft.AnimatedSwitcher:
    return ft.AnimatedSwitcher(
        content=content, duration=500, reverse_duration=250,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN
    )

def before_test(page: ft.Page) -> None:
    page.title = "Test 004"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.decoration = ft.BoxDecoration(
        bgcolor=ft.Colors.PRIMARY, border=ft.Border.all(5, ft.Colors.ON_PRIMARY)
    )
    
    page.window.title_bar_hidden = True

async def test(page: ft.Page) -> None:
    # == EVENT HANDLERS ==
    async def on_keyboard_event(e: ft.KeyboardEvent):
        if e.key == "Escape":
            print("Exiting app!")
            await page.window.close()
        if e.key == "`":
            nonlocal card_list
            print("Clearing deck")
            card_list = []
    
    def pick_card(_):
        nonlocal rnd_card, test_card
        rnd_card = pick_then_del(card_list)
        if rnd_card is None:
            test_card.content = error_container("DECK EXHAUSTED")
            test_card.max_simultaneous_drags = 0
            test_btn.disabled = True
        else:
            test_card_img.src = rnd_card
        test_card.update()
    
    def drag_will_accept(e: ft.DragWillAcceptEvent):
        card_cont: ft.Container = e.control.content
        card_cont.border = ft.Border.all(
            width=4,
            color=ft.Colors.PRIMARY if e.accept else ft.Colors.ERROR
        )
        card_cont.update()
    
    def drag_accept(e: ft.DragTargetEvent):
        src_anim_sw: ft.AnimatedSwitcher = e.src.content
        src_card_cont: ft.Image = src_anim_sw.content
        
        card_cont: ft.Container = e.control.content
        new_img = ft.Image(
            src=src_card_cont.src,
            fit=src_card_cont.fit,
            width=src_card_cont.width,
            height=src_card_cont.height
        )
        
        print(f"Setting {card_cont.content} to a new image copied from {src_card_cont.src}")
        
        card_cont.content = new_img
        card_cont.border = ft.Border.all(width=2, color=ft.Colors.ON_SECONDARY)
        card_cont.update()
    
    def drag_leave(e: ft.DragTargetLeaveEvent):
        card_cont: ft.Container = e.control.content
        card_cont.border = ft.Border.all(width=2, color=ft.Colors.ON_SECONDARY)
        card_cont.update()
    
    # == SETUP ==
    card_list = get_file_names(WHITE_CARDS_PATH)
    rnd_card = pick_then_del(card_list)
    
    # == CONTROLS ==
    # Card Component
    test_card_img = ft.Image(
        src=rnd_card, width=655/4, height=930/4,
        fit=ft.BoxFit.CONTAIN, gapless_playback=True,
        error_content=error_container("SOURCE ERROR")
    )
    test_card_anim_sw = simple_anim_con(test_card_img)
    test_card = ft.Draggable(
        content=test_card_anim_sw, group="card",
        on_drag_complete=pick_card,
        max_simultaneous_drags=1,
        content_when_dragging=empty_card_container()
    )
    
    # Card Handlers
    test_card_dest = ft.DragTarget(
        content=empty_card_container(),
        group="card",
        on_accept=drag_accept,
        on_leave=drag_leave,
        on_will_accept=drag_will_accept
    )
    
    # Buttons
    test_btn = ft.Button(
        content=ft.Text("Randomize Card"),
        on_click=pick_card
    )
    
    # Layout
    card_row = ft.Row(
        controls=[test_card, test_btn, test_card_dest],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END
    )
    draggable_win = ft.WindowDragArea(
        content=card_row, expand=True, maximizable=False
    )
    
    # Page Stuff
    page.add(draggable_win)
    page.on_keyboard_event = on_keyboard_event
    await page.window.center()
    
    
if __name__ == "__main__":
    ft.run(main=test, before_main=before_test, assets_dir="src/assets")