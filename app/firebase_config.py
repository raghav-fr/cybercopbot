import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

SERVICE_KEY_PATH = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')

cred = credentials.Certificate(SERVICE_KEY_PATH)

try:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'cybercopai.firebasestorage.app'  # e.g. 'myproject.appspot.com'
    })
except ValueError:
    # already initialized
    pass

db = firestore.client()
print(db)
bucket = storage.bucket()