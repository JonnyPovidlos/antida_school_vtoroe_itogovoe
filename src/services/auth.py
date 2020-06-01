class AuthService:
	def __init__(self, connection):
		self.connection = connection

	def get_user(self, email):
		cur = self.connection.execute(
			f'SELECT id, email, password '
			f'FROM account '
			f'WHERE email LIKE "{email}"'
		)

		try:
			result = dict(cur.fetchone())
		except:
			result = None
		return result
