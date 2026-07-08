import falcon
from playhouse.shortcuts import model_to_dict
from cart_api.database import DatabaseCoupon


class Coupon:
    def on_get(self, req, resp, code):
        coupon = DatabaseCoupon.get_or_none(code=code, active=True)
        if coupon is None:
            raise falcon.HTTPNotFound(title="Coupon not found")

        resp.media = model_to_dict(coupon)
        resp.status = falcon.HTTP_200


class Coupons:
    def on_get(self, req, resp):
        coupons = DatabaseCoupon.select().where(DatabaseCoupon.active == True)
        resp.media = [model_to_dict(coupon) for coupon in coupons]
        resp.status = falcon.HTTP_200
