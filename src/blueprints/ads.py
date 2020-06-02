from flask import (
	Blueprint,
	jsonify,
	request,
	session,
)
import datetime
from flask.views import MethodView
from database import db
from services.users import UsersService
from services.ads import AdsService
from services.ads import AdService
from services.colors import ColorsService

bp = Blueprint('ads', __name__)


class AdsView(MethodView):
	def get(self, user_id=None):
		with db.connection as con:
			service_ads = AdsService(con)
			service_ad = AdService(con)
			ads = service_ads.get_ads(user_id)

			for ad in ads:
				ad_id = ad['id']
				tags_id = service_ads.get_tags_id(ad_id=ad_id)

				tags = service_ad.get_tags(tags_id)

				ad.update({'tags': tags})

				car_id = ad.pop('car_id')
				car = service_ad.get_car(car_id)
				# cur = con.execute(
				# 	f'SELECT make, model, mileage, num_owners, reg_number '
				# 	f'FROM car '
				# 	f'WHERE id = {car_id}'
				# )
				# car = dict(cur.fetchone())
				# cur = con.execute(
				# 	f'SELECT color_id '
				# 	f'FROM carcolor '
				# 	f'WHERE car_id = {car_id}'
				# )
				# colors_id = [dict(row)['color_id'] for row in cur.fetchall()]
				colors_id = service_ad.get_car_color(car_id)
				colors = []
				for color_id in colors_id:
					color = ColorsService(con).get_color(id=color_id)
					colors += color
				# for color_id in colors_id:
				# 	cur = con.execute(
				# 		f'SELECT * '
				# 		f'FROM color '
				# 		f'WHERE id = {color_id} '
				# 	)
				# 	colors.append(dict(cur.fetchone()))
				car['colors'] = colors

				ad.update({'car': car})
			return jsonify(ads), 200

	def post(self, user_id=None):
		if not session.get('user_id', None):
			return '', 403
		if user_id is not None and user_id != session['user_id']:
			return '', 403
		account_id = session['user_id']

		with db.connection as con:
			service = UsersService(con)
			service_ad = AdsService(con)
			is_seller = service.account_is_seller(account_id)
			if not is_seller:
				return '', 403
			request_json = request.json
			response = dict()
			title = request_json['title']
			tags = request_json['tags']
			car = request_json['car']
			colors_id = car['colors']
			images = car['images']
			car.setdefault('num_owners', 1)

			response.update(
				{
					'title': title,
					'tags': tags,
					'seller_id': account_id,
					'is_seller': is_seller
				}
			)
			car_id = service_ad.create_car(car)
			service_ad.add_images(images, car_id)

			date = datetime.datetime.now().strftime('%Y-%m-%d')
			response.update({'date': date})

			service_ad.add_tag(tags)
			tags_id = service_ad.get_tags_id(tags=tags)

			colors = []
			service_ad.set_car_color(colors_id, car_id)
			service_color = ColorsService(con)
			for color_id in colors_id:
				color = service_color.get_color(id=color_id)
				colors += (color)
			car['colors'] = colors

			response.update({'car': car})

			ad_id = service_ad.create_ad(
				title=title,
				date=date,
				account_id=account_id,
				car_id=car_id
			)
			response.update({'id': ad_id})
			service_ad.set_ad_tag(ad_id, tags_id)
			return jsonify(response), 201


class AdView(MethodView):
	def get(self, ad_id):
		with db.connection as con:

			response = {'id': ad_id}
			service = AdService(con)
			ad = service.get_ad(ad_id)
			if ad is None:
				return '', 404
			response.update(ad)

			tags_id = AdsService(con).get_tags_id(ad_id=ad_id)
			tags = service.get_tags(tags_id)
			response['tags'] = tags

			car_id = response.pop('car_id')
			car = service.get_car(car_id)

			colors_id = service.get_car_color(car_id)
			colors = []
			for color_id in colors_id:
				color = ColorsService(con).get_color(id=color_id)
				colors += color
			car['colors'] = colors

			images = service.get_images(car_id)
			car['images'] = images
			response['car'] = car
			return jsonify(response), 200

	def delete(self, ad_id):
		if not session.get('user_id', None):
			return '', 401

		with db.connection as con:
			cur = con.execute(
				f'SELECT seller_id, title, date, car_id '
				f'FROM ad '
				f'WHERE id = {ad_id} '
			)
			ad = cur.fetchone()
			if not ad:
				return '', 404
			ad = dict(ad)
			seller_id = ad['seller_id']
			car_id = ad['car_id']
			if seller_id != session['user_id']:
				return '', 403
			con.execute(
				f'DELETE FROM image '
				f'WHERE car_id = {car_id}'
			)
			con.execute(
				f'DELETE FROM carcolor '
				f'WHERE car_id = {car_id}'
			)
			con.execute(
				f'DELETE FROM car '
				f'WHERE id = {car_id}'
			)
			con.execute(
				f'DELETE FROM ad '
				f'WHERE id = {ad_id}'
			)
			return f'', 204

	def patch(self, ad_id):
		request_json = request.json
		title = request_json.get('title')
		tags = request_json.get('tags')
		car = request_json.get('car')
		with db.connection as con:
			if title:
				con.execute(
					f'UPDATE ad'
					f'SET title = "{title}"'
					f'WHERE id = {ad_id}'
				)
		return '', 200


bp.add_url_rule('/ads', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/users/<int:user_id>/ads', view_func=AdsView.as_view('user_id_ads'))
bp.add_url_rule('/ads/<int:ad_id>', view_func=AdView.as_view('ad'))