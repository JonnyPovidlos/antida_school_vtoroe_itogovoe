from flask import (
	Blueprint,
	jsonify,
	request,
	session,
)
from flask.views import MethodView
from services.users import (
	UsersService,
	UserService
)
from database import db

bp = Blueprint('users', __name__)


class UsersView(MethodView):
	def post(self):
		request_json = request.json
		email = request_json.get('email')
		password = request_json.get('password')
		first_name = request_json.get('first_name')
		last_name = request_json.get('last_name')
		is_seller = request_json.get('is_seller')
		if is_seller:
			phone = request_json.get('phone')
			zip_code = int(request_json.get('zip_code'))
			city_id = int(request_json.get('city_id'))
			street = request_json.get('street')
			home = request_json.get('home')
		with db.connection as con:
			service = UsersService(con)
			account_id = service.create_account(first_name, last_name, email, password)
			if not account_id:
				return f'Аккаунт с таким email уже создан'
			if is_seller:
				account_id = service.create_seller(email, phone, zip_code, city_id, street, home)
			response = service.get_user(account_id, is_seller)
			return jsonify(response)


class UserView(MethodView):
	def get(self, account_id):
		if not session.get('user_id', None):
			return '', 401
		with db.connection as con:
			service = UserService(con)
			account = service.get_account(account_id)
			is_seller = service.account_is_seller(account_id)
			if is_seller:
				seller = service.get_seller(account_id)
				account.update(seller)
			print(account)
		return jsonify(account), 200

	def patch(self, account_id):
		def update_data(data_dict, key, req_json):
			if req_json.get(key, None):
				data_dict.update({key: req_json[key]})
			return data_dict

		if not session.get('user_id', None):
			return '', 401

		if account_id != session['user_id']:
			return '', 403

		request_json = request.json
		with db.connection as con:
			service = UserService(con)

			account_update = dict()
			account_update = update_data(account_update, 'first_name', request_json)
			account_update = update_data(account_update, 'last_name', request_json)
			for key, value in account_update.items():
				con.execute(
					f'UPDATE account '
					f'SET {key} = "{value}" '
					f'WHERE id = {account_id} '
				)
			is_seller_update = request_json.get('is_seller', None)
			if is_seller_update is not None:
				is_seller = service.account_is_seller(account_id)
				if is_seller_update:
					seller_update = dict()
					zipcode_update = dict()
					seller_update.update(update_data(seller_update, 'phone', request_json))
					seller_update.update(update_data(seller_update, "zip_code", request_json))
					zipcode_update.update(update_data(zipcode_update, "zip_code", request_json))
					seller_update.update(update_data(seller_update, "street", request_json))
					zipcode_update.update(update_data(zipcode_update, "city_id", request_json))
					seller_update.update(update_data(seller_update, "home", request_json))
					if not is_seller:
						cur = con.execute(
							f'SELECT email '
							f'FROM account '
							f'WHERE id = {account_id} '
						)
						email = dict(cur.fetchone())['email']
						UsersService(con).create_seller(email=email,
						                                city_id=seller_update['city_id'],
						                                zip_code=zipcode_update['zip_code'],
						                                home=seller_update['home'],
						                                phone=seller_update['phone'],
						                                street=seller_update['street']
						                                )
						return jsonify(UsersService(con).get_user(account_id, is_seller_update)), 200
					else:
						con.execute(
							f'INSERT OR IGNORE INTO zipcode (zip_code, city_id) '
							f'VALUES ({zipcode_update["zip_code"]}, {zipcode_update["city_id"]})'
						)

						for key, value in seller_update.items():
							con.execute(
								f'UPDATE seller '
								f'SET {key} = "{value}" '
								f'WHERE account_id = {account_id}'
							)
						return jsonify(UsersService(con).get_user(account_id, is_seller_update)), 200
				else:
					if is_seller:
						with db.connection as con:
							cur = con.execute(
								f'SELECT * '
								f'FROM ad '
								f'WHERE seller_id = {account_id} '
							)
							ads = [dict(row) for row in cur.fetchall()]
							for ad in ads:
								car_id = ad['car_id']
								con.execute(
									f'DELETE FROM carcolor '
									f'WHERE car_id = {car_id}'
								)
								con.execute(
									f'DELETE FROM car '
									f'WHERE id = {car_id}'
								)
								con.execute(
									f'DELETE FROM image '
									f'WHERE car_id = {car_id}'
								)
								con.execute(
									f'DELETE FROM ad '
									f'WHERE seller_id = {account_id} '
								)
								con.execute(
									f'DELETE FROM seller '
									f'WHERE account_id = {account_id}'
								)
					return jsonify(UsersService(con).get_user(account_id, is_seller_update)), 200


bp.add_url_rule('/', view_func=UsersView.as_view('users'))
bp.add_url_rule('/<int:account_id>', view_func=UserView.as_view('user'))
