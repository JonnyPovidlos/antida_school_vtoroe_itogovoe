class AdsService:
	def __init__(self, connection):
		self.connection = connection

	def create_car(self, car):
		make = car['make']
		model = car['model']
		mileage = car['mileage']
		num_owners = car['num_owners']
		reg_number = car['reg_number']
		cur = self.connection.execute(
			f'INSERT INTO car (make, model, mileage, num_owners, reg_number) '
			f'VALUES '
			f'("{make}", "{model}", "{mileage}", "{num_owners}", "{reg_number}")'
		)
		car_id = cur.lastrowid
		return car_id

	def add_images(self, images, car_id):
		for image in images:
			keys = image.keys()
			insert_str = ', '.join(f'{key}' for key in keys)
			values = ', '.join(f'"{image[key]}"' for key in keys)

			self.connection.execute(
				f'INSERT INTO image ({insert_str}, car_id)'
				f'VALUES ({values}, {car_id})'
			)

	def add_tag(self, tags):
		for tag in tags:
			self.connection.execute(
				f'INSERT OR IGNORE INTO tag (name)'
				f'VALUES ("{tag}")'
			)

	def get_tags(self, tags):
		tags_id = []
		for tag in tags:
			cur = self.connection.execute(
				f'SELECT id '
				f'FROM tag '
				f'WHERE name = "{tag}"'
			)
			tags_id.append(dict(cur.fetchone())['id'])
		return tags_id

	def set_car_color(self, colors_id, car_id):
		for color_id in colors_id:
			self.connection.execute(
				f'INSERT INTO carcolor (color_id, car_id) '
				f'VALUES ({color_id}, {car_id})'
			)

	def create_ad(self, title, date, account_id, car_id):
		cur = self.connection.execute(
			f'INSERT INTO ad (title, date, seller_id, car_id) '
			f'VALUES ("{title}", "{date}", {account_id}, {car_id})'
		)
		ad_id = cur.lastrowid
		return ad_id

	def set_ad_tag(self, ad_id, tags_id):
		for tag_id in tags_id:
			self.connection.execute(
				f'INSERT INTO adtag (tag_id, ad_id) '
				f'VALUES ({tag_id}, {ad_id})'
			)

	def get_ad(self, ad_id):
		pass


