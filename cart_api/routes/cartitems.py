import falcon
from playhouse.shortcuts import model_to_dict
from cart_api.database import DatabaseCartItem, DatabaseProducts


def _get_product(product_id):
    try:
        return DatabaseProducts.get(id=product_id)
    except DatabaseProducts.DoesNotExist:
        return None


class CartItems:
    def on_get(self, req, resp):
        cartItems = DatabaseCartItem.select()
        resp.media = []
        for cartItem in cartItems:
            cartItem_dict = model_to_dict(cartItem)
            resp.media.append(cartItem_dict)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        cart_item_data = req.media
        product_id = cart_item_data.get("product_id")

        if product_id is not None:
            product = _get_product(product_id)
            if product is None:
                resp.status = falcon.HTTP_404
                resp.media = {"code": "404_PRODUCT_NOT_FOUND",
                              "message": f"Product with id {product_id} was not found."}
                return

            requested_qty = cart_item_data.get("quantity", 1)
            existing = DatabaseCartItem.get_or_none(product_id=product_id)

            if existing is not None:
                combined = existing.quantity + requested_qty
                if combined > product.quantity:
                    resp.status = falcon.HTTP_409
                    resp.media = {"code": "409_QUANTITY_EXCEEDED",
                                  "message": (f"Cannot add {requested_qty} of '{product.name}' to cart. "
                                              f"Cart already has {existing.quantity}; "
                                              f"only {product.quantity} in stock.")}
                    return
                DatabaseCartItem.update(quantity=combined).where(DatabaseCartItem.id == existing.id).execute()
                resp.media = model_to_dict(DatabaseCartItem.get(id=existing.id))
                resp.status = falcon.HTTP_201
                return
            else:
                if requested_qty > product.quantity:
                    resp.status = falcon.HTTP_409
                    resp.media = {"code": "409_QUANTITY_EXCEEDED",
                                  "message": (f"Cannot add {requested_qty} of '{product.name}' to cart. "
                                              f"Only {product.quantity} in stock.")}
                    return

        new_cart_item = DatabaseCartItem.create(**cart_item_data)
        resp.media = model_to_dict(new_cart_item)
        resp.status = falcon.HTTP_201


class CartItem:
    def on_get(self, req, resp, cart_item_id):
        cart_item = DatabaseCartItem.get(id=cart_item_id)
        resp.media = model_to_dict(cart_item)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, cart_item_id):
        DatabaseCartItem.delete_by_id(cart_item_id)
        resp.status = falcon.HTTP_204

    def on_patch(self, req, resp, cart_item_id):
        cart_item_data = req.media
        new_qty = cart_item_data.get("quantity")

        if new_qty is not None:
            cart_item = DatabaseCartItem.get_or_none(id=cart_item_id)
            if cart_item is None:
                resp.status = falcon.HTTP_404
                resp.media = {"code": "404_CART_ITEM_NOT_FOUND",
                              "message": f"Cart item with id {cart_item_id} was not found."}
                return

            if cart_item.product_id is not None:
                product = _get_product(cart_item.product_id)
                if product is None:
                    resp.status = falcon.HTTP_404
                    resp.media = {"code": "404_PRODUCT_NOT_FOUND",
                                  "message": f"Product with id {cart_item.product_id} was not found."}
                    return
                if new_qty > product.quantity:
                    resp.status = falcon.HTTP_409
                    resp.media = {"code": "409_QUANTITY_EXCEEDED",
                                  "message": (f"Cannot set quantity to {new_qty} for '{product.name}'. "
                                              f"Only {product.quantity} in stock.")}
                    return

        DatabaseCartItem.update(**cart_item_data).where(DatabaseCartItem.id == cart_item_id).execute()
        resp.status = falcon.HTTP_204
