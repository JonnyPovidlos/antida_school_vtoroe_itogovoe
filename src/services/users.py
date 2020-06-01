from werkzeug.security import generate_password_hash


class UsersService:
	def __init__(self, connection):
		self.connection = connection

	def create_account(self, first_name, last_name, email, password):
		password_hash = generate_password_hash(password)
		try:
			self.connection.execute(
				f'INSERT INTO account (first_name, last_name, email, password)'
				f'VALUES ("{first_name}", "{last_name}", "{email}", "{password_hash}")'
			)
		except:
			return None
		cur = self.connection.execute(
			f'SELECT id '
			f'FROM account '
			f'WHERE email LIKE "{email}"'
		)
		account = dict(cur.fetchone())
		account_id = account['id']
		return account_id

	def create_seller(self, email, phone, zip_code, city_id, street, home):
		self.connection.execute(
			f'INSERT OR IGNORE INTO zipcode (zip_code, city_id) '
			f'VALUES ({zip_code}, {city_id})'
		)
		cur = self.connection.execute(
			f'SELECT id '
			f'FROM account '
			f'WHERE email LIKE "{email}"'
		)
		account = dict(cur.fetchone())
		account_id = account['id']
		self.connection.execute(
			f'INSERT INTO seller (zip_code, street, home, phone, account_id)'
			f'VALUES ({zip_code}, "{street}", "{home}", "{phone}", {account_id})'
		)
		return account_id

	def get_user(self, user_id, is_seller):
		cur = self.connection.execute(
			f'SELECT id, email, first_name, last_name '
			f'FROM account '
			f'WHERE id = {user_id}'
		)
		user = dict(cur.fetchone())
		if is_seller:
			cur = self.connection.execute(
				f'SELECT account_id, zip_code, street, home, phone '
				f'FROM seller '
				f'WHERE account_id = {user_id}'
			)
			user.update(dict(cur.fetchone()))
			cur = self.connection.execute(
				f'SELECT city_id '
				f'FROM zipcode '
				f'WHERE zip_code = {user["zip_code"]}'
			)
			user.update(dict(cur.fetchone()))
		return user


class UserService:
	def __init__(self, connection):
		self.connection = connection

	def get_account(self, account_id):
		cur = self.connection.execute(
				f'SELECT id, first_name, last_name, email '
				f'FROM account '
				f'WHERE id = {account_id}'
			)
		return dict(cur.fetchone())

	def get_seller(self, account_id):
		cur = self.connection.execute(
			f'SELECT zip_code, street, home, phone '
			f'FROM seller '
			f'WHERE account_id = {account_id}'
		)
		seller = dict(cur.fetchone())
		cur = self.connection.execute(
			f'SELECT city_id '
			f'FROM zipcode '
			f'WHERE zip_code = {seller["zip_code"]}'
		)
		seller.update(dict(cur.fetchone()))
		return seller

	def account_is_seller(self, account_id):
		cur = self.connection.execute(
			f'SELECT id '
			f'FROM seller '
			f'WHERE account_id = {account_id}'
		)
		row = cur.fetchone()
		if row:
			return True
		return False


