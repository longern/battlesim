import re

from hslog.parser import LogParser

from .exporter import SimulatorExporter

REROLL_BUTTON_REMOVED = (
    "TAG_CHANGE.*TB_BaconShop_8p_Reroll_Button.*value=REMOVEDFROMGAME"
)


def do_nothing(self):
    pass


class BattlegroundParser(LogParser):
    def __init__(self, callbacks: dict):
        super(BattlegroundParser, self).__init__()
        self.combat = False
        self.callbacks = callbacks

    def read_line(self, line: str):
        super().read_line(line)

        if "GameState" not in line:
            return

        if "tag=MULLIGAN_STATE value=INPUT" in line:
            self.callbacks.get("choose_hero", do_nothing)(self)
            return

        if "GameState.DebugPrintOptions() - id=" in line:
            self.callbacks.get("idle", do_nothing)(self)
            return

        if not self.combat and re.search(REROLL_BUTTON_REMOVED, line):
            self.combat = True
            return

        if not self.combat or "MAIN_START_TRIGGER" not in line:
            return

        self.combat = False

        self.callbacks.get("combat", do_nothing)(self)

    def export_game(self) -> SimulatorExporter.game_class:
        exporter = SimulatorExporter(self.games[-1])
        game = getattr(exporter.export(), "game", None)

        if not isinstance(game, SimulatorExporter.game_class):
            return None

        game.entities = {
            entity_id: entity
            for entity_id, entity in game.entities.items()
            if entity.zone.name != "REMOVEDFROMGAME"
        }

        return game
