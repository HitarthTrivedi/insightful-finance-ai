import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx


class AIAdvisorService:
    """
    AI Financial Advisor Service
    Optimized for xAI Grok API (Llama 3.3 70B)
    """

    def __init__(self, provider: str = "xai"):
        """
        Initialize AI service with specified provider
        Args:
            provider: "openai", "anthropic", or "xai" (default: xai)
        """
        self.provider = provider
        self._setup_client()

    def _setup_client(self):
        """Setup the AI client based on provider"""
        if self.provider == "openai":
            try:
                import openai
                self.client = openai
                self.client.api_key = os.getenv("OPENAI_API_KEY")
            except ImportError:
                raise ImportError("Install openai: pip install openai")

        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            except ImportError:
                raise ImportError("Install anthropic: pip install anthropic")

        elif self.provider == "xai":
            # xAI Grok integration with Llama 3.3 70B
            self.api_key = os.getenv("XAI_API_KEY")
            if not self.api_key:
                raise ValueError("XAI_API_KEY not found in environment variables")

            self.base_url = "https://api.x.ai/v1"
            self.model = "grok-beta"  # Using Llama 3.3 70B
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )

    def generate_financial_context(
            self,
            transactions: List,
            goals: List,
            stats: Dict
    ) -> str:
        """
        Generate context about user's financial situation
        """
        context_parts = []

        # Add stats context
        context_parts.append(f"Current Financial Overview:")
        context_parts.append(f"- Total Balance: ${stats.get('total_balance', 0):,.2f}")
        context_parts.append(f"- Monthly Income: ${stats.get('monthly_income', 0):,.2f}")
        context_parts.append(f"- Monthly Expenses: ${stats.get('monthly_expenses', 0):,.2f}")
        context_parts.append(f"- Savings Rate: {stats.get('savings_rate', 0):.1f}%\n")

        # Add recent transactions
        if transactions:
            context_parts.append("Recent Transactions:")
            for t in transactions[:10]:
                context_parts.append(
                    f"- {t.title}: ${abs(t.amount):,.2f} ({t.category}) - {t.date.strftime('%Y-%m-%d')}"
                )
            context_parts.append("")

        # Add goals
        if goals:
            context_parts.append("Financial Goals:")
            for g in goals:
                progress = (g.current / g.target * 100) if g.target > 0 else 0
                context_parts.append(
                    f"- {g.title}: ${g.current:,.2f} / ${g.target:,.2f} ({progress:.1f}%)"
                )
            context_parts.append("")

        return "\n".join(context_parts)

    def get_advice(
            self,
            question: str,
            transactions: List,
            goals: List,
            stats: Dict
    ) -> Dict[str, any]:
        """
        Get AI-powered financial advice
        """
        context = self.generate_financial_context(transactions, goals, stats)

        system_prompt = """You are an expert financial advisor AI powered by Llama 3.3 70B. 
        Analyze the user's financial data and provide personalized, actionable advice. 
        Be specific with numbers and recommendations. Focus on practical tips for saving, 
        budgeting, and reaching financial goals. Keep responses concise but informative."""

        user_prompt = f"{context}\n\nUser Question: {question}\n\nProvide detailed advice:"

        try:
            if self.provider == "xai":
                return self._get_xai_advice(system_prompt, user_prompt)
            elif self.provider == "openai":
                return self._get_openai_advice(system_prompt, user_prompt)
            elif self.provider == "anthropic":
                return self._get_anthropic_advice(system_prompt, user_prompt)
        except Exception as e:
            print(f"AI Error: {str(e)}")
            return self._get_fallback_advice(question, transactions, stats)

    def _get_openai_advice(self, system_prompt: str, user_prompt: str) -> Dict:
        """Get advice from OpenAI GPT"""
        response = self.client.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        advice_text = response.choices[0].message.content
        return self._parse_advice_response(advice_text)

    def _get_anthropic_advice(self, system_prompt: str, user_prompt: str) -> Dict:
        """Get advice from Anthropic Claude"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        advice_text = message.content[0].text
        return self._parse_advice_response(advice_text)

    def _get_xai_advice(self, system_prompt: str, user_prompt: str) -> Dict:
        """Get advice from xAI Grok (Llama 3.3 70B)"""
        import asyncio

        async def make_request():
            try:
                response = await self.client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    advice_text = data["choices"][0]["message"]["content"]
                    return self._parse_advice_response(advice_text)
                else:
                    raise ValueError("Invalid response format from xAI API")

            except httpx.HTTPStatusError as e:
                print(f"xAI API Error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                print(f"xAI Request Error: {str(e)}")
                raise

        # Run async function
        return asyncio.run(make_request())

    def _parse_advice_response(self, advice_text: str) -> Dict:
        """Parse AI response into structured format"""
        # Extract suggestions if AI formatted them
        suggestions = []
        lines = advice_text.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                suggestions.append(line[2:])
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                suggestions.append(line.split('.', 1)[1].strip())

        return {
            "response": advice_text,
            "suggestions": suggestions[:5] if suggestions else [
                "Review your spending patterns",
                "Consider automating savings",
                "Track your progress regularly"
            ]
        }

    def _get_fallback_advice(
            self,
            question: str,
            transactions: List,
            stats: Dict
    ) -> Dict:
        """Provide rule-based advice when AI is unavailable"""
        advice_parts = []
        suggestions = []

        # Analyze savings rate
        savings_rate = stats.get('savings_rate', 0)
        if savings_rate < 20:
            advice_parts.append(
                f"Your savings rate is {savings_rate:.1f}%, which is below the "
                f"recommended 20%. Consider reducing discretionary spending."
            )
            suggestions.append("Aim to save at least 20% of your income")
        else:
            advice_parts.append(
                f"Great job! Your savings rate of {savings_rate:.1f}% is above average."
            )

        # Analyze expense categories
        if transactions:
            category_totals = {}
            for t in transactions:
                if t.type == "expense":
                    category_totals[t.category] = category_totals.get(t.category, 0) + abs(t.amount)

            if category_totals:
                highest_category = max(category_totals.items(), key=lambda x: x[1])
                advice_parts.append(
                    f"\n\nYour highest spending category is {highest_category[0]} "
                    f"at ${highest_category[1]:,.2f}. Review if this aligns with your priorities."
                )
                suggestions.append(f"Review and optimize {highest_category[0]} expenses")

        suggestions.extend([
            "Set up automatic savings transfers",
            "Create an emergency fund (3-6 months expenses)",
            "Track daily expenses with a budgeting app",
            "Review subscriptions and cut unused ones"
        ])

        return {
            "response": " ".join(advice_parts) if advice_parts else
            "Based on your financial data, focus on consistent saving and tracking expenses.",
            "suggestions": suggestions[:5]
        }

    def analyze_spending_patterns(self, transactions: List) -> Dict:
        """Analyze spending patterns and identify trends"""
        if not transactions:
            return {"message": "No transactions to analyze"}

        # Group by category
        categories = {}
        monthly_spending = {}

        for t in transactions:
            if t.type == "expense":
                # Category totals
                categories[t.category] = categories.get(t.category, 0) + abs(t.amount)

                # Monthly totals
                month_key = t.date.strftime("%Y-%m")
                monthly_spending[month_key] = monthly_spending.get(month_key, 0) + abs(t.amount)

        # Find highest category
        highest_category = max(categories.items(), key=lambda x: x[1]) if categories else None

        # Calculate trend
        months = sorted(monthly_spending.keys())
        trend = "stable"
        if len(months) >= 2:
            recent = monthly_spending[months[-1]]
            previous = monthly_spending[months[-2]]
            change_pct = ((recent - previous) / previous * 100) if previous > 0 else 0

            if change_pct > 10:
                trend = "increasing"
            elif change_pct < -10:
                trend = "decreasing"

        return {
            "highest_category": highest_category[0] if highest_category else None,
            "highest_amount": highest_category[1] if highest_category else 0,
            "monthly_trend": trend,
            "categories": categories,
            "monthly_spending": monthly_spending
        }

    def suggest_budget(self, monthly_income: float) -> Dict:
        """Suggest budget allocation based on 50/30/20 rule"""
        if monthly_income <= 0:
            return {"error": "Invalid income amount"}

        return {
            "needs": {
                "amount": monthly_income * 0.5,
                "percentage": 50,
                "description": "Housing, food, utilities, transportation"
            },
            "wants": {
                "amount": monthly_income * 0.3,
                "percentage": 30,
                "description": "Entertainment, dining out, hobbies"
            },
            "savings": {
                "amount": monthly_income * 0.2,
                "percentage": 20,
                "description": "Emergency fund, investments, debt repayment"
            }
        }

    def predict_goal_completion(self, goal_target: float, current_amount: float,
                                monthly_contribution: float) -> Dict:
        """Predict when a financial goal will be reached"""
        if monthly_contribution <= 0:
            return {"error": "Monthly contribution must be positive"}

        remaining = goal_target - current_amount
        if remaining <= 0:
            return {"message": "Goal already achieved!", "months_remaining": 0}

        months_needed = remaining / monthly_contribution
        completion_date = datetime.now() + timedelta(days=months_needed * 30)

        return {
            "months_remaining": round(months_needed, 1),
            "estimated_completion": completion_date.strftime("%B %Y"),
            "monthly_contribution_needed": monthly_contribution,
            "total_remaining": remaining
        }