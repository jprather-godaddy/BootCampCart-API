import falcon
from cart_api.database import DatabaseWishlistItem


class WishlistItems:
    def on_get(self, req, resp):
        wishlist_items = DatabaseWishlistItem.select()

        resp.media = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "name": item.name,
                "description": item.description,
                "image_url": item.image_url,
                "price": item.price,
                "is_on_sale": item.is_on_sale,
                "sale_price": item.sale_price,
            }
            for item in wishlist_items
        ]

        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        data = req.media

        wishlist_item = DatabaseWishlistItem(
            product_id=data.get("product_id"),
            name=data.get("name"),
            description=data.get("description"),
            image_url=data.get("image_url"),
            price=data.get("price"),
            is_on_sale=data.get("is_on_sale", False),
            sale_price=data.get("sale_price"),
        )

        wishlist_item.save()

        resp.media = {
            "id": wishlist_item.id,
            "product_id": wishlist_item.product_id,
            "name": wishlist_item.name,
            "description": wishlist_item.description,
            "image_url": wishlist_item.image_url,
            "price": wishlist_item.price,
            "is_on_sale": wishlist_item.is_on_sale,
            "sale_price": wishlist_item.sale_price,
        }

        resp.status = falcon.HTTP_201


class WishlistItem:
    def on_delete(self, req, resp, wishlist_item_id):
        DatabaseWishlistItem.delete_by_id(wishlist_item_id)

        resp.status = falcon.HTTP_204