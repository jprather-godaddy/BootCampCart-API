import falcon
from playhouse.shortcuts import model_to_dict
from cart_api.database import DatabaseCartItem, DatabaseProducts


# Exercise 3:
# Using the database model you created in Exercise 1 create a cartitems route
# CartItems should have a responder for POST and GET
# CartItem should have responders for GET DELETE PATCH
# Your API response statuses and bodies should conform to your OpenAPI spec

#Fetch a Cart Item row based on the given item_id
#Delete a Cart Item row based on the given item_id
#Update a Cart Item row based on the given item_id

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
        query = DatabaseCartItem.update(**cart_item_data).where(DatabaseCartItem.id == cart_item_id)
        query.execute()
        resp.status = falcon.HTTP_204
