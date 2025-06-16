import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL=os.environ.get('DATABASE_URL')


LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


SAVE_DIR = os.environ.get('SAVE_DIR', 'saved_images')

LOGS_DIR = os.environ.get('LOGS_DIR', 'logs')
