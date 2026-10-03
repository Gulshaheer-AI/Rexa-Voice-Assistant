"""
File-based Business Data Connector for Rexa.
Supports loading business metrics from JSON, CSV, and Excel (.xlsx) files.
Features automatic caching and hot-reloading when files are updated on disk.
"""

import os
import json
import csv
import time
from typing import Dict, Any, List, Optional
from .base import BaseBusinessConnector


class FileBusinessConnector(BaseBusinessConnector):
    """
    Connects Rexa to local files (JSON, CSV, Excel).
    Any business can drop their daily export file into the data folder
    and have Rexa report on their metrics immediately.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_dir = self.config.get("data_dir", "data")
        self.json_path = self.config.get("json_path", os.path.join(self.data_dir, "business_data.json"))
        self.csv_campaigns_path = self.config.get("csv_campaigns_path", os.path.join(self.data_dir, "campaigns.csv"))
        self.csv_sales_path = self.config.get("csv_sales_path", os.path.join(self.data_dir, "sales.csv"))
        self.excel_path = self.config.get("excel_path", os.path.join(self.data_dir, "business_data.xlsx"))
        
        self.currency = self.config.get("currency", "USD")
        self.business_name = self.config.get("business_name", "Our Business")
        self.cache_ttl = self.config.get("cache_duration_seconds", 60)

        self._cached_data: Dict[str, Any] = {}
        self._last_loaded_time: float = 0

    def _is_cache_expired(self) -> bool:
        return (time.time() - self._last_loaded_time) > self.cache_ttl

    def load_data(self) -> Dict[str, Any]:
        """Loads business data from available JSON, CSV, or Excel files."""
        if self._cached_data and not self._is_cache_expired():
            return self._cached_data

        combined_data: Dict[str, Any] = {
            "business_name": self.business_name,
            "currency": self.currency,
            "financials": {},
            "campaigns": [],
            "top_products": [],
            "notes": []
        }

        # 1. Attempt to load JSON data
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    if isinstance(json_data, dict):
                        combined_data["business_name"] = json_data.get("business_name", self.business_name)
                        combined_data["currency"] = json_data.get("currency", self.currency)
                        combined_data["financials"].update(json_data.get("financials", {}))
                        combined_data["campaigns"].extend(json_data.get("campaigns", []))
                        combined_data["top_products"].extend(json_data.get("top_products", []))
                        combined_data["notes"].extend(json_data.get("notes", []))
            except Exception as e:
                print(f"[FileBusinessConnector] Warning loading JSON ({self.json_path}): {e}")

        # 2. Attempt to load Campaigns CSV (supplements or overrides JSON campaigns)
        if os.path.exists(self.csv_campaigns_path):
            try:
                csv_campaigns = self._read_csv_campaigns(self.csv_campaigns_path)
                if csv_campaigns:
                    combined_data["campaigns"] = csv_campaigns
            except Exception as e:
                print(f"[FileBusinessConnector] Warning loading Campaigns CSV: {e}")

        # 3. Attempt to load Sales CSV (supplements daily financials)
        if os.path.exists(self.csv_sales_path):
            try:
                sales_metrics = self._read_csv_sales(self.csv_sales_path)
                if sales_metrics:
                    combined_data["financials"].update(sales_metrics)
            except Exception as e:
                print(f"[FileBusinessConnector] Warning loading Sales CSV: {e}")

        # 4. Attempt to load Excel if present and openpyxl is installed
        if os.path.exists(self.excel_path):
            try:
                self._load_excel_data(self.excel_path, combined_data)
            except Exception as e:
                print(f"[FileBusinessConnector] Warning loading Excel: {e}")

        self._cached_data = combined_data
        self._last_loaded_time = time.time()
        return self._cached_data

    def _read_csv_campaigns(self, file_path: str) -> List[Dict[str, Any]]:
        """Parses a CSV file containing marketing campaign metrics."""
        campaigns = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize keys to lowercase for resilient mapping
                norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                campaigns.append({
                    "name": norm_row.get("campaign", norm_row.get("name", "Unnamed Campaign")),
                    "channel": norm_row.get("channel", norm_row.get("platform", "General")),
                    "status": norm_row.get("status", "Active"),
                    "spend": norm_row.get("spend", norm_row.get("cost", "0")),
                    "revenue": norm_row.get("revenue", "0"),
                    "conversions": norm_row.get("conversions", norm_row.get("leads", norm_row.get("sales", "0"))),
                    "roas": norm_row.get("roas", norm_row.get("roi", "N/A"))
                })
        return campaigns

    def _read_csv_sales(self, file_path: str) -> Dict[str, Any]:
        """Parses a CSV file containing sales and profit figures."""
        metrics = {}
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            total_rev = 0.0
            total_prof = 0.0
            total_exp = 0.0
            order_count = 0
            for row in reader:
                norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                try:
                    rev = float(norm_row.get("revenue", norm_row.get("amount", 0)))
                    exp = float(norm_row.get("expense", norm_row.get("cost", 0)))
                    prof = float(norm_row.get("profit", rev - exp))
                    total_rev += rev
                    total_exp += exp
                    total_prof += prof
                    order_count += 1
                except (ValueError, TypeError):
                    continue
            
            if order_count > 0:
                metrics["total_sales_revenue"] = total_rev
                metrics["total_sales_profit"] = total_prof
                metrics["total_sales_expenses"] = total_exp
                metrics["orders_count"] = order_count
        return metrics

    def _load_excel_data(self, file_path: str, data_store: Dict[str, Any]):
        """Optional parser for .xlsx files using openpyxl if available."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            if "Financials" in wb.sheetnames:
                sheet = wb["Financials"]
                for row in sheet.iter_rows(values_only=True):
                    if row and len(row) >= 2 and row[0]:
                        key = str(row[0]).strip().lower().replace(" ", "_")
                        data_store["financials"][key] = row[1]
        except ImportError:
            # openpyxl is optional; log once and continue
            pass

    def get_financials(self) -> Dict[str, Any]:
        data = self.load_data()
        return data.get("financials", {})

    def get_campaigns(self) -> List[Dict[str, Any]]:
        data = self.load_data()
        return data.get("campaigns", [])

    def get_summary_context(self) -> str:
        """
        Creates a clean, human-readable summary of all live business data
        to be inserted directly into the AI prompt.
        """
        data = self.load_data()
        curr = data.get("currency", self.currency)
        name = data.get("business_name", self.business_name)
        fin = data.get("financials", {})
        camps = data.get("campaigns", [])
        prods = data.get("top_products", [])
        notes = data.get("notes", [])

        lines = [
            f"=== Business Intelligence Report for {name} ===",
            f"Currency: {curr}"
        ]

        # Financial Summary
        lines.append("\n[Financial Performance]:")
        if fin:
            for k, v in fin.items():
                label = k.replace("_", " ").title()
                is_non_currency = any(non_curr in k.lower() for non_curr in ["order", "count", "unit", "rate", "percent", "margin"])
                if isinstance(v, float):
                    if is_non_currency:
                        lines.append(f"- {label}: {v:,.2f}")
                    else:
                        lines.append(f"- {label}: {curr} {v:,.2f}")
                elif isinstance(v, int):
                    if is_non_currency:
                        lines.append(f"- {label}: {v:,}")
                    else:
                        lines.append(f"- {label}: {curr} {v:,}")
                else:
                    lines.append(f"- {label}: {v}")
        else:
            lines.append("- No financial metrics recorded for today.")

        # Marketing Campaigns
        lines.append("\n[Marketing Campaigns]:")
        if camps:
            for c in camps:
                c_name = c.get("name", "Unknown")
                c_channel = c.get("channel", "General")
                c_status = c.get("status", "Active")
                c_spend = c.get("spend", "0")
                c_rev = c.get("revenue", "0")
                c_roas = c.get("roas", "N/A")
                c_conv = c.get("conversions", "0")
                lines.append(
                    f"- '{c_name}' ({c_channel}) | Status: {c_status} | Spend: {curr} {c_spend} | "
                    f"Revenue: {curr} {c_rev} | Conversions: {c_conv} | ROAS: {c_roas}"
                )
        else:
            lines.append("- No active marketing campaigns reported.")

        # Top Products
        if prods:
            lines.append("\n[Top Selling Products / Services]:")
            for p in prods:
                p_name = p.get("name", "Item")
                p_units = p.get("units_sold", "N/A")
                p_rev = p.get("revenue", "N/A")
                lines.append(f"- {p_name}: {p_units} units sold | Revenue: {curr} {p_rev}")

        # Operational Notes
        if notes:
            lines.append("\n[Management Notes & Alerts]:")
            for note in notes:
                lines.append(f"- {note}")

        return "\n".join(lines)
