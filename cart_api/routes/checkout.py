import falcon
from datetime import datetime
from cart_api.database import DatabaseOrder, DatabaseCartItem


class Checkout:
    def on_post(self, req, resp):
        data = req.media

        order = DatabaseOrder.create(
            name=data.get('name'),
            email=data.get('email'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            total_price=data.get('total_price'),
            created_at=datetime.utcnow(),
        )

        DatabaseCartItem.delete().execute()

        resp.media = {
            'id': order.id,
            'name': order.name,
            'email': order.email,
            'address': order.address,
            'city': order.city,
            'state': order.state,
            'zip_code': order.zip_code,
            'total_price': order.total_price,
            'created_at': str(order.created_at),
        }
        resp.status = falcon.HTTP_201


class Order:
    def on_get(self, req, resp, order_id):
        try:
            order = DatabaseOrder.get_by_id(order_id)
        except DatabaseOrder.DoesNotExist:
            resp.status = falcon.HTTP_404
            resp.media = {'error': 'Order not found'}
            return

        resp.media = {
            'id': order.id,
            'name': order.name,
            'email': order.email,
            'address': order.address,
            'city': order.city,
            'state': order.state,
            'zip_code': order.zip_code,
            'total_price': order.total_price,
            'created_at': str(order.created_at),
        }
        resp.status = falcon.HTTP_200
