import cv2 as cv
import time
import datetime
import requests
import json
import pathlib
import re

API_ROUTE_URL = "http://localhost:5000/sendEmail"
SECONDS_TO_RECORD_AFTER_DETECTION = 15
SECONDS_BETWEEN_RECORDINGS = 60

def drawRectangle(obj, frame):
    for (x, y, width, heigth) in obj:
        cv.rectangle(frame, (x, y), (x + width, y + heigth), (0, 255, 0), 2)

def makeApiRequest(fileName, email):
    payload = json.dumps({
        "to": email,
        "path": f"{pathlib.Path(__file__).parent.resolve()}/videos",
        "fileName": fileName
    })

    headers = {
        "Content-Type": "application/json"
    }

    return requests.request("POST", API_ROUTE_URL, headers=headers, data=payload)

def validateEmail(email):
    r = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')

    if r.match(email): 
        return True

    return False

def requestEmail():

    email = ""
    first_time = True

    while True:

        if first_time:
            print("Insira o e-mail para onde vamos enviar os alertas:")
        email = input()

        if validateEmail(email):
            print("\nE-mail cadastrado com sucesso!\n")
            return email
        else:
            first_time = False
            print("\nO e-mail inserido não é valido! Tente novamente:")
            
def main():

    email = requestEmail()

    # Setup
    cap = cv.VideoCapture(2) # É necessário encontrar o indice da sua camera
    frame_size = (int(cap.get(3)), int(cap.get(4)))
    fourcc = cv.VideoWriter_fourcc(*"mp4v")

    face_cascade = cv.CascadeClassifier(
        cv.data.haarcascades + "haarcascade_frontalface_default.xml")

    body_cascade = cv.CascadeClassifier(
        cv.data.haarcascades + "haarcascade_fullbody.xml")

    # Declaring variables
    detection = False
    last_time_saved = None
    start_time = None
    current_time = None

    print("Sistema iniciando...\n")

    # Main loop
    while True:
        _, frame = cap.read()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.25, 5)
        bodies = body_cascade.detectMultiScale(gray, 1.25, 5)

        if len(faces) + len(bodies) > 0:

            if not detection:
                if last_time_saved == None or time.time() - last_time_saved >= SECONDS_BETWEEN_RECORDINGS:
                    detection = True
                    start_time = time.time()
                    current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                    out = cv.VideoWriter(
                        f"./videos/{current_time}.mp4", fourcc, 20, frame_size
                    )
                    print(f"Gravação iniciada!")
            
        
        if detection and time.time() - start_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
            detection = False
            out.release()
            last_time_saved = time.time()

            print("Gravação finalizada!")

            fileName = current_time + ".mp4"

            try:
                response = makeApiRequest(fileName, email)

                if response.status_code == 200:
                    print(f"E-mail com arquivo {current_time}.mp4 enviado!\n")

            except:
                print("Algum erro ocorreu no envio do e-mail!")
            

        drawRectangle(faces, frame)
        drawRectangle(bodies, frame)

        if detection:
            out.write(frame)

        # Mostra a camera na tela
        cv.imshow("Camera", frame)

        if (cv.waitKey(1) == ord("q")):
            break

    out.release()
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
