from ..entities import Enchantment


class RebornRite(Enchantment):
    def on_attached(self):
        self.attached_entity.reborn = True
