from hearthstone.enums import CardType, GameTag
from hslog.export import BaseExporter

from ..simulator.entities import Card, Game, Player
from ..simulator.entity import get
from ..simulator.state import GameState


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


class GameStateExporter(BaseExporter):
    def __init__(self, packet_tree):
        super(GameStateExporter, self).__init__(packet_tree)
        self.game_state = GameState()

    def handle_create_game(self, packet):
        self.handle_full_entity(packet)
        for player in packet.players:
            self.handle_full_entity(player)

    def handle_full_entity(self, packet):
        create_kwargs = {
            tag.name.lower(): value
            for tag, value in packet.tags
            if isinstance(tag, GameTag)
        }
        if hasattr(packet, "card_id"):
            create_kwargs["card_id"] = packet.card_id

        # Get entity class according to card type
        new_entity = get(create_kwargs.get("cardtype"))()

        for key, value in create_kwargs.items():
            setattr(new_entity, key, value)
        self.game_state.entities[create_kwargs["entity_id"]] = new_entity

    def handle_show_entity(self, packet):
        update_kwargs = {
            tag.name.lower(): value
            for tag, value in packet.tags
            if isinstance(tag, GameTag)
        }
        update_kwargs["card_id"] = packet.card_id
        entity = self.game_state.entities[packet.entity]

        # Update entity class according to card type
        cardtype = update_kwargs.get("cardtype")
        if isinstance(cardtype, CardType):
            entity.__class__ = get(cardtype)

        for key, value in update_kwargs.items():
            setattr(entity, key, value)

    def handle_tag_change(self, packet):
        if not isinstance(packet.tag, GameTag):
            return
        if not isinstance(packet.entity, int):
            packet.entity = packet.entity.entity_id
        setattr(
            self.game_state.entities[packet.entity],
            packet.tag.name.lower(),
            packet.value,
        )
