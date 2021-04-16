from hearthstone.cardxml import load


def setup_module(module):
    load()
    load(locale="zhCN")
