"""Example usage for AgenticMultimodalInvoiceReceiptReconciler."""
import sys
import json
from client import AgenticMultimodalInvoiceReceiptReconciler

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== Agentic Financial Invoice & Receipt Reconciler Demo ===")
    reconciler = AgenticMultimodalInvoiceReceiptReconciler()

    receipt_raw = """
Vendor: Stripe Payments US Inc.
Invoice: INV-STRIPE-40912
Date: 2026-10-07
Platform Usage: $1,200.00
Tax / Processing Fees: $36.00
Grand Total: $1,236.00
"""

    # 1. Parse structured metadata & tax rate
    print("\n--- 1. Parsing Receipt Metadata & Tax Breakdown ---")
    inv = reconciler.parse_invoice_metadata(receipt_raw)
    print(f"Vendor: {inv['vendor']} | Inv: {inv['invoice_number']}")
    print(f"Total: ${inv['grand_total']:.2f} (Tax: ${inv['tax_amount']:.2f}, Est Rate: {inv['tax_rate_estimated']}%)")

    # 2. Reconcile against bank statement feed
    print("\n--- 2. Three-Way Reconciliation Against Bank Feed ---")
    bank_feed = [
        {"id": "tx_901", "description": "STRIPE PAYMENTS FEE", "amount": -1236.00, "date": "2026-10-07"},
        {"id": "tx_902", "description": "AWS INFRASTRUCTURE", "amount": -4500.00, "date": "2026-10-06"}
    ]
    reconciliation = reconciler.reconcile_against_bank_ledger(inv, bank_feed)
    print(f"Status: {reconciliation['reconciliation_status']} | Match: {reconciliation['reconciled']}")
    print(f"Matched Tx: {reconciliation['matched_bank_transaction']['description']} (${reconciliation['matched_bank_transaction']['amount']})")

    # 3. Generate double-entry bookkeeping journal entries
    print("\n--- 3. Synthesizing GAAP Double-Entry Journal Entry ---")
    journal = reconciler.generate_accounting_journal_entry(inv, "Payment Gateway Processing Fees")
    print(f"Journal ID: {journal['journal_entry_id']} | Balanced: {journal['is_balanced']}")
    for line in journal["journal_lines"]:
        print(f"  {line['account']:<42} Dr: ${line['debit']:>8.2f} | Cr: ${line['credit']:>8.2f}")

if __name__ == "__main__":
    main()
