from datetime import datetime
from pymongo import UpdateOne

def generate_timestamp():
    now = datetime.now()
    return {
        "timestamp": now,
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M %p")
    }

def adjust_balances_after_update(db, book_id: str, changed_tx_timestamp, delta: float):
    """
    Efficiently update balances of transactions after a specific transaction using bulk_write with batching.
    """
    cursor = db.transactions.find(
        {"book_id": book_id, "timestamp": {"$gte": changed_tx_timestamp}},
        {"transaction_id": 1, "balance": 1}
    ).sort("timestamp", 1)

    bulk_ops = []
    BATCH_SIZE = 1000

    for tx in cursor:
        new_balance = tx.get("balance", 0) + delta
        bulk_ops.append(
            UpdateOne(
                {"transaction_id": tx["transaction_id"]},
                {"$set": {"balance": new_balance}}
            )
        )

        if len(bulk_ops) >= BATCH_SIZE:
            db.transactions.bulk_write(bulk_ops)
            bulk_ops = []

    if bulk_ops:
        db.transactions.bulk_write(bulk_ops)

    # Update book balance once
    db.books.update_one(
        {"book_id": book_id},
        {"$inc": {"balance": delta}}
    )

def adjust_totals_on_transaction_change(book: dict, old_amount: float, old_type: str, new_amount: float, new_type: str):
    """
    Calculate change in totals and balance based on old and new transaction
    Returns: delta_balance, delta_cash_in, delta_cash_out
    """
    delta_cash_in = 0
    delta_cash_out = 0
    delta_balance = 0

    # Remove old transaction effect
    if old_type == "in":
        delta_cash_in -= old_amount
        delta_balance -= old_amount
    else:
        delta_cash_out -= old_amount
        delta_balance += old_amount

    # Apply new transaction effect
    if new_type == "in":
        delta_cash_in += new_amount
        delta_balance += new_amount
    else:
        delta_cash_out += new_amount
        delta_balance -= new_amount

    return delta_balance, delta_cash_in, delta_cash_out
