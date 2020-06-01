class CitiesService:
	def __init__(self, connection):
		self.connection = connection

	def get_cities(self, city_name=None):
		query = 'SELECT * ' \
		        'FROM city '
		if city_name:
			query += f'WHERE lower(name) LIKE lower("{city_name}")'
		cur = self.connection.execute(query)
		cities = cur.fetchall()
		return [dict(row) for row in cities]

	def add_city(self, city_name):
		query = f'INSERT OR IGNORE INTO city (name) ' \
		        f'VALUES ("{city_name}")'
		self.connection.execute(query)
		self.connection.commit()

