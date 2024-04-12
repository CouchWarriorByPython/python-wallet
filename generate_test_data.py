import argparse
import random
from datetime import datetime, timedelta

from finance_manager import FinanceManager


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate test data for the Finance Manager"
    )
    parser.add_argument(
        "--start_date", help="Start date for transactions (YYYY-MM-DD)", required=True
    )
    parser.add_argument(
        "--end_date", help="End date for transactions (YYYY-MM-DD)", required=True
    )
    parser.add_argument(
        "--transactions_per_day",
        help="Range of transactions per day (min-max)",
        default="1-3",
    )
    parser.add_argument(
        "--amount_range",
        help="Range of transaction amounts (min-max)",
        default="10-100",
    )
    parser.add_argument(
        "--wallet_names",
        nargs="*",
        help="List of wallet names to use for transactions",
        default=["DefaultWallet"],
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        help="List of categories for transactions",
        default="",
    )
    parser.add_argument(
        "--tags", nargs="*", help="List of tags for transactions", default=""
    )
    return parser.parse_args()


def ensure_wallets_exist(finance_manager, wallet_names):
    for name in wallet_names:
        if name not in finance_manager.wallets:
            finance_manager.add_wallet(name, initial_balance=random.uniform(1000, 5000))


def generate_transactions(finance_manager, config):
    min_transactions, max_transactions = map(
        int, config["transactions_per_day"].split("-")
    )
    min_amount, max_amount = map(float, config["amount_range"].split("-"))
    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(config["end_date"], "%Y-%m-%d")

    if not config["categories"]:
        config["categories"] = finance_manager.list_categories

    current_date = start_date
    while current_date <= end_date:
        for wallet_name in config["wallet_names"]:
            num_transactions = random.randint(min_transactions, max_transactions)
            for _ in range(num_transactions):
                transaction_type = random.choice(["expense", "income"])
                category = random.choice(config["categories"](transaction_type))

                tag_choices = (
                    config["tags"]
                    if config["tags"]
                    else finance_manager.available_tags[transaction_type][category]
                )
                tag = random.choice(tag_choices)
                amount = random.uniform(min_amount, max_amount)

                finance_manager.add_transaction(
                    wallet_name,
                    transaction_type,
                    category,
                    round(amount, 2),
                    "USD",
                    current_date.strftime("%Y-%m-%d"),
                    [tag],
                )
        current_date += timedelta(days=1)


def main():
    args = parse_args()
    finance_manager = FinanceManager(data_file="finance_data.json")
    config = {
        "wallet_names": args.wallet_names,
        "categories": args.categories,
        "transactions_per_day": args.transactions_per_day,
        "tags": args.tags,
        "amount_range": args.amount_range,
        "start_date": args.start_date,
        "end_date": args.end_date,
    }

    ensure_wallets_exist(finance_manager, config["wallet_names"])
    generate_transactions(finance_manager, config)
    finance_manager.save_to_file()
    print("Test transactions generated and saved successfully.")


if __name__ == "__main__":
    main()
