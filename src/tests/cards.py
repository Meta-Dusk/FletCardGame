import flet as ft
import random
from pathlib import Path

ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"
WHITE_CARDS_PATH = ASSETS_PATH / "images" / "cards" / "white"

def get_file_names(path: Path):
    return [f.name for f in path.iterdir() if f.is_file()]

def format_card(src: str):
    return (WHITE_CARDS_PATH / src).as_posix()

def pick_random_src(list: list):
    rnd_card: str = random.choice(list)
    print(f"Picked {rnd_card} from deck.")
    return format_card(rnd_card)

def pick_then_del(list: list):
    rnd_card: str = random.choice(list) if len(list) > 0 else None
    print(f"Picked {rnd_card} from deck of size {len(list)}. Also removing from deck...")
    list.remove(rnd_card)
    print(f"Deck is now {len(list)} cards after removal.")
    return format_card(rnd_card)

def error_container(text: str):
    return ft.Container(
        content=ft.Text(text, color=ft.Colors.ERROR),
        bgcolor=ft.Colors.ERROR_CONTAINER,
        border=ft.Border.all(2, ft.Colors.ON_ERROR_CONTAINER),
        padding=5, border_radius=5, width=655/4, height=930/4,
        alignment=ft.Alignment.CENTER
    )

def before_test(page: ft.Page):
    page.title = "Test 004"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.decoration = ft.BoxDecoration(
        bgcolor=ft.Colors.PRIMARY, border=ft.Border.all(5, ft.Colors.ON_PRIMARY)
    )
    
    page.window.frameless = True

async def test(page: ft.Page):
    await page.window.center()
    
    async def on_keyboard_event(e: ft.KeyboardEvent):
        if e.key == "Escape":
            await page.window.close()
        if e.key == "`":
            nonlocal card_list
            print("Clearing deck")
            card_list = []
    
    def on_click(_):
        nonlocal rnd_card
        rnd_card = pick_then_del(card_list)
        if rnd_card is None:
            test_card_anim_sw.content = error_container("DECK EXHAUSTED")
        else:
            test_card_img.src = rnd_card
        test_card.update()
    
    card_list = get_file_names(WHITE_CARDS_PATH)
    rnd_card = pick_then_del(card_list)
    
    test_card_img = ft.Image(
        src=rnd_card,
        width=655/4, height=930/4,
        fit=ft.BoxFit.CONTAIN,
        error_content=error_container("SOURCE ERROR"),
        gapless_playback=True
    )
    test_card_anim_sw = ft.AnimatedSwitcher(
        content=test_card_img,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=500,
        reverse_duration=250,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN
    )
    test_card = ft.Draggable(
        content=test_card_anim_sw, group="card",
    )
    
    test_button = ft.Button(
        content=ft.Text("Randomize Card"),
        on_click=on_click
    )
    
    card_row = ft.Row(
        controls=[test_card, test_button],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END
    )
    
    page.add(card_row)
    page.on_keyboard_event = on_keyboard_event
    
    
if __name__ == "__main__":
    ft.run(main=test, before_main=before_test, assets_dir="src/assets")