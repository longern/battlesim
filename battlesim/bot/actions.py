import logging

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
    logging.info("Buy minion %d in %d minions", index, total)
    offset = index + (1 - total) / 2
    pyautogui.moveTo(duration=1, **get_minion_position(offset, enemy=True))
    pyautogui.dragTo(duration=1, button="left", **get_hero_position())


def sell_minion(index: int, total: int):
    # Drag minion to bob
    logging.info("Sell minion %d in %d minions", index, total)
    offset = index + (1 - total) / 2
    pyautogui.moveTo(duration=1, **get_minion_position(offset))
    pyautogui.dragTo(duration=1, button="left", **get_hero_position(enemy=True))


def play_card(index: int, total: int):
    pyautogui.moveTo(x=920, y=1000, duration=1)
    pyautogui.dragTo(duration=1, button="left", **get_minion_position(0, enemy=False))


def choose(index: int, total: int):
    pass


def tier_up():
    logging.info("Tier up")
    pyautogui.click(x=800, y=200, duration=1)


def refresh():
    logging.info("Refresh")
    pyautogui.click(x=1130, y=200, duration=1)


def freeze():
    logging.info("Freeze")
    pyautogui.click(x=1250, y=200, duration=1)


def use_hero_power():
    pyautogui.click(**get_hero_power_position())
