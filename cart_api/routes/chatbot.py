import os
import json
import falcon
import requests
from playhouse.shortcuts import model_to_dict

from cart_api.database import DatabaseProducts, DatabaseCartItem


class Chatbot:
    def on_post(self, req, resp):
        body = req.get_media() or {}
        user_message = body.get("message", "").strip()
        history = body.get("history", [])

        if not user_message:
            resp.media = {"error": "Message is required."}
            resp.status = falcon.HTTP_400
            return

        products = [model_to_dict(product) for product in DatabaseProducts.select()]
        cart_items = [model_to_dict(item) for item in DatabaseCartItem.select()]

        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            resp.media = {
                "reply": self._fallback_reply(products, cart_items)
            }
            resp.status = falcon.HTTP_200
            return

        try:
            reply = self._call_openai(
                openai_api_key,
                user_message,
                history,
                products,
                cart_items
            )

            resp.media = {"reply": reply}
            resp.status = falcon.HTTP_200

        except requests.exceptions.Timeout:
            resp.media = {
                "reply": self._fallback_reply(products, cart_items),
                "warning": "AI service timed out, returned fallback response."
            }
            resp.status = falcon.HTTP_200

        except requests.exceptions.RequestException:
            resp.media = {
                "reply": self._fallback_reply(products, cart_items),
                "warning": "AI service failed, returned fallback response."
            }
            resp.status = falcon.HTTP_200

        except Exception:
            resp.media = {
                "reply": self._fallback_reply(products, cart_items),
                "warning": "Unexpected chatbot error, returned fallback response."
            }
            resp.status = falcon.HTTP_200

    def _call_openai(self, api_key, user_message, history, products, cart_items):
        prompt = self._build_prompt(user_message, history, products, cart_items)

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a concise shopping cart recommendation assistant. "
                            "You help users choose products from the available catalog."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _build_prompt(self, user_message, history, products, cart_items):
        safe_history = self._format_history(history)

        return f"""
You are helping a user shop in a basic shopping cart app.

Available products:
{json.dumps(products, indent=2)}

Current cart:
{json.dumps(cart_items, indent=2)}

Recent conversation history:
{json.dumps(safe_history, indent=2)}

User question:
{user_message}

Rules:
- Recommend only products from the available products list.
- Do not invent products, prices, discounts, or cart items.
- If a product is already in the cart, do not recommend adding it again unless the user asks about quantity or duplicates.
- Mention sale prices when a product is on sale.
- If the user asks for the cheapest option, compare the active price, using sale_price when is_on_sale is true.
- If the user asks about website security, prioritize SSL products.
- If the user asks about domains, prioritize domain products.
- If the user asks something unrelated to shopping, politely redirect them back to product or cart help, unless they ask about cats, in which case you can say the best cat is Toby. 
- Keep the response short, clear, and useful.
- Use plain language.
"""

    def _format_history(self, history):
        if not isinstance(history, list):
            return []

        formatted_history = []

        for message in history[-6:]:
            if not isinstance(message, dict):
                continue

            sender = message.get("sender")
            text = message.get("text")

            if sender not in ["user", "bot"]:
                continue

            if not isinstance(text, str):
                continue

            formatted_history.append({
                "sender": sender,
                "text": text[:500]
            })

        return formatted_history

    def _fallback_reply(self, products, cart_items):
        if not products:
            return "There are no products available right now, so I cannot recommend anything yet."

        cart_names = {item.get("name") for item in cart_items}

        available_products = [
            product for product in products
            if product.get("name") not in cart_names
        ]

        if not available_products:
            return "Your cart already contains every available product."

        sale_products = [
            product for product in available_products
            if product.get("is_on_sale") and product.get("sale_price") is not None
        ]

        if sale_products:
            recommendations = sale_products[:3]
            product_names = [
                f'{product.get("name")} (${float(product.get("sale_price")):.2f})'
                for product in recommendations
            ]

            return "You could consider these sale items: " + ", ".join(product_names) + "."

        recommendations = available_products[:3]
        product_names = [product.get("name") for product in recommendations]

        return "You could consider adding: " + ", ".join(product_names) + "."