import os

import firebase_admin
from firebase_admin import credentials, messaging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(base_dir, "service_account.json")


cred = credentials.Certificate(json_path)
firebase_admin.initialize_app(cred)
