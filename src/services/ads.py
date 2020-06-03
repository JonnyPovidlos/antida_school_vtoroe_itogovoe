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
			self.connection.commit()

	def get_tags_id(self, tags=None, ad_id=None):
		tags_id = []
		if tags is not None:
			for tag in tags:
				cur = self.connection.execute(
					f'SELECT id '
					f'FROM tag '
					f'WHERE name = "{tag}"'
				)
				tags_id.append(dict(cur.fetchone())['id'])
		if ad_id is not None:
			cur = self.connection.execute(
				f'SELECT tag_id '
				f'FROM adtag '
				f'WHERE ad_id = {ad_id}'
			)
			tags_id = [dict(row)['tag_id'] for row in cur.fetchall()]
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

	def get_ads(self, seller_id=None):
		query = f'SELECT ad.*  ' \
		        f'FROM ad '
		if seller_id is not None:
			query += f'WHERE seller_id = {seller_id} '
		cur = self.connection.execute(query)
		return [dict(row) for row in cur.fetchall()]

	def delete_ad_tags(self, ad_id):
		self.connection.execute(
			f'DELETE FROM adtag '
			f'WHERE ad_id = {ad_id}'
		)


	def get_tags(self, tags_id):
		tags = []
		for tag_id in tags_id:
			cur = self.connection.execute(
				f'SELECT name '
				f'FROM tag '
				f'WHERE id = {tag_id}'
			)
			tags.append(dict(cur.fetchone())['name'])
		return tags

	def get_car(self, car_id):
		cur = self.connection.execute(
			f'SELECT make, model, mileage, num_owners, reg_number '
			f'FROM car '
			f'WHERE id = {car_id}'
		)
		return dict(cur.fetchone())

	def get_car_color(self, car_id):
		cur = self.connection.execute(
			f'SELECT color_id '
			f'FROM carcolor '
			f'WHERE car_id = {car_id}'
		)
		return [dict(row)['color_id'] for row in cur.fetchall()]

	def get_images(self, car_id):
		cur = self.connection.execute(
			f'SELECT title, url '
			f'FROM image '
			f'WHERE car_id = {car_id}'
		)
		return [dict(row) for row in cur.fetchall()]

	def update_title(self, ad_id, title):
		self.connection.execute(
			f'UPDATE ad'
			f'SET title = "{title}"'
			f'WHERE id = {ad_id}'
		)

	def update_car(self, car_id, car_update):
		set_params = ', '.join(f'{key} = "{values}"' for key, values in car_update.items())
		self.connection.execute(
			f'UPDATE car '
			f'SET {set_params} '
			f'WHERE id = {car_id}'
		)

	def delete_car_color(self, car_id):
		self.connection.execute(
			f'DELETE FROM carcolor '
			f'WHERE car_id = {car_id}'
		)

	def delete_images(self, car_id):
		self.connection.execute(
			f'DELETE FROM image '
			f'WHERE car_id = {car_id}'
		)

	def get_ad(self, ad_id):
		cur = self.connection.execute(
			f'SELECT date, title, seller_id, car_id '
			f'FROM ad '
			f'WHERE id = {ad_id}'
		)
		try:
			ad = dict(cur.fetchone())
		except:
			return None
		return ad


# class AdService:
# 	def __init__(self, connection):
# 		self.connection = connection

	# def get_ad(self, ad_id):
	# 	cur = self.connection.execute(
	# 		f'SELECT date, title, seller_id, car_id '
	# 		f'FROM ad '
	# 		f'WHERE id = {ad_id}'
	# 	)
	# 	try:
	# 		ad = cur.fetchone()
	# 	except:
	# 		return None
	# 	return dict(ad)

	# def get_ad_tags(self, ad_id):
	# 	cur = self.connection.execute(
	# 		f'SELECT tag_id '
	# 		f'FROM adtag '
	# 		f'WHERE ad_id = {ad_id}'
	# 	)
	# 	try:
	# 		tags_id = [dict(row) for row in cur.fetchall()]
	# 	except:
	# 		return []
	# 	return tags_id

	# def get_tags(self, tags_id):
	# 	tags = []
	# 	for tag_id in tags_id:
	# 		cur = self.connection.execute(
	# 			f'SELECT name '
	# 			f'FROM tag '
	# 			f'WHERE id = {tag_id}'
	# 		)
	# 		tags.append(dict(cur.fetchone())['name'])
	# 	return tags
	#
	# def get_car(self, car_id):
	# 	cur = self.connection.execute(
	# 		f'SELECT make, model, mileage, num_owners, reg_number '
	# 		f'FROM car '
	# 		f'WHERE id = {car_id}'
	# 	)
	# 	return dict(cur.fetchone())
	#
	# def get_car_color(self, car_id):
	# 	cur = self.connection.execute(
	# 		f'SELECT color_id '
	# 		f'FROM carcolor '
	# 		f'WHERE car_id = {car_id}'
	# 	)
	# 	return [dict(row)['color_id'] for row in cur.fetchall()]
	#
	# def get_images(self, car_id):
	# 	cur = self.connection.execute(
	# 		f'SELECT title, url '
	# 		f'FROM image '
	# 		f'WHERE car_id = {car_id}'
	# 	)
	# 	return [dict(row) for row in cur.fetchall()]


