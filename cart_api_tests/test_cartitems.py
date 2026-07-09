from .test_heartbeat import TestClient
from .test_exercises import EXAMPLE_CART_ITEM

CARTITEMS_PATH = "/v1/cartitems"
CARTITEM_PATH = "/v1/cartitems/{item_id}"
PRODUCTS_PATH = "/v1/products"
PRODUCT_PATH = "/v1/products/{product_id}"


class Exercise3(TestClient):
    def test_get_items(self):
        response = self.simulate_get(CARTITEMS_PATH)
        self.assertEqual(response.status_code, 200)
        body = response.json
        self.assertIsInstance(body, list)

    def test_get_item(self):
        body = EXAMPLE_CART_ITEM
        response = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(response.status_code, 201, "Requires working POST")
        self.aitem = response.json

        response = self.simulate_get(CARTITEM_PATH.format(item_id=self.aitem["id"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], self.aitem["name"])

        self.simulate_delete(CARTITEM_PATH.format(item_id=self.aitem["id"]))

    def test_post_cartitems(self):
        body = EXAMPLE_CART_ITEM

        response = self.simulate_post(CARTITEMS_PATH, json=body)

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json)
        self.assertIsInstance(response.json, dict)

        generated_id = response.json["id"]
        self.assertIsInstance(generated_id, int)
        self.assertEqual(body["name"], response.json["name"])

        # Delete the new item
        item_uri = CARTITEM_PATH.format(item_id=generated_id)
        self.simulate_delete(item_uri)

    def test_delete_item(self):
        body = EXAMPLE_CART_ITEM
        response = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(response.status_code, 201, "Requires working POST")
        self.aitem = response.json

        response = self.simulate_delete(CARTITEM_PATH.format(item_id=self.aitem["id"]))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, "")

    def test_patch_item(self):
        body = EXAMPLE_CART_ITEM
        response = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(response.status_code, 201, "Requires working POST")
        self.aitem = response.json
        changes = {"quantity": 5}
        response = self.simulate_patch(
            CARTITEM_PATH.format(item_id=self.aitem["id"]),
            json=changes,
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, "")

        # Verify change
        response = self.simulate_get(CARTITEM_PATH.format(item_id=self.aitem["id"]))
        self.assertEqual(response.status_code, 200, "Requires working GET")
        self.assertEqual(response.json["quantity"], 5)

        self.simulate_delete(CARTITEM_PATH.format(item_id=self.aitem["id"]))


class CartItemValidationTests(TestClient):
    def setUp(self):
        super().setUp()
        resp = self.simulate_post(PRODUCTS_PATH, json={"name": "Test Stock Product", "price": 9.99, "quantity": 5})
        self.product = resp.json
        self.product_id = self.product["id"]

    def tearDown(self):
        super().tearDown()
        self.simulate_delete(PRODUCT_PATH.format(product_id=self.product_id))
        cart_resp = self.simulate_get(CARTITEMS_PATH)
        for item in cart_resp.json:
            if item.get("product_id") == self.product_id:
                self.simulate_delete(CARTITEM_PATH.format(item_id=item["id"]))

    def test_post_no_product_id_skips_validation(self):
        resp = self.simulate_post(CARTITEMS_PATH, json=dict(name="No PID Item", price=1.00, quantity=9999))
        self.assertEqual(resp.status_code, 201)
        self.simulate_delete(CARTITEM_PATH.format(item_id=resp.json["id"]))

    def test_post_within_stock(self):
        body = dict(name="In Stock Item", price=1.00, quantity=3, product_id=self.product_id)
        resp = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json["quantity"], 3)

    def test_post_exceeds_stock(self):
        body = dict(name="Over Stock Item", price=1.00, quantity=10, product_id=self.product_id)
        resp = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json["code"], "409_QUANTITY_EXCEEDED")

    def test_post_nonexistent_product_id(self):
        body = dict(name="Ghost Product Item", price=1.00, quantity=1, product_id=999999)
        resp = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json["code"], "404_PRODUCT_NOT_FOUND")

    def test_post_combines_duplicate(self):
        body = dict(name="Dup Item", price=1.00, quantity=2, product_id=self.product_id)
        resp1 = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(resp1.status_code, 201)

        resp2 = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(resp2.status_code, 201)

        cart_resp = self.simulate_get(CARTITEMS_PATH)
        matching = [i for i in cart_resp.json if i.get("product_id") == self.product_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["quantity"], 4)

    def test_post_combine_exceeds_stock(self):
        body = dict(name="Near Max Item", price=1.00, quantity=4, product_id=self.product_id)
        resp1 = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(resp1.status_code, 201)

        body2 = dict(name="Near Max Item", price=1.00, quantity=3, product_id=self.product_id)
        resp2 = self.simulate_post(CARTITEMS_PATH, json=body2)
        self.assertEqual(resp2.status_code, 409)
        self.assertEqual(resp2.json["code"], "409_QUANTITY_EXCEEDED")

    def test_patch_within_stock(self):
        body = dict(name="Patch Stock Item", price=1.00, quantity=1, product_id=self.product_id)
        post_resp = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(post_resp.status_code, 201)
        item_id = post_resp.json["id"]

        patch_resp = self.simulate_patch(CARTITEM_PATH.format(item_id=item_id), json={"quantity": 4})
        self.assertEqual(patch_resp.status_code, 204)

        get_resp = self.simulate_get(CARTITEM_PATH.format(item_id=item_id))
        self.assertEqual(get_resp.json["quantity"], 4)

    def test_patch_exceeds_stock(self):
        body = dict(name="Patch Over Stock Item", price=1.00, quantity=1, product_id=self.product_id)
        post_resp = self.simulate_post(CARTITEMS_PATH, json=body)
        self.assertEqual(post_resp.status_code, 201)
        item_id = post_resp.json["id"]

        patch_resp = self.simulate_patch(CARTITEM_PATH.format(item_id=item_id), json={"quantity": 10})
        self.assertEqual(patch_resp.status_code, 409)
        self.assertEqual(patch_resp.json["code"], "409_QUANTITY_EXCEEDED")

    def test_patch_no_product_id_skips_validation(self):
        post_resp = self.simulate_post(CARTITEMS_PATH, json=EXAMPLE_CART_ITEM)
        self.assertEqual(post_resp.status_code, 201)
        item_id = post_resp.json["id"]

        patch_resp = self.simulate_patch(CARTITEM_PATH.format(item_id=item_id), json={"quantity": 9999})
        self.assertEqual(patch_resp.status_code, 204)
        self.simulate_delete(CARTITEM_PATH.format(item_id=item_id))
