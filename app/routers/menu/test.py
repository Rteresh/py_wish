import os

from aiogram import Router

all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_media')

test_router = Router()

user_data = {}
