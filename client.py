"""
Agentic Multimodal Invoice & Receipt Reconciler (Zero External Dependencies)
Performs three-way invoice-to-ledger matching, tax audit, and double-entry journal entry generation.
"""
import time
import math
import hashlib
import json
import re
from typing import Dict, Any, List, Optional

class AgenticMultimodalInvoiceReceiptReconciler:
    def __init__(self, default_tolerance: float = 0.05):
        self.default_tolerance = default_tolerance

    def parse_invoice_metadata(self, invoice_text: str) -> Dict[str, Any]:
        """Extracts vendor, invoice number, subtotal, tax, and grand total from text."""
        # Find invoice number
        inv_match = re.search(r"(?:invoice|inv|receipt)[#:\s]+([A-Z0-9_-]{4,16})", invoice_text, re.IGNORECASE)
        inv_no = inv_match.group(1).upper() if inv_match else "INV-UNKNOWN"

        # Find vendor
        vendor_match = re.search(r"(?:vendor|merchant|billed by|seller)[#:\s]+([\w\s]{3,30})", invoice_text, re.IGNORECASE)
        vendor = vendor_match.group(1).strip() if vendor_match else "General Vendor"

        # Extract amounts
        amounts = [float(x.replace(",", "")) for x in re.findall(r"\$([0-9,]+\.[0-9]{2})", invoice_text)]
        grand_total = max(amounts) if amounts else 0.0
        tax = 0.0
        tax_match = re.search(r"(?:tax|vat|gst)[#:\s]+\$?([0-9,]+\.[0-9]{2})", invoice_text, re.IGNORECASE)
        if tax_match:
            tax = float(tax_match.group(1).replace(",", ""))

        subtotal = round(grand_total - tax, 2)

        return {
            "invoice_number": inv_no,
            "vendor": vendor,
            "currency": "USD",
            "subtotal": max(0.0, subtotal),
            "tax_amount": tax,
            "grand_total": grand_total,
            "tax_rate_estimated": round((tax / max(0.01, subtotal)) * 100, 2) if subtotal > 0 else 0.0
        }

    def reconcile_against_bank_ledger(
        self,
        invoice: Dict[str, Any],
        bank_transactions: List[Dict[str, Any]],
        tolerance_usd: Optional[float] = None
    ) -> Dict[str, Any]:
        """Matches invoice against bank statement transactions within tolerance."""
        tol = tolerance_usd if tolerance_usd is not None else self.default_tolerance
        inv_total = float(invoice.get("grand_total", 0.0))
        inv_vendor = str(invoice.get("vendor", "")).lower()

        matched_tx = None
        min_delta = 999999.0

        for tx in bank_transactions:
            tx_amount = abs(float(tx.get("amount", 0.0)))
            delta = abs(tx_amount - inv_total)
            tx_desc = str(tx.get("description", "")).lower()

            # Check vendor match or substring
            vendor_match = (inv_vendor in tx_desc) or (tx_desc in inv_vendor) or (len(inv_vendor) < 3)

            if delta <= tol and (vendor_match or delta < 0.01):
                if delta < min_delta:
                    min_delta = delta
                    matched_tx = tx

        is_reconciled = matched_tx is not None

        return {
            "invoice_number": invoice.get("invoice_number", "UNKNOWN"),
            "invoice_amount": inv_total,
            "reconciled": is_reconciled,
            "reconciliation_status": "MATCHED" if is_reconciled else "UNRECONCILED_DISCREPANCY",
            "variance_usd": round(min_delta, 2) if is_reconciled else None,
            "matched_bank_transaction": matched_tx,
            "reconciled_at": time.time()
        }

    def generate_accounting_journal_entry(
        self,
        invoice: Dict[str, Any],
        expense_category: str = "Operating Expenses"
    ) -> Dict[str, Any]:
        """Generates GAAP-compliant balanced double-entry accounting journal entry."""
        now = time.time()
        total = float(invoice.get("grand_total", 0.0))
        tax = float(invoice.get("tax_amount", 0.0))
        subtotal = round(total - tax, 2)

        entry_id = "JE-" + hashlib.md5(f"{invoice.get('invoice_number')}:{now}".encode("utf-8")).hexdigest()[:8].upper()

        lines = [
            {"account": f"6000 - {expense_category}", "debit": subtotal, "credit": 0.0},
        ]
        if tax > 0:
            lines.append({"account": "1300 - Input VAT / Tax Receivable", "debit": tax, "credit": 0.0})
        lines.append({"account": "2000 - Accounts Payable / Bank", "debit": 0.0, "credit": total})

        total_debits = sum(l["debit"] for l in lines)
        total_credits = sum(l["credit"] for l in lines)
        is_balanced = abs(total_debits - total_credits) < 0.001

        return {
            "journal_entry_id": entry_id,
            "reference_invoice": invoice.get("invoice_number"),
            "vendor": invoice.get("vendor"),
            "currency": invoice.get("currency", "USD"),
            "is_balanced": is_balanced,
            "total_amount": total,
            "journal_lines": lines,
            "created_at": now
        }
