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
from services.colors import ColorsService

bp = Blueprint('ads', __name__)


class AdsView(MethodView):
	def get(self, user_id=None):
		with db.connection as con:
			qs = dict()
			service_ads = AdsService(con)
			ads = service_ads.get_ads(user_id)
			response = []
			for ad in ads:
				ad_id = ad['id']
				tags_id = service_ads.get_tags_id(ad_id=ad_id)
				tags = service_ads.get_tags(tags_id)
				ad.update({'tags': tags})
				car_id = ad.pop('car_id')
				car = service_ads.get_car(car_id)
				colors_id = service_ads.get_car_color(car_id)
				colors = []
				for color_id in colors_id:
					color = ColorsService(con).get_color(id=color_id)
					colors += color
				car['colors'] = colors
				ad.update({'car': car})

				tags_equals = True
				make_equals = True
				model_equals = True
				seller_equals = True
				if 'tags' in request.args:
					qs['tags'] = [tag.strip() for tag in request.args['tags'].split(',')]
					if set(tags) != set(qs['tags']):
						tags_equals = False
				if 'make' in request.args:
					qs['make'] = request.args['make'].strip()
					if car['make'] != qs['make']:
						make_equals = False
				if 'model' in request.args:
					qs['model'] = request.args['model'].strip()
					if car['model'] != qs['model']:
						model_equals = False
				if 'seller_id' in request.args:
					qs['seller_id'] = int(request.args['seller_id'])
					if ad['seller_id'] != qs['seller_id']:
						seller_equals = False
				print(ad)
				print(tags_equals, make_equals, model_equals, seller_equals)
				if tags_equals and make_equals and model_equals and seller_equals:
					response.append(ad)
			return jsonify(response), 200

	def post(self, user_id=None):
		if not session.get('user_id', None):
			return '', 403
		if user_id is not None and user_id != session['user_id']:
			return '', 403
		account_id = session['user_id']

		with db.connection as con:
			service = UsersService(con)
			service_ads = AdsService(con)
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
			car_id = service_ads.create_car(car)
			service_ads.add_images(images, car_id)

			date = datetime.datetime.now().strftime('%Y-%m-%d')
			response.update({'date': date})

			service_ads.add_tag(tags)
			tags_id = service_ads.get_tags_id(tags=tags)

			colors = []
			service_ads.set_car_color(colors_id, car_id)
			service_color = ColorsService(con)
			for color_id in colors_id:
				color = service_color.get_color(id=color_id)
				colors += color
			car['colors'] = colors

			response.update({'car': car})

			ad_id = service_ads.create_ad(
				title=title,
				date=date,
				account_id=account_id,
				car_id=car_id
			)
			response.update({'id': ad_id})
			service_ads.set_ad_tag(ad_id, tags_id)
			return jsonify(response), 201


class AdView(MethodView):
	def get(self, ad_id):
		with db.connection as con:

			response = {'id': ad_id}
			service = AdsService(con)
			ad = service.get_ad(ad_id)
			if ad is None:
				return '', 404
			response.update(ad)

			tags_id = service.get_tags_id(ad_id=ad_id)
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
			return f'', 200

	def patch(self, ad_id):
		if not session.get('user_id', None):
			return '', 401

		def update_data(data_dict, key, req_json):
			if req_json.get(key):
				data_dict.update({key: req_json[key]})
			return data_dict


		request_json = request.json
		title = request_json.get('title')
		tags = request_json.get('tags')
		car = request_json.get('car')
		with db.connection as con:
			service = AdsService(con)
			ad = service.get_ad(ad_id)
			if ad:
				if ad['seller_id'] != session['user_id']:
					return '', 403
			else:
				return '', 404

			if title:
				service.update_title(ad_id, title)
			if tags:
				service.add_tag(tags)
				tags_id = service.get_tags_id(tags=tags)
				service.delete_ad_tags(ad_id)
				service.set_ad_tag(ad_id, tags_id)
			if car:
				car_update = dict()
				colors_update = dict()
				images_update = dict()
				update_data(car_update, 'make', car)
				update_data(car_update, 'model', car)
				update_data(colors_update, 'colors', car)
				update_data(car_update, 'mileage', car)
				update_data(car_update, 'num_owners', car)
				update_data(car_update, 'reg_number', car)
				update_data(images_update, 'images', car)
				car_id = ad['car_id']
				if len(car_update):
					service.update_car(car_id, car_update)
				if len(colors_update):
					colors_id = colors_update['colors']
					service.delete_car_color(car_id)
					service.set_car_color(colors_id, car_id)
				if len(images_update):
					images_update = images_update['images']
					service.delete_images(car_id)
					service.add_images(images_update, car_id)

		return '', 200


bp.add_url_rule('/ads', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/users/<int:user_id>/ads', view_func=AdsView.as_view('user_id_ads'))
bp.add_url_rule('/ads/<int:ad_id>', view_func=AdView.as_view('ad'))