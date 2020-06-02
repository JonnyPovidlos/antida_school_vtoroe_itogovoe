class ColorsService:
	def __init__(self, connection):
		self.connection = connection

	def add_color(self, name, hex):
		self.connection.execute(
			f'INSERT INTO color (name, hex) '
			f'VALUES ("{name}", "{hex}")'
		)

	def get_color(self, name=None, id=None):
		query = f'SELECT * ' \
				f'FROM color '
		if name:
			query += f'WHERE name LIKE "{name}"'
		if id:
			query += f'WHERE id = {id}'
		cur = self.connection.execute(query)
		return [dict(row) for row in cur]

