import falcon
from playhouse.shortcuts import model_to_dict
from cart_api.database import DatabaseProducts


class Product:
    def on_get(self, req, resp, product_id): 
        product = DatabaseProducts.get(id=product_id)
        resp.media = model_to_dict(product) 
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp, product_id):
        DatabaseProducts.delete_by_id(product_id)
        resp.status = falcon.HTTP_204


# Excercise 2:
# Products route should respond to GET and POST requests
# GET products returns a list of every product in the database
# POST products creates a product and returns the data it created

    


class Products:
    # pass  # must have a pass line because you cannot have a "blank" class
    
    def on_get(self, req, resp):
        products = DatabaseProducts.select()
        resp.media = []
        for product in products:
            product_dict = model_to_dict(product)
            resp.media.append(product_dict)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        product = DatabaseProducts.create(**req.media)
        product_data = model_to_dict(product)

        if "quantity" in product_data:
            del product_data["quantity"]

        resp.media = product_data
        resp.status = falcon.HTTP_201
