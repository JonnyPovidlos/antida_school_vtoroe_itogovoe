from flask import (
	session,
	request,
	Blueprint,
)
from werkzeug.security import check_password_hash
from services.auth import AuthService
from database import db

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
	request_json = request.json
	email = request_json.get('email')
	password = request_json.get('password')
	if not email or not password:
		return '', 404

	with db.connection as con:
		service = AuthService(con)
		user = service.get_user(email)
		if not user:
			return '', 403
		if not check_password_hash(user['password'], password):
			return '', 403
		session['user_id'] = user['id']
		return '', 200


@bp.route('/logout', methods=['POST'])
def logout():
	session.pop('user_id', None)
	return '', 200
