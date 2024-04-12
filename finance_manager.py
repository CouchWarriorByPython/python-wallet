import json
from collections import defaultdict
from datetime import datetime


class Wallet:
    def __init__(self, name, balance=0.0, currency="USD"):
        self.name = name
        self.balance = round(balance, 4)
        self.currency = currency

    def to_dict(self):
        return {"name": self.name, "balance": self.balance, "currency": self.currency}


class Transaction:
    def __init__(
        self,
        id,
        wallet_name,
        transaction_type,
        category,
        amount,
        currency,
        date=None,
        tags=None,
    ):
        self.id = id
        self.wallet_name = wallet_name
        self.transaction_type = transaction_type
        self.category = category
        self.amount = float(amount)
        self.currency = currency
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.tags = tags or []

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_data": {
                "wallet_name": self.wallet_name,
                "transaction_type": self.transaction_type,
                "category": self.category,
                "amount": self.amount,
                "currency": self.currency,
                "date": self.date,
                "tags": self.tags,
            },
        }


class FinanceManager:
    PREDEFINED_CATEGORIES = {
        "expense": [
            "food",
            "clothing",
            "transportation",
            "entertainment",
            "health",
            "education",
            "charity",
        ],
        "income": ["salary", "investment income"],
    }

    def __init__(self, data_file="finance_data.json"):
        self.data_file = data_file
        self.wallets = {}
        self.transactions = []
        self.custom_categories = {"expense": [], "income": []}
        self.default_wallet = None
        self.transaction_id_counter = len(self.transactions) + 1
        self.available_tags = {
            "expense": {
                "food": ["groceries", "organic"],
                "clothing": ["casual wear", "formal wear"],
                "transportation": ["commute", "long-distance"],
                "entertainment": ["movies", "live music"],
                "health": ["pharmacy", "wellness"],
                "education": ["textbooks", "courses"],
                "charity": ["donations", "community support"],
            },
            "income": {
                "salary": ["regular salary", "overtime"],
                "investment income": ["stocks", "bonds"],
            },
        }
        self.load_from_file()

    def add_wallet(self, name, initial_balance=0.0, currency="USD"):
        if name not in self.wallets:
            self.wallets[name] = Wallet(name, initial_balance, currency)
        self.save_to_file()

    def add_transaction(
        self,
        wallet_name,
        transaction_type,
        category,
        amount,
        currency,
        date=None,
        tags=None,
    ):
        if wallet_name in self.wallets:
            valid_categories = (
                self.PREDEFINED_CATEGORIES[transaction_type]
                + self.custom_categories[transaction_type]
            )
            if category in valid_categories:
                transaction = Transaction(
                    self.transaction_id_counter,
                    wallet_name,
                    transaction_type,
                    category,
                    amount,
                    currency,
                    date,
                    tags,
                )
                self.transactions.append(transaction)
                self.transaction_id_counter += 1
                self.save_to_file()


    def add_custom_category(self, transaction_type, category_name, tags=[]):
        if (
            category_name not in self.custom_categories[transaction_type]
            and category_name not in self.PREDEFINED_CATEGORIES[transaction_type]
        ):
            self.custom_categories[transaction_type].append(category_name)
            tags = tags.split(",") if isinstance(tags, str) else tags
            self.update_available_tags(transaction_type, category_name, tags)
            self.save_to_file()


    def edit_custom_category(self, transaction_type, old_category_name, new_category_name):
        if old_category_name in self.custom_categories[transaction_type]:
            index = self.custom_categories[transaction_type].index(old_category_name)
            self.custom_categories[transaction_type][index] = new_category_name
            
            for transaction in self.transactions:
                if transaction.category == old_category_name and transaction.transaction_type == transaction_type:
                    transaction.category = new_category_name

            if old_category_name in self.available_tags[transaction_type]:
                old_tags = self.available_tags[transaction_type][old_category_name]
                del self.available_tags[transaction_type][old_category_name]
                self.available_tags[transaction_type][new_category_name] = old_tags

            self.save_to_file()
        else:
            raise ValueError(f"Category '{old_category_name}' not found in {transaction_type} categories.")


    def delete_custom_category(self, transaction_type, category_name):
        if category_name in self.custom_categories[transaction_type]:
            self.custom_categories[transaction_type].remove(category_name)

            if category_name in self.available_tags[transaction_type]:
                del self.available_tags[transaction_type][category_name]

            self.save_to_file()
        else:
            raise ValueError(f"Category '{category_name}' not found in {transaction_type} categories.")


    def save_to_file(self):
        data = {
            "wallets": {name: wallet.to_dict() for name, wallet in self.wallets.items()},
            "transactions": [transaction.to_dict() for transaction in self.transactions],
            "custom_categories": self.custom_categories,
            "default_wallet": self.default_wallet,
            "available_tags": self.available_tags
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=4)

    def load_from_file(self):
        try:
            with open(self.data_file, "r") as file:
                data = json.load(file)
                self.wallets = {name: Wallet(**info) for name, info in data.get("wallets", {}).items()}
                self.transactions = [
                    Transaction(
                        id=info['id'],
                        wallet_name=info['transaction_data']['wallet_name'],
                        transaction_type=info['transaction_data']['transaction_type'],
                        category=info['transaction_data']['category'],
                        amount=float(info['transaction_data']['amount']),
                        currency=info['transaction_data']['currency'],
                        date=info['transaction_data']['date'],
                        tags=info['transaction_data']['tags']
                    ) for info in data.get("transactions", [])
                ]
                self.custom_categories = data.get("custom_categories", {})
                self.default_wallet = data.get("default_wallet")
                self.available_tags = data.get("available_tags", self.available_tags)
        except (FileNotFoundError, json.JSONDecodeError):
            self.wallets = {}
            self.transactions = []
            self.custom_categories = {"expense": [], "income": []}
            self.default_wallet = None
            self.available_tags = {
                "expense": {
                    "food": ["groceries", "organic"],
                    "clothing": ["casual wear", "formal wear"],
                    "transportation": ["commute", "long-distance"],
                    "entertainment": ["movies", "live music"],
                    "health": ["pharmacy", "wellness"],
                    "education": ["textbooks", "courses"],
                    "charity": ["donations", "community support"],
                },
                "income": {
                    "salary": ["regular salary", "overtime"],
                    "investment income": ["stocks", "bonds"],
                },
            }




    def list_transactions(self, wallet_name=None, start_date=None, end_date=None):
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        filtered_transactions = []
        for transaction in self.transactions:
            transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
            if (not wallet_name or transaction.wallet_name == wallet_name) and \
            (not start_date or transaction_date >= start_date) and \
            (not end_date or transaction_date <= end_date):
                filtered_transactions.append(transaction)

        transactions_by_date = defaultdict(list)
        for transaction in filtered_transactions:
            transactions_by_date[transaction.date].append(transaction)

        for date in sorted(transactions_by_date.keys()):
            daily_transactions = sorted(transactions_by_date[date], key=lambda x: x.id)
            total_amount = sum(t.amount for t in daily_transactions)
            print(f"Date: {date}, Total Amount: ${total_amount:.2f}")
            for transaction in daily_transactions:
                print(f"  - Wallet: {transaction.wallet_name}, Category: {transaction.category}, Amount: ${transaction.amount:.2f}")



    def delete_transaction(self, transaction_id):
        self.transactions = [t for t in self.transactions if t.id != transaction_id]
        self.save_to_file()

    def edit_transaction(self, transaction_id, **updates):
        for transaction in self.transactions:
            if transaction.id == transaction_id:
                for key, value in updates.items():
                    setattr(transaction, key, value)
                self.save_to_file()
                return True
        return False

    def set_default_wallet(self, name):
        if name in self.wallets:
            self.default_wallet = name
            self.save_to_file()
            return True
        return False

    def get_default_wallet_name(self):
        return getattr(self, "default_wallet", None)

    def search_expenses_by_tag(self, tag):
        return [
            transaction.to_dict()["transaction_data"]
            for transaction in self.transactions
            if tag in transaction.tags and transaction.transaction_type == "expense"
        ]

    def list_categories(self, transaction_type):
        combined_categories = {"expense": [], "income": []}

        for category_type in ["expense", "income"]:
            combined_categories[category_type] = (
                self.PREDEFINED_CATEGORIES[category_type]
                + self.custom_categories[category_type]
            )
        return combined_categories[transaction_type]

    @property
    def get_available_tags(self):
        """Retrieve default tags."""
        return self.available_tags

    def update_available_tags(self, transaction_type, category, new_tags):
        print(transaction_type, category, new_tags)
        """Update tags for a specific transaction type and category."""
        if transaction_type in self.available_tags:
            self.available_tags[transaction_type][category] = new_tags
        else:
            raise ValueError("Transaction type or category does not exist.")
