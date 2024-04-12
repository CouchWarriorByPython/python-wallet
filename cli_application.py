import argparse
import os
import random
from collections import OrderedDict

from finance_manager import FinanceManager


class FinanceCLI:
    def __init__(self, manager):
        self.manager = manager
        self.actions = OrderedDict(
            [
                ("1", self.add_wallet),
                ("2", self.set_default_wallet),
                ("3", self.add_transaction),
                ("4", self.edit_transaction),
                ("5", self.delete_transaction),
                ("6", self.list_wallet_transactions),
                ("7", self.list_all_transactions),
                ("8", self.search_expenses_by_tag),
                ("9", self.add_custom_category),
                ("10", self.edit_custom_category),
                ("11", self.delete_custom_category),
                ("12", self.exit),
            ]
        )

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="Interactive CLI for Finance Manager"
        )
        parser.add_argument(
            "--data_file",
            help="Path to the data file",
            default=os.getenv("FINANCE_MANAGER_DATA_FILE", "finance_data.json"),
        )
        return parser.parse_args()

    def main_menu(self):
        print("\nAvailable Commands:")
        for key, action in self.actions.items():
            print(f"{key}: {action.__doc__}")
        return input("Select an option: ")

    def run(self):
        while True:
            choice = self.main_menu()
            action = self.actions.get(choice)
            if action:
                action()
            else:
                print("Invalid option. Please try again.")

    def add_wallet(self):
        """Add Wallet"""
        name = input("Wallet Name: ")
        initial_balance = float(input("Initial Balance: "))
        currency = input("Currency (default USD): ") or "USD"
        self.manager.add_wallet(name, initial_balance, currency)

    def add_tag(self, transaction_type, category):
        try:
            default_tags = self.manager.get_available_tags[transaction_type][category]
        except Exception as e:
            print("You selected wrong combination Transaction Type + Category\n", e)

        print(
            f"\nDefault tags for ⤵\nTransaction type - {transaction_type}\nCategory - {category}: {', '.join(default_tags)}"
        )
        tags_input = input("Tags (comma-separated, leave blank for defaults): ").strip()
        return tags_input.split(",") if tags_input else random.choice(default_tags)

    def set_default_wallet(self):
        """Set Default Wallet"""
        name = input("Default Wallet Name: ")
        self.manager.set_default_wallet(name)

    def add_transaction(self):
        """Add Transaction"""
        wallet_name = (
            input("Wallet Name (leave blank for default): ")
            or self.manager.get_default_wallet_name()
        )
        transaction_type = input("Type (expense/income): ").lower()
        categories = self.manager.list_categories
        category = input(
            "\nAvailable categories ⤵\n"
            f"{transaction_type.capitalize()}: {categories(transaction_type)}\n"
            "Select your category: "
        )
        amount = float(input("Amount: "))
        currency = input("Currency (default USD): ") or "USD"
        date = input("Date (YYYY-MM-DD, leave blank for today): ") or None
        tags = self.add_tag(transaction_type, category)

        self.manager.add_transaction(
            wallet_name, transaction_type, category, amount, currency, date, tags
        )

    def edit_transaction(self):
        """Edit Transaction"""
        transaction_id = int(input("Transaction ID to edit: "))
        transaction = [t for t in self.manager.transactions if t.id == transaction_id]
        if transaction:
            transaction_data = transaction[0]

            transaction_type = (
                input("New Type (expense/income, leave blank to skip): ").lower()
                or transaction_data.transaction_type
            )
            category = (
                input("New Category (leave blank to skip): ")
                or transaction_data.category
            )
            amount_input = input("New Amount (leave blank to skip): ")
            amount = float(amount_input) if amount_input else None
            currency = input("New Currency (leave blank to skip): ")
            date = input("New Date (YYYY-MM-DD, leave blank to skip): ")
            tags = self.add_tag(transaction_type, category)

            updates = {}
            if category:
                updates["category"] = category
            if amount is not None:
                updates["amount"] = amount
            if currency:
                updates["currency"] = currency
            if transaction_type:
                updates["transaction_type"] = transaction_type
            if date:
                updates["date"] = date
            if tags is not None:
                updates["tags"] = tags

            self.manager.edit_transaction(transaction_id, **updates)
        else:
            print("Transaction not found")

    def delete_transaction(self):
        """Delete Transaction"""
        transaction_id = int(input("Transaction ID to delete: "))
        self.manager.delete_transaction(transaction_id)

    def list_wallet_transactions(self):
        """List Transactions For A Specific Wallet with optional date filtering."""
        wallet_name = input("Wallet Name: ")
        start_date = input("Start Date (YYYY-MM-DD, optional): ")
        end_date = input("End Date (YYYY-MM-DD, optional): ")

        start_date = start_date if start_date else None
        end_date = end_date if end_date else None

        self.manager.list_transactions(
            wallet_name=wallet_name, start_date=start_date, end_date=end_date
        )

    def list_all_transactions(self):
        """List All Transactions with optional date filtering."""
        self.manager.list_transactions()

    def search_expenses_by_tag(self):
        """Search Expenses By Tag"""
        tag = input("Enter tag to search for: ")
        results = self.manager.search_expenses_by_tag(tag)
        if results:
            print(f"\nExpenses matching tag '{tag}':")
            for i, transaction in enumerate(results, 1):
                print(
                    f"Date: {transaction['date']} | Category: {transaction['category']} "
                    f"| Amount: {transaction['amount']} {transaction['currency']} | Tags: {', '.join(transaction['tags'])}"
                )
        else:
            print(f"No expenses found with tag '{tag}'.")

    def add_custom_category(self):
        """Add Custom Category"""
        transaction_type = input(
            "\nEnter transaction type (expense/income) for category name: "
        )
        category_name = input("Enter new custom category name: ")
        tags = input(
            "Add one or several Tags (comma-separated, leave blank to skip): "
        ).strip()
        self.manager.add_custom_category(transaction_type, category_name, tags)

    def edit_custom_category(self):
        """Edit Custom Category"""
        transaction_type = input(
            "\nEnter transaction type (expense/income) to edit category name: "
        )
        old_category_name = input("Current category name: ")
        new_category_name = input("New category name: ")
        self.manager.edit_custom_category(
            transaction_type, old_category_name, new_category_name
        )

    def delete_custom_category(self):
        """Delete Custom Category"""
        transaction_type = input(
            "\nEnter transaction type (expense/income) to detect category: "
        )
        category_name = input("Enter custom category name to delete: ")
        self.manager.delete_custom_category(transaction_type, category_name)

    def exit(self):
        """Exit"""
        print("Exiting...")
        exit()


if __name__ == "__main__":
    args = FinanceCLI(FinanceManager()).parse_args()
    cli = FinanceCLI(FinanceManager(data_file=args.data_file))
    cli.run()
