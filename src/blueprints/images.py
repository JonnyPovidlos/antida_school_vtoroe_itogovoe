from flask import (
	Blueprint,
	request,
	session,
	url_for,
	send_from_directory
)
from flask.views import MethodView
import os
from services.users import UserService
from database import db

bp = Blueprint('images', __name__)


class ImagesView(MethodView):
	def __init__(self):
		target_path = os.path.join(os.getcwd(), 'upload/')
		if not os.path.exists(target_path):
			os.makedirs(target_path)
		self.UPLOAD_FOLDER = target_path

	def post(self):
		account_id = session.get('user_id')
		if not account_id:
			return '', 401

		with db.connection as con:
			is_seller = UserService(con).account_is_seller(account_id)
			if not is_seller:
				return '', 403
			file = request.files.get('')
			count = len(os.listdir(self.UPLOAD_FOLDER))
			filename = f'image{count + 1}'

			file.save(os.path.join(self.UPLOAD_FOLDER, filename))
			result = {'url': url_for('images.image', image_name=filename)}
		return result, 200


class ImageView(MethodView):
	def __init__(self):
		target_path = os.path.join(os.getcwd(), 'upload/')
		if not os.path.exists(target_path):
			os.makedirs(target_path)
		self.UPLOAD_FOLDER = target_path

	def get(self, image_name):
		target_file = os.path.join(self.UPLOAD_FOLDER, image_name)
		if not os.path.exists(target_file):
			return '', 404
		return send_from_directory(self.UPLOAD_FOLDER, image_name, mimetype='image/gif'), 200




bp.add_url_rule('/', view_func=ImagesView.as_view('images'))
bp.add_url_rule('/<image_name>', view_func=ImageView.as_view('image'))
