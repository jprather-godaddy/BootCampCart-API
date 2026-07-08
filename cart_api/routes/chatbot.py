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
                products,
                cart_items
            )

            resp.media = {"reply": reply}
            resp.status = falcon.HTTP_200

        except Exception:
            resp.media = {
                "reply": self._fallback_reply(products, cart_items),
                "warning": "AI service failed, returned fallback response."
            }
            resp.status = falcon.HTTP_200

    def _call_openai(self, api_key, user_message, products, cart_items):
        prompt = f"""
You are a shopping assistant for a basic shopping cart app.

Available products:
{json.dumps(products, indent=2)}

Current cart:
{json.dumps(cart_items, indent=2)}

User question:
{user_message}

Rules:
- Recommend only products from the available products list.
- Do not invent products, prices, discounts, or cart items.
- Be concise.
- Suggest 1 to 3 products when useful.
- Explain the recommendation in plain language.
"""

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
                        "content": "You are a concise shopping cart recommendation assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 250
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

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

        recommendations = available_products[:3]
        product_names = [product.get("name") for product in recommendations]

        return "You could consider adding: " + ", ".join(product_names) + "."