import requests
import cv2
import numpy as np
import json

send_to_predict = 0

if send_to_predict == 1:

    file_name = 'Images/AF02.jpg'
    files = [
        ('file', (file_name, open(file_name, 'rb'), 'application/octet'))
        #('meta', ('meta', json.dumps(meta), 'application/json') ),
    ]

    url = "http://127.0.0.1:5000/skin"

    r = requests.post(url, files=files)


else:
    file_name = 'Images/AF02.jpg'
    files = [
        ('file', (file_name, open(file_name, 'rb'), 'application/octet'))
        #('meta', ('meta', json.dumps(meta), 'application/json') ),
    ]

    url = "http://127.0.0.1:5000/face_analysis"

    r = requests.post(url, files=files)