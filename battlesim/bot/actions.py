try:
    import pyautogui
except KeyError:  # No GUI
    pass


def get_minion_position(offset: int, enemy=False):
    ENEMY_POSITION_Y = 400
    FRIENDLY_POSITION_Y = 600
    CENTER_X = 960
    OFFSET_PER_SLOT = 140

    return {
        "x": CENTER_X + int(OFFSET_PER_SLOT * offset),
        "y": ENEMY_POSITION_Y if enemy else FRIENDLY_POSITION_Y,
    }


def get_hero_position(enemy: bool = False):
    return {"x": 960, "y": 230 if enemy else 830}


def get_hero_power_position():
    return {"x": 1140, "y": 830}


def choose_hero(index: int):
    hero_position = {"x": 500 + 300 * index, "y": 540}
    pyautogui.click(**hero_position, duration=0.5)
    confirm_position = {"x": 960, "y": 830}
    pyautogui.click(**confirm_position, duration=0.5)


def buy_minion(index: int, total: int):
    # Drag minion to hero
    offset = index + (1 - total) / 2
    pyautogui.moveTo(**get_minion_position(offset, enemy=True))
    pyautogui.dragTo(duration=1, **get_hero_position())


def sell_minion(index: int, total: int):
    # Drag minion to bob
    offset = index + (1 - total) / 2
    pyautogui.moveTo(**get_minion_position(offset))
    pyautogui.dragTo(duration=1, **get_hero_position(enemy=False))


def play_card(index: int, total: int):
    pass


def tier_up():
    pyautogui.click(x=800, y=200)


def refresh():
    pyautogui.click(x=1130, y=200)


def freeze():
    pyautogui.click(x=1250, y=200)


def use_hero_power():
    pyautogui.click(**get_hero_power_position())
