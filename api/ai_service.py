import httpx
import os
from typing import Dict, List


class GrokAIService:
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise Exception("XAI_API_KEY not found in environment variables")

        self.model = "llama-3.3-70b-versatile"
        self.api_url = "https://api.x.ai/v1/chat/completions"

    async def get_financial_advice(
            self,
            user_query: str,
            transactions: List[Dict] = None,
            goals: List[Dict] = None,
            stats: Dict = None
    ) -> str:
        """Get financial advice from Grok AI based on user data"""

        # Build context from user data
        context = self._build_context(transactions, goals, stats)

        # Create system prompt
        system_prompt = """You are a financial advisor AI assistant. Analyze user's financial data and provide personalized advice.
Be concise, actionable, and friendly. Focus on savings, spending patterns, and goal achievement."""

        # Create user message with context
        user_message = f"""User Query: {user_query}

Financial Context:
{context}

Provide helpful financial advice based on this data."""

        # Call Grok API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Grok API error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Failed to get AI advice: {str(e)}")

    def _build_context(self, transactions: List[Dict], goals: List[Dict], stats: Dict) -> str:
        """Build context string from user's financial data"""
        context_parts = []

        # Add stats
        if stats:
            context_parts.append(f"""
Financial Overview:
- Total Balance: ${stats.get('total_balance', 0):.2f}
- Monthly Income: ${stats.get('monthly_income', 0):.2f}
- Monthly Expenses: ${stats.get('monthly_expenses', 0):.2f}
- Savings Rate: {stats.get('savings_rate', 0):.1f}%
""")

        # Add recent transactions
        if transactions and len(transactions) > 0:
            context_parts.append("\nRecent Transactions:")
            for txn in transactions[:10]:  # Last 10 transactions
                context_parts.append(
                    f"- {txn.get('title', 'N/A')}: ${abs(txn.get('amount', 0)):.2f} ({txn.get('category', 'N/A')})"
                )

        # Add goals
        if goals and len(goals) > 0:
            context_parts.append("\nFinancial Goals:")
            for goal in goals:
                progress = (goal.get('current', 0) / goal.get('target', 1)) * 100
                context_parts.append(
                    f"- {goal.get('title', 'N/A')}: ${goal.get('current', 0):.2f} / ${goal.get('target', 0):.2f} ({progress:.0f}%)"
                )

        return "\n".join(context_parts)

    async def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze spending patterns using Grok AI"""

        if not transactions:
            return {"analysis": "No transactions to analyze"}

        # Prepare transaction summary
        categories = {}
        for txn in transactions:
            if txn.get('type') == 'expense':
                category = txn.get('category', 'Other')
                amount = abs(txn.get('amount', 0))
                categories[category] = categories.get(category, 0) + amount

        summary = "\n".join([f"- {cat}: ${amt:.2f}" for cat, amt in categories.items()])

        prompt = f"""Analyze these spending patterns and provide insights:

{summary}

Provide:
1. Top spending category
2. Potential savings opportunities
3. One actionable recommendation"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 300
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "analysis": data["choices"][0]["message"]["content"],
                        "categories": categories
                    }
                else:
                    return {"analysis": "Unable to analyze spending patterns", "categories": categories}

        except Exception as e:
            return {"analysis": f"Error: {str(e)}", "categories": categories}