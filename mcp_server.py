"""MCP Server for Agentic Multimodal Invoice Receipt Reconciler."""
import sys
import json
import time
from client import AgenticMultimodalInvoiceReceiptReconciler

reconciler = AgenticMultimodalInvoiceReceiptReconciler()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "reconcile_invoice_receipt":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "reconcile_against_bank_ledger")
    if action == "parse_invoice_metadata":
        return reconciler.parse_invoice_metadata(args.get("invoice_text", ""))
    elif action == "reconcile_against_bank_ledger":
        return reconciler.reconcile_against_bank_ledger(
            invoice=args.get("invoice_data", {}),
            bank_transactions=args.get("bank_statement_transactions", []),
            tolerance_usd=args.get("tolerance_usd")
        )
    elif action == "generate_accounting_journal_entry":
        return reconciler.generate_accounting_journal_entry(
            invoice=args.get("invoice_data", {}),
            expense_category=args.get("expense_category", "Cloud Services")
        )
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        sample_inv_text = "Vendor: Tencent Cloud Services\nInvoice #INV-2026-8819\nSubtotal: $450.00\nTax: $45.00\nTotal: $495.00"
        inv = reconciler.parse_invoice_metadata(sample_inv_text)
        assert inv["invoice_number"] == "INV-2026-8819"
        assert inv["grand_total"] == 495.00
        assert inv["tax_amount"] == 45.00

        bank_txs = [
            {"id": "tx_01", "description": "Tencent Cloud Payment", "amount": -495.00, "date": "2026-10-06"},
            {"id": "tx_02", "description": "Office Supplies", "amount": -89.50, "date": "2026-10-05"}
        ]
        rec = reconciler.reconcile_against_bank_ledger(inv, bank_txs)
        assert rec["reconciled"] is True
        assert rec["reconciliation_status"] == "MATCHED"

        je = reconciler.generate_accounting_journal_entry(inv, "Cloud Infrastructure")
        assert je["is_balanced"] is True
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "AgenticMultimodalInvoiceReceiptReconciler", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "reconcile_invoice_receipt",
                            "description": "Extract financial metadata, verify VAT/sales tax calculations, reconcile invoices against bank transaction feeds, and synthesize double-entry journal entries.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["parse_invoice_metadata", "reconcile_against_bank_ledger", "generate_accounting_journal_entry"]},
                                    "invoice_data": {"type": "object"},
                                    "bank_statement_transactions": {"type": "array"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
