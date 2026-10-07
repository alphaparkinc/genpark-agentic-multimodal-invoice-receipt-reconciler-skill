# genpark-agentic-multimodal-invoice-receipt-reconciler-skill

[![GenPark AI](https://img.shields.io/badge/GenPark-AI%20Skill-blue.svg)](https://genpark.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-0%20(Pure%20Stdlib)-brightgreen.svg)](requirements.txt)
[![MCP Compliant](https://img.shields.io/badge/MCP-JSON--RPC%202.0-purple.svg)](mcp_server.py)

Autonomous Multi-Modal Invoice & Receipt Reconciler. Parses structured financial receipts, invoices, and bank statements, performs tolerance-based three-way reconciliation, detects tax calculation drift and duplicate claims, and synthesizes double-entry bookkeeping journal entries.

---

## 🌟 Key Features

- **100% Zero External Dependencies**: Runs entirely on the Python 3.9+ standard library.
- **Model Context Protocol (MCP) Standard**: Native support for JSON-RPC 2.0 `initialize`, `tools/list`, and `tools/call`.
- **Industrial-Grade Determinism**: Rigorous exception isolation, predictable algorithmic complexity, and type annotations.
- **Dual Deployment Ecosystem**: Verified across `alphaparkinc` and `Alpha-Park` organizations with multi-account validation.

---

## 🚀 Quick Start

### 1. Direct Python SDK Usage

```python
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

```

### 2. Run as Model Context Protocol (MCP) Server

Start standard JSON-RPC 2.0 server over `stdio`:

```bash
python mcp_server.py
```

Execute embedded test harness:

```bash
python mcp_server.py --test
```

---

## 🛠️ MCP Tool Specification

Inspect [`skill.json`](skill.json) for parameter schemas and tool definitions compatible with Anthropic Claude, Meta Muse, and OpenAI Function Calling formats.

---

## 📜 License

Licensed under the [MIT License](LICENSE). Copyright © 2026 GenPark AI.
