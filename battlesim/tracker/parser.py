import re

from hslog.export import EntityTreeExporter
from hslog.parser import LogParser

REROLL_BUTTON_REMOVED = (
    "TAG_CHANGE.*TB_BaconShop_8p_Reroll_Button.*value=REMOVEDFROMGAME"
)


class BattlegroundParser(LogParser):
    def __init__(self, combat_callback):
        super(BattlegroundParser, self).__init__()
        self.combat = False
        self.combat_callback = combat_callback

    def read_line(self, line: str):
        super().read_line(line)

        if "GameState" not in line:
            return

        if not self.combat and re.search(REROLL_BUTTON_REMOVED, line):
            self.combat = True
            return

        if not self.combat or "MAIN_START_TRIGGER" not in line:
            return

        self.combat = False

        self.combat_callback(self)

    def export_game(self) -> EntityTreeExporter.game_class:
        exporter = EntityTreeExporter(self.games[-1])
        game = getattr(exporter.export(), "game", None)

        if not isinstance(game, EntityTreeExporter.game_class):
            return None

        game._entities = {
            entity_id: entity
            for entity_id, entity in game._entities.items()
            if entity.zone.name != "REMOVEDFROMGAME"
        }

        return game
