import os


class Config:
	DB_CONNECTION = os.getenv('DB_CONNECTION', 'db.db')
	SECRET_KEY = os.getenv('SECRET_KEY', 'secret').encode()


