import firebase_admin
from firebase_admin import credentials, messaging


cred  = credentials.Certificate('hotpot/service_account.json')
firebase_admin.initialize_app(cred)