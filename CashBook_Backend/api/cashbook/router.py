from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from core.helpers import adjust_balances_after_update, adjust_totals_on_transaction_change
from models import Book, Transaction
from core.database import conn_mongo_client
from core.helpers import generate_timestamp, adjust_balances_after_update, adjust_totals_on_transaction_change
from datetime import datetime
from uuid import uuid4
import pandas as pd
import xlsxwriter, io
from fpdf import FPDF
from fastapi.responses import StreamingResponse
from urllib.parse import quote


mongo_client = conn_mongo_client()
db = mongo_client["cashbook"]

routes = APIRouter()

# ----------- Helper -----------
def generate_timestamp():
    now = datetime.now()
    return {
        "timestamp": now,
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M %p")
    }

# ----------- Books -----------
@routes.post("/books")
async def create_book(book: Book):
    if db.books.find_one({"user_id": book.user_id, "book_name": book.book_name}):
        raise HTTPException(status_code=400, detail="Book already exists for this user")

    book_id = str(uuid4())
    book_dict = {
        "user_id": book.user_id,
        "book_id": book_id,
        "book_name": book.book_name,
        "balance": 0,
        "created_at": datetime.now(),
    }

    result = db.books.insert_one(book_dict)

    book_dict["_id"] = str(result.inserted_id)
    return {"message": "Book created successfully", "book": book_dict}

@routes.get("/books/{user_id}")
async def get_user_books(user_id: str):
    books_cursor = db.books.find({"user_id": user_id})
    books = []

    for book in books_cursor:
        latest_tx = db.transactions.find_one(
            {"book_id": book["book_id"]},
            sort=[("timestamp", -1)]
        )
        latest_tx_timestamp = latest_tx["timestamp"] if latest_tx else book["created_at"]

        books.append({
            "book_id": book["book_id"],
            "book_name": book["book_name"],
            "balance": book.get("balance", 0),
            "created_at": book["created_at"],
            "latest_transaction": latest_tx_timestamp
        })

    books.sort(key=lambda x: x["latest_transaction"], reverse=True)

    return books

@routes.put("/books/{book_id}")
async def rename_book(book_id: str, new_name: str = Query(...)):
    book = db.books.find_one({"book_id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if db.books.find_one({"user_id": book["user_id"], "book_name": new_name}):
        raise HTTPException(status_code=400, detail="Book name already exists for this user")

    db.books.update_one(
        {"book_id": book_id},
        {"$set": {"book_name": new_name}}
    )

    return {"message": "Book renamed successfully"}

@routes.delete("/books/{book_id}")
async def delete_book(book_id: str):
    book = db.books.find_one({"book_id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    delete_tx_result = db.transactions.delete_many({"book_id": book_id})
    delete_book_result = db.books.delete_one({"_id": book["_id"]})

    return {
        "message": "Book and its transactions deleted successfully",
        "deleted_transactions_count": delete_tx_result.deleted_count,
        "deleted_book_count": delete_book_result.deleted_count
    }

# --------- Upload/Export Book ---------
@routes.post("/books/upload")
async def upload_new_book_transactions(
    user_id: str = Form(...),
    book_name: str = Form(...),
    file: UploadFile = File(...)
):
    from datetime import datetime, timedelta

    existing_book = db.books.find_one({"user_id": user_id, "book_name": book_name})
    if existing_book:
        raise HTTPException(status_code=400, detail="Book already exists. Cannot upload to existing book.")

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file.file)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV or Excel allowed.")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    first_row = df.iloc[0]
    book_created_at = datetime.now()
    if "Date" in df.columns and "Time" in df.columns:
        try:
            book_created_at = pd.to_datetime(f"{first_row['Date']} {first_row['Time']}", dayfirst=True)
        except Exception:
            pass

    book_id = str(uuid4())
    book_dict = {
        "user_id": user_id,
        "book_id": book_id,
        "book_name": book_name,
        "balance": 0,
        "total_cash_in": 0,
        "total_cash_out": 0,
        "created_at": book_created_at,
    }
    db.books.insert_one(book_dict)

    balance = 0
    total_cash_in = 0
    total_cash_out = 0
    transactions = []

    timestamp_counters = {}

    for _, row in df.iterrows():
        def safe_float(value):
            try:
                if pd.isna(value) or value == "" or value is None:
                    return 0.0
                s = str(value).replace(",", "").replace("₹", "").replace("Rs", "").replace("rs", "").strip()
                if s.startswith("(") and s.endswith(")"):
                    s = "-" + s[1:-1]
                return float(s)
            except Exception:
                return 0.0

        def safe_str(value):
            if pd.isna(value) or value is None:
                return ""
            return str(value).strip()

        try:
            base_ts = pd.to_datetime(f"{row['Date']} {row['Time']}", dayfirst=True, errors="raise")
        except Exception:
            base_ts = datetime.now()

        if base_ts not in timestamp_counters:
            timestamp_counters[base_ts] = 0
        else:
            timestamp_counters[base_ts] += 1

        timestamp = base_ts + timedelta(seconds=timestamp_counters[base_ts])

        cash_in = safe_float(row.get("Cash In"))
        cash_out = safe_float(row.get("Cash Out"))
        tx_type = "in" if cash_in > 0 else "out"
        tx_amount = cash_in if tx_type == "in" else cash_out

        balance = balance + tx_amount if tx_type == "in" else balance - tx_amount
        total_cash_in += cash_in
        total_cash_out += cash_out

        user = db.users.find_one({"user_id": user_id})

        tx_dict = {
            "transaction_id": str(uuid4()),
            "book_id": book_id,
            "update_by": user["user_name"] if user else "Unknown",
            "transaction_amount": tx_amount,
            "transaction_type": tx_type,
            "remark": safe_str(row.get("Remark")),
            "mode": safe_str(row.get("Mode")),
            "category": safe_str(row.get("Category")),
            "timestamp": timestamp,
            "date": timestamp.strftime("%d %B %Y"),
            "time": timestamp.strftime("%I:%M %p"),
            "balance": safe_float(balance),
        }
        transactions.append(tx_dict)

    # --- Insert all transactions ---
    if transactions:
        db.transactions.insert_many(transactions)

    # --- Update book totals ---
    db.books.update_one(
        {"book_id": book_id},
        {"$set": {
            "balance": balance,
            "total_cash_in": total_cash_in,
            "total_cash_out": total_cash_out
        }}
    )

    return {
        "message": f"Book created successfully with {len(transactions)} transactions",
        "book_id": book_id
    }

@routes.get("/books/{book_id}/export")
async def export_book_transactions(book_id: str, file_type: str = Query("csv", regex="^(csv|xlsx|pdf)$")):
    # Fetch book
    book = db.books.find_one({"book_id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Fetch transactions, sorted by timestamp
    transactions = list(db.transactions.find({"book_id": book_id}).sort("timestamp", 1))
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this book")

    # Prepare export data
    export_data = []
    for tx in transactions:
        export_data.append({
            "Date": tx.get("date", ""),
            "Time": tx.get("time", ""),
            "Remark": tx.get("remark", ""),
            "Entry by": tx.get("update_by", ""),
            "Category": tx.get("category", "General"),  # fallback if missing
            "Mode": tx.get("mode", ""),
            "Cash In": tx["transaction_amount"] if tx["transaction_type"] == "in" else "",
            "Cash Out": tx["transaction_amount"] if tx["transaction_type"] == "out" else "",
            "Balance": tx.get("balance", 0)
        })

    # --- CSV Export ---
    if file_type == "csv":
        output = io.BytesIO()
        df = pd.DataFrame(export_data)
        csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        output.write(csv_bytes)
        output.seek(0)

        # Unicode-safe filename header
        filename = f"{book['book_name']}_transactions.csv"
        quoted_filename = quote(filename)
        headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"}

        return StreamingResponse(output, media_type="text/csv; charset=utf-8", headers=headers)

    # --- Excel Export ---
    elif file_type == "xlsx":
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Transactions")

        # Write headers
        headers_list = list(export_data[0].keys())
        for col_num, header in enumerate(headers_list):
            worksheet.write(0, col_num, str(header))

        # Write rows safely
        for row_num, row_data in enumerate(export_data, 1):
            for col_num, key in enumerate(headers_list):
                value = row_data[key]
                if value is None:
                    value = ""
                worksheet.write(row_num, col_num, str(value))  # Convert all to string

        workbook.close()
        output.seek(0)

        filename = f"{book['book_name']}_transactions.xlsx"
        quoted_filename = quote(filename)
        headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"}

        return StreamingResponse(output,
                                 media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers=headers)

    # --- PDF Export ---
    elif file_type == "pdf":
        output = io.BytesIO()
        pdf = FPDF()
        pdf.add_page()
        # Add Unicode font
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)  # Place DejaVuSans.ttf in your project folder
        pdf.set_font('DejaVu', '', 10)

        # Header row
        header_line = " | ".join(export_data[0].keys())
        pdf.cell(0, 8, header_line, ln=True)

        # Rows
        for tx in export_data:
            line = " | ".join(str(tx[k]) for k in export_data[0].keys())
            pdf.cell(0, 8, line, ln=True)

        pdf.output(output)
        output.seek(0)

        filename = f"{book['book_name']}_transactions.pdf"
        quoted_filename = quote(filename)
        headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"}

        return StreamingResponse(output, media_type="application/pdf", headers=headers)

# ----------- Transaction -----------
# @routes.post("/add_transaction")
# async def add_transaction(transaction: Transaction):
#     if not transaction.book_id:
#         book = db.books.find_one({"book_name": transaction.book_name})
#         if not book:
#             raise HTTPException(status_code=404, detail="Book not found")
#         transaction.book_id = book["book_id"]
#     else:
#         book = db.books.find_one({"book_id": transaction.book_id})
#         if not book:
#             raise HTTPException(status_code=404, detail="Book not found")

#     ts = generate_timestamp()
#     transaction.timestamp = ts["timestamp"]
#     transaction.date = ts["date"]
#     transaction.time = ts["time"]

#     transaction.transaction_id = str(uuid4())

#     last_tx = db.transactions.find_one(
#         {"book_id": transaction.book_id},
#         sort=[("timestamp", -1)]
#     )
#     last_balance = last_tx["balance"] if last_tx else 0
#     total_cash_in = book.get("total_cash_in", 0)
#     total_cash_out = book.get("total_cash_out", 0)

#     if transaction.transaction_type.lower() == "in":
#         transaction.balance = last_balance + transaction.transaction_amount
#         total_cash_in += transaction.transaction_amount
#         # cash_in = transaction.transaction_amount
#         # cash_out = 0
#     elif transaction.transaction_type.lower() == "out":
#         transaction.balance = last_balance - transaction.transaction_amount
#         total_cash_out += transaction.transaction_amount
#         # cash_in = 0
#         # cash_out = transaction.transaction_amount
#     else:
#         raise HTTPException(status_code=400, detail="transaction_type must be 'in' or 'out'")
    
#     user = db.users.find_one({"user_id": transaction.update_by})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     transaction.update_by = user["user_name"]

#     tx_dict = transaction.dict()
#     # tx_dict.update({
#     #     "cash_in": cash_in,
#     #     "cash_out": cash_out
#     # })

#     result = db.transactions.insert_one(tx_dict)
#     tx_dict["_id"] = str(result.inserted_id)

#     db.books.update_one(
#         {"book_id": transaction.book_id},
#         {"$set": {"balance": transaction.balance, "total_cash_in": total_cash_in,"total_cash_out": total_cash_out}}
#     )

#     user = db.users.find_one({"user_id": tx_dict["update_by"]})
#     tx_dict["user_name"] = user["user_name"] if user else "Unknown"

#     return {"message": "Transaction added successfully", "transaction": tx_dict}

@routes.get("/transactions/{book_id}")
async def get_book_transactions(
    book_id: str,
    page: int = 1,
    limit: int = 100
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    
    skip = (page - 1) * limit

    cursor = db.transactions.find({"book_id": book_id}, {"_id": 0}) \
                            .sort("timestamp", -1) \
                            .skip(skip) \
                            .limit(limit)

    transactions = list(cursor)
    # transactions.reverse()

    book = db.books.find_one({"book_id": book_id})

    total_count = db.transactions.count_documents({"book_id": book_id})
    total_pages = (total_count + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_transactions": total_count,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "total_cash_in": book.get("total_cash_in", 0),
        "total_cash_out": book.get("total_cash_out", 0),
        "total_balance": book.get("balance", 0),
        "transactions": transactions
    }

# ---------------- Add Transaction ----------------
@routes.post("/add_transaction")
async def add_transaction(transaction: Transaction):
    # Validate book
    if not transaction.book_id:
        book = db.books.find_one({"book_name": transaction.book_name})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        transaction.book_id = book["book_id"]
    else:
        book = db.books.find_one({"book_id": transaction.book_id})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

    ts = generate_timestamp()
    transaction.timestamp = ts["timestamp"]
    transaction.date = ts["date"]
    transaction.time = ts["time"]
    transaction.transaction_id = str(uuid4())

    last_tx = db.transactions.find_one({"book_id": transaction.book_id}, sort=[("timestamp", -1)])
    last_balance = last_tx["balance"] if last_tx else 0

    if transaction.transaction_type.lower() == "in":
        transaction.balance = last_balance + transaction.transaction_amount
        book_total_cash_in = book.get("total_cash_in", 0) + transaction.transaction_amount
        book_total_cash_out = book.get("total_cash_out", 0)
    elif transaction.transaction_type.lower() == "out":
        transaction.balance = last_balance - transaction.transaction_amount
        book_total_cash_in = book.get("total_cash_in", 0)
        book_total_cash_out = book.get("total_cash_out", 0) + transaction.transaction_amount
    else:
        raise HTTPException(status_code=400, detail="transaction_type must be 'in' or 'out'")

    # Get user
    user = db.users.find_one({"user_id": transaction.update_by})
    transaction.update_by = user["user_name"] if user else "Unknown"

    tx_dict = transaction.dict()
    result = db.transactions.insert_one(tx_dict)
    tx_dict["_id"] = str(result.inserted_id)

    # Update book totals
    db.books.update_one(
        {"book_id": transaction.book_id},
        {"$set": {"balance": transaction.balance, "total_cash_in": book_total_cash_in, "total_cash_out": book_total_cash_out}}
    )

    return {"message": "Transaction added successfully", "transaction": tx_dict}

# ---------------- Update Transaction ----------------
@routes.put("/transactions/{transaction_id}")
async def update_transaction(transaction_id: str, updated_data: dict):
    transaction = db.transactions.find_one({"transaction_id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    book = db.books.find_one({"book_id": transaction["book_id"]})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    allowed_fields = {"transaction_amount", "transaction_type", "remark", "mode", "category"}
    update_fields = {k: v for k, v in updated_data.items() if k in allowed_fields}

    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    old_type = transaction["transaction_type"].lower()
    old_amount = float(transaction["transaction_amount"])
    new_type = update_fields.get("transaction_type", old_type).lower()
    new_amount = float(update_fields.get("transaction_amount", old_amount))

    # Calculate deltas
    delta_balance, delta_cash_in, delta_cash_out = adjust_totals_on_transaction_change(
        book, old_amount, old_type, new_amount, new_type
    )

    # Update transaction
    db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": update_fields}
    )

    # Adjust subsequent balances
    adjust_balances_after_update(db, book["book_id"], transaction["timestamp"], delta_balance)

    # Update book totals
    db.books.update_one(
        {"book_id": book["book_id"]},
        {"$inc": {"total_cash_in": delta_cash_in, "total_cash_out": delta_cash_out}}
    )

    return {"message": "Transaction updated successfully"}

# ---------------- Delete Transaction ----------------
@routes.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    transaction = db.transactions.find_one({"transaction_id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    book = db.books.find_one({"book_id": transaction["book_id"]})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    old_type = transaction["transaction_type"].lower()
    old_amount = float(transaction["transaction_amount"])

    # Calculate delta for deleting this transaction
    delta_balance, delta_cash_in, delta_cash_out = adjust_totals_on_transaction_change(
        book, old_amount, old_type, 0, old_type
    )

    # Delete transaction
    db.transactions.delete_one({"transaction_id": transaction_id})

    # Adjust subsequent balances
    adjust_balances_after_update(db, book["book_id"], transaction["timestamp"], delta_balance)

    # Update book totals
    db.books.update_one(
        {"book_id": book["book_id"]},
        {"$inc": {"total_cash_in": delta_cash_in, "total_cash_out": delta_cash_out}}
    )

    return {"message": "Transaction deleted successfully"}


# @routes.put("/transactions/{transaction_id}")
# async def update_transaction(transaction_id: str, updated_data: dict):
#     transaction = db.transactions.find_one({"transaction_id": transaction_id})
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")

#     book = db.books.find_one({"book_id": transaction["book_id"]})
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")

#     allowed_fields = {"transaction_amount", "transaction_type", "remark", "mode", "category"}
#     update_fields = {k: v for k, v in updated_data.items() if k in allowed_fields}

#     if not update_fields:
#         raise HTTPException(status_code=400, detail="No valid fields to update")

#     old_type = transaction["transaction_type"].lower()
#     old_amount = float(transaction["transaction_amount"])
#     new_type = update_fields.get("transaction_type", old_type).lower()
#     new_amount = float(update_fields.get("transaction_amount", old_amount))

#     total_cash_in = book.get("total_cash_in", 0)
#     total_cash_out = book.get("total_cash_out", 0)
#     balance = book.get("balance", 0)

#     if old_type == "in":
#         total_cash_in -= old_amount
#         balance -= old_amount
#     else:
#         total_cash_out -= old_amount
#         balance += old_amount

#     if new_type == "in":
#         total_cash_in += new_amount
#         balance += new_amount
#     else:
#         total_cash_out += new_amount
#         balance -= new_amount

#     db.transactions.update_one(
#         {"transaction_id": transaction_id},
#         {"$set": update_fields}
#     )

#     db.books.update_one(
#         {"book_id": transaction["book_id"]},
#         {"$set": {
#             "total_cash_in": total_cash_in,
#             "total_cash_out": total_cash_out,
#             "balance": balance
#         }}
#     )

#     return {"message": "Transaction updated successfully"}

# @routes.delete("/transactions/{transaction_id}")
# async def delete_transaction(transaction_id: str):
#     transaction = db.transactions.find_one({"transaction_id": transaction_id})
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")

#     book = db.books.find_one({"book_id": transaction["book_id"]})
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")

#     old_type = transaction["transaction_type"].lower()
#     old_amount = float(transaction["transaction_amount"])

#     total_cash_in = book.get("total_cash_in", 0)
#     total_cash_out = book.get("total_cash_out", 0)
#     balance = book.get("balance", 0)

#     if old_type == "in":
#         total_cash_in -= old_amount
#         balance -= old_amount
#     else:
#         total_cash_out -= old_amount
#         balance += old_amount

#     db.transactions.delete_one({"transaction_id": transaction_id})

#     db.books.update_one(
#         {"book_id": transaction["book_id"]},
#         {"$set": {
#             "total_cash_in": total_cash_in,
#             "total_cash_out": total_cash_out,
#             "balance": balance
#         }}
#     )

#     return {"message": "Transaction deleted successfully"}


#####KICK

# @routes.put("/transactions/{transaction_id}")
# async def update_transaction(transaction_id: str, updated_data: dict):
#     transaction = db.transactions.find_one({"transaction_id": transaction_id})
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")

#     allowed_fields = {"transaction_amount", "transaction_type", "remark", "mode"}
#     update_fields = {k: v for k, v in updated_data.items() if k in allowed_fields}

#     if not update_fields:
#         raise HTTPException(status_code=400, detail="No valid fields to update")

#     db.transactions.update_one({"transaction_id": transaction_id}, {"$set": update_fields})

#     book_id = transaction["book_id"]
#     timestamp = transaction["timestamp"]

#     all_tx = list(db.transactions.find(
#         {"book_id": book_id, "timestamp": {"$gte": timestamp}}
#     ).sort("timestamp", 1))

#     prev_tx = db.transactions.find_one(
#         {"book_id": book_id, "timestamp": {"$lt": timestamp}},
#         sort=[("timestamp", -1)]
#     )
#     balance = prev_tx["balance"] if prev_tx else 0

#     for tx in all_tx:
#         if tx["transaction_type"].lower() == "in":
#             balance += tx["transaction_amount"]
#         else:
#             balance -= tx["transaction_amount"]
#         db.transactions.update_one({"_id": tx["_id"]}, {"$set": {"balance": balance}})

#     db.books.update_one({"book_id": book_id}, {"$set": {"balance": balance}})

#     return {"message": "Transaction updated successfully"}

# @routes.delete("/transactions/{transaction_id}")
# async def delete_transaction(transaction_id: str):
#     transaction = db.transactions.find_one({"transaction_id": transaction_id})
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")

#     book_id = transaction["book_id"]
#     timestamp = transaction["timestamp"]

#     db.transactions.delete_one({"transaction_id": transaction_id})

#     all_tx = list(db.transactions.find(
#         {"book_id": book_id, "timestamp": {"$gte": timestamp}}
#     ).sort("timestamp", 1))

#     prev_tx = db.transactions.find_one(
#         {"book_id": book_id, "timestamp": {"$lt": timestamp}},
#         sort=[("timestamp", -1)]
#     )
#     balance = prev_tx["balance"] if prev_tx else 0

#     for tx in all_tx:
#         if tx["transaction_type"].lower() == "in":
#             balance += tx["transaction_amount"]
#         else:
#             balance -= tx["transaction_amount"]

#         db.transactions.update_one(
#             {"_id": tx["_id"]},
#             {"$set": {"balance": balance}}
#         )

#     db.books.update_one({"book_id": book_id}, {"$set": {"balance": balance}})

#     return {"message": "Transaction deleted successfully"}
