from hearthstone.enums import GameTag
from hslog.export import BaseExporter

from ..simulator.entities import Game, Player, Card


class SimulatorExporter(BaseExporter):
    game_class = Game

    def handle_create_game(self, packet):
        create_kwargs = {
            tag.name.lower(): value
            for tag, value in packet.tags
            if isinstance(tag, GameTag)
        }
        self.game = Game(**create_kwargs)
        self.game.entities[self.game.entity_id] = self.game
        for player in packet.players:
            self.handle_full_entity(player, entity_class=Player)

    def handle_full_entity(self, packet, entity_class=Card):
        create_kwargs = {
            tag.name.lower(): value
            for tag, value in packet.tags
            if isinstance(tag, GameTag)
        }
        if hasattr(packet, "card_id"):
            create_kwargs["card_id"] = packet.card_id
        new_entity = entity_class(**create_kwargs)
        self.game.entities[create_kwargs["entity_id"]] = new_entity
        new_entity.game = self.game

    def handle_show_entity(self, packet):
        update_kwargs = {
            tag.name.lower(): value
            for tag, value in packet.tags
            if isinstance(tag, GameTag)
        }
        update_kwargs["card_id"] = packet.card_id
        for key, value in update_kwargs.items():
            setattr(self.game.entities[packet.entity], key, value)

    def handle_tag_change(self, packet):
        if not isinstance(packet.tag, GameTag):
            return
        setattr(
            self.game.entities[packet.entity], packet.tag.name.lower(), packet.value
        )
