import falcon
from playhouse.shortcuts import model_to_dict
from cart_api.database import DatabaseCartItem

# from cart_api.database import DatabaseCartItem


# Exercise 3:
# Using the database model you created in Exercise 1 create a cartitems route
# CartItems should have a responder for POST and GET
# CartItem should have responders for GET DELETE PATCH
# Your API response statuses and bodies should conform to your OpenAPI spec

#Fetch a Cart Item row based on the given item_id
#Delete a Cart Item row based on the given item_id
#Update a Cart Item row based on the given item_id

class CartItems:
    def on_post(self, req, resp):
        new_cartitem = req.get_media()
        new_model = DatabaseCartItem(
            name=new_cartitem["name"],
            price=new_cartitem["price"],
            quantity=new_cartitem["quantity"],
        )
        new_model.save()
        resp.media = model_to_dict(new_model)
        resp.status = falcon.HTTP_201

    def on_get(self, req, resp):
        resp.media = []
        cartitems = DatabaseCartItem.select()
        for cartitem in cartitems:
            resp.media.append(model_to_dict(cartitem))
        resp.status = falcon.HTTP_200


class CartItem:
    def on_get(self, req, resp, cartitem_id):
        cartitem = DatabaseCartItem.get(id=cartitem_id)
        resp.media = model_to_dict(cartitem)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, cartitem_id):
        DatabaseCartItem.delete_by_id(cartitem_id)
        resp.status = falcon.HTTP_204

    def on_patch(self, req, resp, cartitem_id):
        cartitem = DatabaseCartItem.get(id=cartitem_id)
        changes = req.media
        if "quantity" in changes:
            cartitem.quantity = changes["quantity"]
            cartitem.save()
        resp.status = falcon.HTTP_204