from src.shop import SHOP_ITEMS, ShopItem


def test_shop_has_six_items():
    assert len(SHOP_ITEMS) == 6


def test_shop_has_three_upgrades():
    assert sum(1 for i in SHOP_ITEMS if i.kind == "upgrade") == 3


def test_shop_has_three_consumables():
    assert sum(1 for i in SHOP_ITEMS if i.kind == "consumable") == 3


def test_upgrades_have_max_stacks():
    for item in SHOP_ITEMS:
        if item.kind == "upgrade":
            assert item.max_stacks is not None and item.max_stacks > 0


def test_consumables_have_no_max_stacks():
    for item in SHOP_ITEMS:
        if item.kind == "consumable":
            assert item.max_stacks is None


def test_shop_item_has_required_fields():
    item = SHOP_ITEMS[0]
    assert isinstance(item, ShopItem)
    assert item.name and item.kind and item.cost > 0 and item.description


def test_all_items_have_callable_apply():
    for item in SHOP_ITEMS:
        assert callable(item.apply)
