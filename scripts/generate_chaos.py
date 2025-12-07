import csv
import random
from faker import Faker
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict

SEED_VALUE = 42
NUM_FAKE_ROWS = 70
OUTPUT_FILE = Path('data/raw/generated_transactions.csv')

random.seed(SEED_VALUE)
Faker.seed(SEED_VALUE)
fake = Faker()

def generate_faker_rows(num_rows) -> List[Dict[str,str]]:
    rows = []
    static_merchants = ["STARBUCKS", "AMAZON *PRIME", "COSTCO WHSE", "SHELL OIL", "DIGITAL OCEAN INC", "LYFT RIDE"]

    for i in range(num_rows):
        txn_date = date(2025, 12, 6) - timedelta(days=random.randint(1, 365))
        date_format = random.choice([txn_date.strftime("%Y-%m-%d"), 
                                     txn_date.strftime("%m/%d/%y"), 
                                     txn_date.strftime("%b %d, %Y"), 
                                     txn_date.strftime("%d-%b-%Y"), 
                                     txn_date.strftime("%Y.%m.%d")])

        amount = round(random.uniform(5.0, 500.0), 2)

        comma_fmt = f"{amount:,.2f}"
        basic_fmt = f"{amount:.2f}"
        amount_str = random.choice([f"${basic_fmt}", 
                                    f"${comma_fmt}", 
                                    f"$ {basic_fmt}",
                                    f"{basic_fmt} USD",
                                    f"USD {amount:.2f}", 
                                    f"{basic_fmt}",
                                    f"{amount:.0f}"])
        
        if random.random() < 0.9:
            merchant_name = random.choice(static_merchants)
        else:
            merchant_name = fake.company()
        
        if random.random() < 0.2:
            merchant_name = f"{merchant_name.replace(' ', '*')}"
        if random.random() < 0.1:
            merchant_name = f"**{merchant_name.upper()}**"
        if random.random() < 0.1:
            merchant_name = f" {merchant_name} "

        rows.append({'Trans Date': date_format, 'Description': merchant_name, 'Value': amount_str})

    return rows

def get_edge_cases() -> List[Dict[str,str]]:
    return[
        # Dates
        {'Trans Date': 'Sept. 3rd, 2024', 'Description': 'Google Play Store', 'Value': '$12.99'},
        {'Trans Date': '01/01/2023 11:59 PM', 'Description': 'Late Night Pizza', 'Value': '$35.00'}, 
        {'Trans Date': '2025-01-4', 'Description': 'Gym Membership', 'Value': '1000'},
        {'Trans Date': '2025/13/01', 'Description': 'Amazon', 'Value': '$1.00'}, # Invalid date

        # Amounts
        {'Trans Date': '2025-01-02', 'Description': 'ATM Withdrawal', 'Value': '(500.00)'}, 
        {'Trans Date': '2025-01-02', 'Description': 'Chase ATM', 'Value': '-500.00'}, 
        {'Trans Date': '2025-01-03', 'Description': 'Bonus Deposit', 'Value': '1,500.00 USD'},
        {'Trans Date': '2025-01-04', 'Description': 'Bank Adjustment', 'Value': '0'},

        # Merchants
        {'Trans Date': '2025-01-05', 'Description': 'UBER *TRIP', 'Value': '$25.00'},
        {'Trans Date': '2025-01-05', 'Description': 'Uber Technologies', 'Value': '$23.50'},
        {'Trans Date': '2025-01-06', 'Description': 'Uber EATS', 'Value': '$15.00'},
        {'Trans Date': '2025-01-07', 'Description': 'Amazon Web Services', 'Value': '$5.00'},
        {'Trans Date': '2025-01-07', 'Description': 'AWS', 'Value': '$10.00'},
        {'Trans Date': '2025-01-08', 'Description': 'Starbucks ☕️', 'Value': '$5.00'},
        {'Trans Date': '2025-01-09', 'Description': '        Target Store    ', 'Value': '$10.00'},
        {'Trans Date': '2025-01-09', 'Description': 'Unknown Vendor', 'Value': '$10.00'}, # Should be unrecognized vendor
        

        # Missing Data
        {'Trans Date': '', 'Description': 'walmart', 'Value': '$10.00'}, # Missing Date
        {'Trans Date': '2025-01-10', 'Description': '', 'Value': '5.00'}, # Missing Vendor
        {'Trans Date': '2025/12/10', 'Description': 'Christmas Shopping', 'Value': ''}, # Missing Value
    ]

def create_chaos_file() -> None:
    all_rows = generate_faker_rows(NUM_FAKE_ROWS) + get_edge_cases()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ['Trans Date', 'Description', 'Value']

    print(f"Generating {len(all_rows)} transactions...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Successfully generated data at {OUTPUT_FILE}")

if __name__ == "__main__":
    create_chaos_file()