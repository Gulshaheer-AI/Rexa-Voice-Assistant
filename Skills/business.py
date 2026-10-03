"""
Rexa Business Intelligence Skill.
Intercepts managerial business queries (profits, campaigns, revenue, expenses, reports)
and delivers concise, spoken voice analytics in English and Urdu.
"""

import os
import json
import google.generativeai as genai
from .rules import Skill
from connectors.file_connector import FileBusinessConnector


class BusinessSkill(Skill):
    def __init__(self, config_path: str = "config/business_config.json"):
        self.config = self._load_config(config_path)
        self.business_name = self.config.get("business_name", "Our Business")
        self.currency = self.config.get("currency", "USD")
        
        # Initialize Connector
        connector_type = self.config.get("active_connector", "file")
        if connector_type == "file":
            file_cfg = self.config.get("files", {})
            file_cfg["currency"] = self.currency
            file_cfg["business_name"] = self.business_name
            file_cfg["cache_duration_seconds"] = self.config.get("cache_duration_seconds", 60)
            self.connector = FileBusinessConnector(file_cfg)
        else:
            self.connector = FileBusinessConnector({"currency": self.currency, "business_name": self.business_name})

        # Gemini Model for Business Analytics
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Intent triggers (English & Urdu / Roman Urdu)
        self.triggers = [
            # English business triggers
            "profit", "revenue", "sales", "campaign", "campaigns", "marketing",
            "expenses", "expense", "loss", "roas", "roi", "budget", "turnover",
            "business report", "business performance", "top product", "best seller",
            "orders today", "cash in bank",
            # Urdu / Roman Urdu business triggers
            "munafa", "kamai", "bachat", "kharcha", "kharch", "nuqsan",
            "karobar", "bikri", "tijarat", "tijarati", "kitna profit",
            "campaign kaisi", "campaign kaisa", "order kitne"
        ]

    def _load_config(self, path: str) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[BusinessSkill] Warning reading config ({path}): {e}")
        return {
            "business_name": "Our Business",
            "currency": "USD",
            "active_connector": "file"
        }

    def matches(self, command: str) -> bool:
        cmd = command.lower()
        for trigger in self.triggers:
            if trigger in cmd:
                return True
        return False

    def execute(self, command: str, speak):
        # 1. Fetch live business context
        try:
            context = self.connector.get_summary_context()
        except Exception as e:
            print(f"[BusinessSkill] Error reading business context: {e}")
            speak("I was unable to load the latest business data, sir.")
            return

        # 2. Query Gemini with Business Intelligence persona
        prompt = f"""
You are Rexa, executive business intelligence advisor for {self.business_name}.
Here is the live verified business data snapshot:

{context}

Manager's spoken voice query: "{command}"

Instructions:
1. Answer the manager's question directly and concisely based strictly on the business data above.
2. If the user asked in Urdu or Roman Urdu (e.g. asking about 'munafa', 'kamai', 'campaign kaisi hai'), respond politely in natural spoken Urdu / Roman Urdu.
3. If the user asked in English, respond in clear, confident spoken English.
4. Keep the answer to 1 or 2 spoken sentences maximum.
5. Plain text ONLY. Do NOT use markdown, asterisks, bullet points, or special characters.
6. Always state exact numbers and currency clearly.
"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text.replace("*", "").replace("#", "").strip()
            speak(answer)
        except Exception as e:
            print(f"[BusinessSkill] Gemini query error: {e}")
            # Resilient direct offline fallback
            self._offline_fallback_reply(command, speak)

    def _offline_fallback_reply(self, command: str, speak):
        """Rule-based local fallback in case Gemini connection is offline."""
        cmd = command.lower()
        fin = self.connector.get_financials()
        camps = self.connector.get_campaigns()
        curr = self.currency

        # Urdu language check
        is_urdu = any(u in cmd for u in ["munafa", "kamai", "kharcha", "kaisi", "kaisa", "kitna"])

        if "profit" in cmd or "munafa" in cmd or "kamai" in cmd:
            profit = fin.get("todays_profit", "not recorded")
            if is_urdu:
                speak(f"Sir, aaj ka munafa {curr} {profit:,} hai.")
            else:
                speak(f"Sir, today's profit is {curr} {profit:,}.")
        elif "revenue" in cmd or "bikri" in cmd or "sales" in cmd:
            rev = fin.get("todays_revenue", "not recorded")
            if is_urdu:
                speak(f"Sir, aaj ki total revenue {curr} {rev:,} hai.")
            else:
                speak(f"Sir, today's total revenue is {curr} {rev:,}.")
        elif "campaign" in cmd:
            if camps:
                c = camps[0]
                name = c.get("name", "campaign")
                roas = c.get("roas", "good")
                if is_urdu:
                    speak(f"Sir, {name} active hai aur iska ROAS {roas} chal raha hai.")
                else:
                    speak(f"Sir, your {name} is active and currently performing at a {roas} ROAS.")
            else:
                speak("No active campaigns were found in your records.")
        else:
            if is_urdu:
                speak("Main business data parhne mein masla mehsoos kar rahi hoon.")
            else:
                speak("I have processed your business request, but please check your network connection for full analytics.")
