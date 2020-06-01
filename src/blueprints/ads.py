from flask import (
	Blueprint,
	jsonify,
	request,
	session,
)
import datetime
from flask.views import MethodView
from database import db
from services.users import UserService

bp = Blueprint('ads', __name__)


class AdsView(MethodView):
	def get(self, user_id=None):
		request_params = request.args
		request_tags = request_params.get('tags', None)
		request_make = request_params.get('make', None)
		request_model = request_params.get('model', None)
		request_seller_id = request_params.get('seller_id', None)
		response = []
		if request_tags:
			request_tags = request_tags.split(',')
		if request_make:
			request_make = request_make.split(',')
		if request_model:
			request_model = request_make.split(',')
		if request_seller_id:
			request_seller_id = int(request_seller_id)


		with db.connection as con:
			query = f'SELECT * ' \
			        f'FROM ad '
			if user_id is None:
				if request_seller_id:
					seller_id = request_seller_id
					query += f'WHERE seller_id = {seller_id}'
			else:
				seller_id = user_id
				query += f'WHERE seller_id = {seller_id}'
			cur = con.execute(query)
			ads = [dict(row) for row in cur.fetchall()]
			for ad in ads:
				ad_id = ad['id']
				cur = con.execute(
					f'SELECT tag_id '
					f'FROM adtag '
					f'WHERE ad_id = {ad_id}'
				)
				tags_id = [dict(row)['tag_id'] for row in cur.fetchall()]

				tags = []
				for tag_id in tags_id:
					cur = con.execute(
						f'SELECT name '
						f'FROM tag '
						f'WHERE id = {tag_id}'
					)
					tags.append(dict(cur.fetchone())['name'])

				ad.update({'tags': tags})
				car_id = ad.pop('car_id')
				cur = con.execute(
					f'SELECT make, model, mileage, num_owners, reg_number '
					f'FROM car '
					f'WHERE id = {car_id}'
				)
				car = dict(cur.fetchone())
				cur = con.execute(
					f'SELECT color_id '
					f'FROM carcolor '
					f'WHERE car_id = {car_id}'
				)
				colors_id = [dict(row)['color_id'] for row in cur.fetchall()]
				colors = []
				for color_id in colors_id:
					cur = con.execute(
						f'SELECT * '
						f'FROM color '
						f'WHERE id = {color_id} '
					)
					colors.append(dict(cur.fetchone()))
				car['colors'] = colors

				ad.update({'car': car})
				tags_eq = True
				make_eq = True
				model_eq = True

				if request_tags:
					if set(ad['tags']) != set(request_tags):
						tags_eq = False
				if request_make:
					if set(request_make) != {car['make']}:
						make_eq = False
				if request_model:
					if set(request_model) != {car['model']}:
						model_eq = False
				if tags_eq and make_eq and model_eq:
					response.append(ad)
			return jsonify(response), 200

	def post(self, user_id=None):
		if not session.get('user_id', None):
			return '', 403
		if user_id is not None and user_id != session['user_id']:
			return '', 403
		account_id = session['user_id']

		with db.connection as con:
			service = UserService(con)
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
			response.update({'title': title, 'tags': tags, 'seller_id': account_id, 'is_seller': is_seller})
			cur = con.execute(
				f'INSERT INTO car (make, model, mileage, num_owners, reg_number) '
				f'VALUES '
				f'("{car["make"]}", "{car["model"]}", "{car["mileage"]}", "{car["num_owners"]}", "{car["reg_number"]}")'
			)
			car_id = cur.lastrowid
			for image in images:
				con.execute(
					f'INSERT INTO image (title, url, car_id)'
					f'VALUES ("{image["title"]}", "{image["url"]}", {car_id})'
				)

			car['images'] = images
			date = datetime.datetime.now().strftime('%Y-%m-%d')
			response.update({'date': date})
			tags_id = []
			print(car_id)
			for tag in tags:
				con.execute(
					f'INSERT OR IGNORE INTO tag (name)'
					f'VALUES ("{tag}")'
				)
				cur = con.execute(
					f'SELECT id '
					f'FROM tag '
					f'WHERE name = "{tag}"'
				)
				tags_id.append(dict(cur.fetchone())['id'])
			colors = []
			for color_id in colors_id:
				con.execute(
					f'INSERT INTO carcolor (color_id, car_id) '
					f'VALUES ({color_id}, {car_id})'
				)
				cur = con.execute(
					f'SELECT * '
					f'FROM color '
					f'WHERE id = {color_id}'
				)
				colors.append(dict(cur.fetchone()))
			car['colors'] = colors
			response.update({'car': car})
			cur = con.execute(
				f'INSERT INTO ad (title, date, seller_id, car_id) '
				f'VALUES ("{title}", "{date}", {account_id}, {car_id})'
			)
			ad_id = cur.lastrowid
			for tag_id in tags_id:
				con.execute(
					f'INSERT INTO adtag (tag_id, ad_id) '
					f'VALUES ({tag_id}, {ad_id})'
				)
			return jsonify(response), 201


class AdView(MethodView):
	def get(self, ad_id):
		with db.connection as con:
			response = {'id': ad_id}
			cur = con.execute(
				f'SELECT date, title, seller_id, car_id '
				f'FROM ad '
				f'WHERE id = {ad_id}'
			)
			ad = cur.fetchone()
			if not ad:
				return '', 400
			response.update(dict(ad))
			cur = con.execute(
				f'SELECT tag_id '
				f'FROM adtag '
				f'WHERE ad_id = {ad_id}'
			)
			tags_id = [dict(row) for row in cur.fetchall()]
			tags = []
			for tag_id in tags_id:
				cur = con.execute(
					f'SELECT name '
					f'FROM tag '
					f'WHERE id = {tag_id["tag_id"]}'
				)
				tags.append(dict(cur.fetchone())['name'])
			response['tas'] = tags
			car_id = response.pop('car_id')
			cur = con.execute(
				f'SELECT make, model, mileage, num_owners, reg_number '
				f'FROM car '
				f'WHERE id = {car_id}'
			)
			car = dict(cur.fetchone())
			cur = con.execute(
				f'SELECT color_id '
				f'FROM carcolor '
				f'WHERE car_id = {car_id}'
			)
			colors_id = [dict(row) for row in cur.fetchall()]
			colors = []
			for color_id in colors_id:
				cur = con.execute(
					f'SELECT * '
					f'FROM color '
					f'WHERE id = {color_id["color_id"]}'
				)
				colors.append(dict(cur.fetchone()))
			car['colors'] = colors
			cur = con.execute(
				f'SELECT title, url '
				f'FROM image '
				f'WHERE car_id = {car_id}'
			)
			images = [dict(row) for row in cur.fetchall()]
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


bp.add_url_rule('/ads', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/users/<int:user_id>/ads', view_func=AdsView.as_view('user_id_ads'))
bp.add_url_rule('/ads/<int:ad_id>', view_func=AdView.as_view('ad'))