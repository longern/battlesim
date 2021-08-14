from battlesim.simulator.state import GameState, g
from battlesim.tracker.exporter import GameStateExporter

from .logfile import LogStream, get_log_path
from .parser import BattlegroundParser

def combat_callback(parser: BattlegroundParser):
    exporter = GameStateExporter(parser.games[-1])
    gs: GameState = getattr(exporter.export(), "game_state", None)

    gs.entities = {
        entity_id: entity
        for entity_id, entity in gs.entities.items()
        if entity.zone.name != "REMOVEDFROMGAME"
    }

    g.set(gs)
    print(gs)


def main():
    parser = BattlegroundParser({"combat": combat_callback})
    parser.read(LogStream(get_log_path()))


if __name__ == "__main__":
    main()
