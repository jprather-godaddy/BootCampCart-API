import falcon
import random
from playhouse.shortcuts import model_to_dict
from cart_api.database import DatabasePromoCode


class PromoCodes:
    def on_get(self, req, resp):
        """Get all active promo codes"""
        promo_codes = DatabasePromoCode.select().where(DatabasePromoCode.is_active == True)
        resp.media = [model_to_dict(code) for code in promo_codes]
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        """Create a new promo code"""
        data = req.media
        promo_code = DatabasePromoCode.create(**data)
        resp.media = model_to_dict(promo_code)
        resp.status = falcon.HTTP_201


class PromoCode:
    def on_get(self, req, resp, code):
        """Validate and get a promo code by code string"""
        try:
            promo_code = DatabasePromoCode.get(
                DatabasePromoCode.code == code.upper(),
                DatabasePromoCode.is_active == True
            )
            resp.media = model_to_dict(promo_code)
            resp.status = falcon.HTTP_200
        except DatabasePromoCode.DoesNotExist:
            resp.media = {"error": "Promo code not found or inactive"}
            resp.status = falcon.HTTP_404


class RandomPromoCode:
    def on_get(self, req, resp):
        """Generate a random promo code for fun"""
        discount_options = [5, 10, 15, 20, 25]
        discount = random.choice(discount_options)

        code_prefixes = ["LUCKY", "DEAL", "SAVE", "BONUS", "EXTRA"]
        random_code = f"{random.choice(code_prefixes)}{discount}"

        # Check if this code already exists
        existing = DatabasePromoCode.select().where(DatabasePromoCode.code == random_code).first()

        if not existing:
            promo_code = DatabasePromoCode.create(
                code=random_code,
                discount_percent=float(discount),
                is_active=True,
                description=f"Random {discount}% discount - Lucky you!"
            )
        else:
            promo_code = existing

        resp.media = model_to_dict(promo_code)
        resp.status = falcon.HTTP_200


class ApplyPromoCode:
    def on_post(self, req, resp):
        """Apply a promo code to calculate total with discount"""
        data = req.media
        promo_code_str = data.get("code", "").upper()
        cart_total = data.get("cart_total", 0)

        try:
            promo_code = DatabasePromoCode.get(
                DatabasePromoCode.code == promo_code_str,
                DatabasePromoCode.is_active == True
            )

            discount_amount = (cart_total * promo_code.discount_percent) / 100
            final_total = cart_total - discount_amount

            resp.media = {
                "promo_code": model_to_dict(promo_code),
                "original_total": cart_total,
                "discount_amount": round(discount_amount, 2),
                "final_total": round(final_total, 2)
            }
            resp.status = falcon.HTTP_200
        except DatabasePromoCode.DoesNotExist:
            resp.media = {"error": "Invalid or inactive promo code"}
            resp.status = falcon.HTTP_404
