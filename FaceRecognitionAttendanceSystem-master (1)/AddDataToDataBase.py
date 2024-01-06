import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://attandencesystemcep-default-rtdb.firebaseio.com/"
})
ref =db.reference('Students')
data = {
    "321654":
        {
            "name": "Babar Azam",
            "major":"king of Cricket",
             "year":7,
            "total_attendance":6,
            "Roll,No": "SE-20023",
            "Starting Year":2020,
            "last_attendance_time":"2024-1-2 00:6:40"

        },
"852741":
        {
            "name": "Shaheen",
            "major":"Boller",
            "Starting Year":2020,
            "total_attendance":7,
            "Roll,NO": "SE-20014",
            "year":6,
            "last_attendance_time":"2024-1-2 00:6:40"

        },
"963852":
        {
            "name": "Elon Musk",
            "major":"Physics",
            "Starting Year":2020,
            "total_attendance":6,
            "Roll,No": "SE-",
            "year":4,
            "last_attendance_time":"2024-1-2 00:6:40"

        }
}
for key,value in data.items():
    ref.child(key).set(value)