from ..card import Card


class RebornRite(Card):
    def start_of_combat(self):
        self.attached.reborn = True
