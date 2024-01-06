import cv2
import os
import pickle
import face_recognition
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("D:\FaceRecognitionAttendanceSystem-master (1)\ServiceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://attandencesystemcep-default-rtdb.firebaseio.com/",
    'storageBucket': "attandencesystemcep.appspot.com"
})
bucket = storage.bucket()
# Open the camera
cap = cv2.VideoCapture(0)

# Set the width and height of the camera
cap.set(3, 640)
cap.set(4, 720)

# importing the mode images into a list
folderModePath = "Resources/Modes"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))
# print(modePathList)

# studentIds and encoded data of images is saved in pickle
# Now loading that encoded file
print("Encode file loading")
file = open("EncodeFile.p", "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
# fetching the encodings and student ids
encodeListKnown, studentIds = encodeListKnownWithIds
print(studentIds)
print("Encode file loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

# Storing bg
imgBackground = cv2.imread("Resources/background.png")

while True:
    # img variable is storing the camera
    success, img = cap.read()

    # now resizing the image that is captured by the camera because large images require too much computation power
    # resizing using the scale values(0.25 is the smallest)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)

    # now fetching the face location from the entire frame using face recognition
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # storing img at some specific points of the background
    imgBackground[175:175 + 480, 94:94 + 640] = img

    imgBackground[38:38 + 633, 833:833 + 414] = imgModeList[modeType]
    if faceCurFrame:
        # for summing up two loops in a single loop
        for encoFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            # answer will be true or false. It will just tell face is matching or not
            matches = face_recognition.compare_faces(encodeListKnown, encoFace)
            # answer will be integer. It will just tell difference between the face stored and the current face
            faceDis = face_recognition.face_distance(encodeListKnown, encoFace)
            print("matches", matches)
            print("faceDis", faceDis)

            # Now finding the index where the image in the list becomes true and that is the least value of faceDist
            matchIndex = np.argmin(faceDis)
            # print(matchIndex)
            # print(studentIds[matchIndex])
            # rectangle thickness = rt
            y1, x2, y2, x1 = faceLoc
            # multiplying by 4 because size is reduced
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            # applying padding
            bbox = 90 + x1, 20 + y2, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]
            if counter == 0:
                cvzone.putTextRect(imgBackground,"Loading",(275,400))
                cv2.imshow("Face Attendance",imgBackground)
                cv2.waitKey()
                counter = 1
                modeType = 2

            if counter != 0:
                if counter == 1:
                    studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Get the image from Storage
                # blob = bucket.get_blob(f'Images/{id}.png')
                # array = np.frombuffer(blob.download_as_string(), np.uint8)
                # imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

            # update data of attendance
            datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                             "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondsElapsed)
            if secondsElapsed >30:

             ref = db.reference(f'Students/{id}')
             studentInfo['total_attendance'] += 1
             ref.child('total_attendance').set(studentInfo['total_attendance'])
             ref.child('last_attendance_time').set(datetime.now().strftime( "%Y-%m-%d %H:%M:%S"))
            else:
                # Already marked
                modeType = 1
                counter = 0
                imgBackground[38:38 + 633, 833:833 + 414] = imgModeList[modeType]

            # updating new bg image named markded when attendance is marked
            if 10 < counter < 20:
                modeType = 3
            imgBackground[38:38 + 633, 833:833 + 414] = imgModeList[modeType]

        if counter <= 10:
            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (920, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1),

            cv2.putText(imgBackground, str(studentInfo['major']), (1006, 525),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1),
            cv2.putText(imgBackground, str(id), (1006, 465),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1),
            cv2.putText(imgBackground, str(studentInfo['standing']), (950, 600),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 100), 2),
            cv2.putText(imgBackground, str(studentInfo['Starting Year']), (1090, 600),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 2)

            cv2.putText(imgBackground, str(studentInfo['year']), (1207, 600),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 2),



            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
            offset = (414 - w) // 2
            cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 400),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1),

            # imgBackground[175:175+216,909:909+216] = imgStudent
            counter += 1
            # Active bg pic
        if  counter >= 20:
            counter = 0
            modeType = 1
            studentInfo = []
            imgStudent = []
            imgBackground[38:38 + 633, 833:833 + 414] = imgModeList[modeType]


            # with the help of matchIndex we will draw a rectangle around our face in live camera using cvzone
            if matches[matchIndex]:
                print("Known face detected")
        if not success:
            print("Error reading frame from camera")
            break
    else:
        modeType = 0
        counter = 0
    # Showing main bg
    cv2.imshow("Face Attendance", imgBackground)

    # Exit the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
