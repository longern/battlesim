from ..entities import Enchantment


class RebornRite(Enchantment):
    def on_attached(self):
        self.attached.reborn = True
