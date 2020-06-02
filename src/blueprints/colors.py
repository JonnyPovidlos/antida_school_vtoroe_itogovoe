from flask import (
	Blueprint,
	jsonify,
	request,
	session
)
from flask.views import MethodView
from database import db
from services.colors import ColorsService
from services.users import UsersService

bp = Blueprint('colors', __name__)


class ColorsView(MethodView):
	def get(self):
		with db.connection as con:
			service = ColorsService(con)
			colors = service.get_color()
			return jsonify(colors), 200

	def post(self):
		account_id = session.get('user_id')
		if not account_id:
			return '', 401

		request_json = request.json
		name = request_json['name']
		hex = request_json['hex']

		if not name or not hex:
			return '', 400
		with db.connection as con:
			user_service = UsersService(con)
			is_seller = user_service.account_is_seller(account_id)
			if not is_seller:
				return '', 403
			service = ColorsService(con)
			try:
				service.add_color(name, hex)
			except:
				color = service.get_color(name)
				return jsonify(color), 208
			color = service.get_color(name)
			return jsonify(color), 200


bp.add_url_rule('/', view_func=ColorsView.as_view('colors'))
