import imaplib
import email
from email.header import decode_header
from datetime import datetime
import re
from typing import List, Dict, Optional
import os


class EmailTransactionParser:
    def __init__(self, email_address: str, password: str):
        self.email_address = email_address
        self.password = password
        self.imap = None

    def connect(self, imap_server: str = "imap.gmail.com"):
        """Connect to IMAP server"""
        try:
            self.imap = imaplib.IMAP4_SSL(imap_server)
            self.imap.login(self.email_address, self.password)
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to email: {str(e)}")

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.imap:
            self.imap.logout()

    def parse_transaction_from_email(self, email_body: str, subject: str) -> Optional[Dict]:
        """Parse transaction details from email body and subject"""
        transaction = {
            "title": "",
            "amount": 0.0,
            "type": "expense",
            "category": "Other",
            "bank": "",
            "date": datetime.now().isoformat()
        }

        # Extract bank name from subject or body
        banks = ["HDFC", "ICICI", "SBI", "Axis", "Kotak", "IDFC", "Yes Bank", "IndusInd", "PNB", "BOB", "Canara",
                 "Union Bank"]
        for bank in banks:
            if bank.lower() in subject.lower() or bank.lower() in email_body.lower():
                transaction["bank"] = bank
                break

        # Extract amount (INR patterns: Rs, INR, ₹)
        amount_patterns = [
            r'(?:Rs\.?|INR|₹)\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:amount|Amount|AMOUNT)[\s:]*(?:Rs\.?|INR|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'(?:debited|credited|spent|paid)[\s:]*(?:Rs\.?|INR|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)'
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, email_body, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                transaction["amount"] = float(amount_str)
                break

        # Determine transaction type (credit/debit)
        if any(word in email_body.lower() for word in ["credited", "credit", "received", "deposit"]):
            transaction["type"] = "income"
            transaction["amount"] = abs(transaction["amount"])
        elif any(
                word in email_body.lower() for word in ["debited", "debit", "spent", "paid", "purchase", "withdrawal"]):
            transaction["type"] = "expense"
            transaction["amount"] = -abs(transaction["amount"])

        # Extract merchant/title
        merchant_patterns = [
            r'(?:at|to|from)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+on|\.|,)',
            r'(?:merchant|Merchant|MERCHANT)[\s:]+([A-Za-z0-9\s&]+?)(?:\s+on|\.|,)',
            r'(?:transaction at|payment to)\s+([A-Za-z0-9\s&]+?)(?:\s+on|\.|,)'
        ]

        for pattern in merchant_patterns:
            match = re.search(pattern, email_body)
            if match:
                transaction["title"] = match.group(1).strip()
                break

        if not transaction["title"]:
            transaction["title"] = subject[:50]

        # Categorize transaction
        transaction["category"] = self._categorize_transaction(transaction["title"], email_body)

        # Only return if amount was found
        if transaction["amount"] != 0.0:
            return transaction
        return None

    def _categorize_transaction(self, title: str, body: str) -> str:
        """Categorize transaction based on keywords"""
        text = (title + " " + body).lower()

        categories = {
            "Food": ["restaurant", "cafe", "zomato", "swiggy", "food", "dining", "hotel", "eatery"],
            "Shopping": ["amazon", "flipkart", "myntra", "shopping", "mall", "store", "mart", "retail"],
            "Transport": ["uber", "ola", "petrol", "diesel", "fuel", "parking", "toll", "transport"],
            "Utilities": ["electricity", "water", "gas", "bill", "utility", "broadband", "internet", "mobile",
                          "recharge"],
            "Entertainment": ["netflix", "prime", "spotify", "movie", "cinema", "entertainment", "subscription"],
            "Healthcare": ["hospital", "clinic", "pharmacy", "medical", "doctor", "health"],
            "Education": ["school", "college", "university", "course", "tuition", "education"],
            "Income": ["salary", "credited", "credit", "received", "deposit", "income"]
        }

        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category

        return "Other"

    def fetch_transactions(self, days: int = 30, search_criteria: str = None) -> List[Dict]:
        """Fetch bank transaction emails from inbox"""
        if not self.imap:
            raise Exception("Not connected to email server")

        transactions = []

        try:
            # Select inbox
            self.imap.select("INBOX")

            # Build search query
            if search_criteria:
                search_query = search_criteria
            else:
                # Search for common bank transaction keywords
                bank_keywords = [
                    'SUBJECT "debited"',
                    'SUBJECT "credited"',
                    'SUBJECT "transaction"',
                    'SUBJECT "payment"',
                    'SUBJECT "purchase"',
                    'FROM "alerts"',
                    'FROM "bank"'
                ]
                search_query = f'OR {" OR ".join(bank_keywords)}'

            # Search emails
            status, messages = self.imap.search(None, search_query)

            if status != "OK":
                return transactions

            email_ids = messages[0].split()

            # Process last N emails (limit to avoid timeout)
            for email_id in email_ids[-100:]:  # Last 100 emails
                try:
                    status, msg_data = self.imap.fetch(email_id, "(RFC822)")

                    if status != "OK":
                        continue

                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Get subject
                    subject = ""
                    if msg["Subject"]:
                        subject_parts = decode_header(msg["Subject"])
                        subject = "".join([
                            part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
                            for part, encoding in subject_parts
                        ])

                    # Get email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    # Parse transaction
                    transaction = self.parse_transaction_from_email(body, subject)

                    if transaction:
                        # Add email date
                        email_date = email.utils.parsedate_to_datetime(msg["Date"])
                        transaction["date"] = email_date.isoformat()
                        transactions.append(transaction)

                except Exception as e:
                    continue

            return transactions

        except Exception as e:
            raise Exception(f"Error fetching transactions: {str(e)}")


# Gmail-specific helper
def connect_gmail(email_address: str, app_password: str) -> EmailTransactionParser:
    """
    Connect to Gmail using app password
    Note: Users need to enable 2FA and create app password at:
    https://myaccount.google.com/apppasswords
    """
    parser = EmailTransactionParser(email_address, app_password)
    parser.connect("imap.gmail.com")
    return parser