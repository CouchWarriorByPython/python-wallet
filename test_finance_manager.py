import pytest

from finance_manager import FinanceManager


@pytest.fixture
def finance_manager():
    manager = FinanceManager(data_file="test_data_file.json")
    return manager


def test_add_wallet(finance_manager):
    finance_manager.add_wallet("Test Wallet", 100.0, "USD")
    assert "Test Wallet" in finance_manager.wallets
    assert finance_manager.wallets["Test Wallet"].balance == 100.0
    assert finance_manager.wallets["Test Wallet"].currency == "USD"


def test_add_transaction(finance_manager):
    finance_manager.add_wallet("Test Wallet", 100.0, "USD")
    finance_manager.add_transaction("Test Wallet", "expense", "food", 20.0, "USD")

    assert len(finance_manager.transactions) == 1
    transaction = finance_manager.transactions[0]
    assert transaction.amount == 20.0
    assert transaction.category == "food"
    assert transaction.wallet_name == "Test Wallet"


def test_add_custom_category(finance_manager):
    finance_manager.add_custom_category("expense", "snacks", ["sweet", "salty"])
    assert "snacks" in finance_manager.custom_categories["expense"]
    assert "sweet" in finance_manager.available_tags["expense"]["snacks"]
    assert "salty" in finance_manager.available_tags["expense"]["snacks"]


def test_edit_custom_category(finance_manager):
    finance_manager.add_custom_category("expense", "snacks", ["sweet", "salty"])
    finance_manager.edit_custom_category("expense", "snacks", "refreshments")
    assert "refreshments" in finance_manager.custom_categories["expense"]
    assert "snacks" not in finance_manager.custom_categories["expense"]
    assert "refreshments" in finance_manager.available_tags["expense"]


def test_delete_custom_category(finance_manager):
    finance_manager.add_custom_category("expense", "snacks", ["sweet", "salty"])
    finance_manager.delete_custom_category("expense", "snacks")
    assert "snacks" not in finance_manager.custom_categories["expense"]
    assert "snacks" not in finance_manager.available_tags["expense"]


if __name__ == "__main__":
    pytest.main()
