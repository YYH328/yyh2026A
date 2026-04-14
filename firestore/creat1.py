import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "楊硯涵2",
  "mail": "shaina95328@gmail.com",
  "lab": 666
}

doc_ref = db.collection("靜宜資管2026a")
doc_ref.add(doc)
