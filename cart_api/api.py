import falcon
from swagger_ui import falcon_api_doc
from cart_api.routes.heartbeat import Heartbeat
from cart_api.routes.products import Product, Products
from cart_api.routes.cartitems import CartItem, CartItems
from cart_api.routes.chatbot import Chatbot
from cart_api.routes.promocodes import PromoCodes, PromoCode, RandomPromoCode, ApplyPromoCode

# Instantiate RESTful API and resources
api = falcon.App(cors_enable=True)
api.req_options.strip_url_path_trailing_slash = True
hb = Heartbeat()
product = Product()
products = Products()
cartItem = CartItem()
cartItems = CartItems()
chatbot = Chatbot()
promo_codes = PromoCodes()
promo_code = PromoCode()
random_promo = RandomPromoCode()
apply_promo = ApplyPromoCode()

# Define our API's routes
api.add_route("/heartbeat", hb)
api.add_route("/v1/products/{product_id:int}", product)
api.add_route("/v1/products", products)
api.add_route("/v1/cartitems/{cart_item_id:int}", cartItem)
api.add_route("/v1/cartitems", cartItems)
api.add_route("/v1/chatbot", chatbot)
api.add_route("/v1/promocodes", promo_codes)
api.add_route("/v1/promocodes/random", random_promo)
api.add_route("/v1/promocodes/apply", apply_promo)
api.add_route("/v1/promocodes/{code}", promo_code)

# Add a route which serves our OpenAPI specification
falcon_api_doc(
    api, config_path="/swagger/api.json", url_prefix="/", title="Cart API", editor=True
)


# Add custom error handling
def http405(req, resp, error, params):
    """Intercept any 405 type errors and return json"""
    resp.status = falcon.HTTP_405
    resp.media = {
        "code": "405_METHOD_NOT_ALLOWED",
        "message": "Cannot perform " + req.method + " on " + req.url,
    }


api.add_error_handler(falcon.HTTPMethodNotAllowed, http405)
