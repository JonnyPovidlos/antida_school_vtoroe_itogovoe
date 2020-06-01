from flask import (
	Blueprint,
	jsonify,
	request,
)
from flask.views import MethodView
from services.cities import CitiesService
from database import db

bp = Blueprint('cities', __name__)


class CitiesView(MethodView):
	def get(self):
		with db.connection as con:
			service = CitiesService(con)
			cities = service.get_cities()
			return jsonify(cities), 200

	def post(self):
		request_json = request.json
		name = request_json.get('name')
		if not name:
			return '', 401
		with db.connection as con:
			service = CitiesService(con)
			service.add_city(city_name=name)
			city = service.get_cities(city_name=name)
		return jsonify(city)


bp.add_url_rule('/', view_func=CitiesView.as_view('cities'))

