from src import *
import pdb

from PIL import Image, ImageDraw
import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_classful import FlaskView, route
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
import json
app = Flask(__name__)
CORS(app)
run_with_ngrok(app)  # Start ngrok when app is run

@app.route('/hello')
def hello():
    return 'Go /predict'


class EcoMaggie(FlaskView):

    @route('/skin', methods=['POST'])
    def skin(self):
        #pdb.set_trace()
        pil_img = Image.open(request.files['file'])
        path_origin = 'assets/origin/skin_img_origin.jpg'
        pil_img.save(path_origin)
        pil_img.close()

        resp = send_request_skin_facepp(path_origin)
        resp_json = json.loads(resp)
        spots = ['acne', 'mole', 'skin_spot','closed_comedones']
        outline = [(255, 255, 0), (0, 0, 0), (255, 255, 255), (255, 0, 0)]
        #print(resp)
        with Image.open(path_origin) as img:
            img_canvas = ImageDraw.Draw(img)
            for i in range(len(spots)):
                for spot in resp_json['result'][spots[i]]['rectangle']:
                    img_canvas.rectangle([(spot['left'], spot['top']), (spot['left']+spot['width'], spot['top']+spot['height'])], fill=None, outline=outline[i], width=1)
            #img.show()
            img.save('assets/results/skin_img.jpg')
        return resp_json

    @route('/face_analysis', methods=['POST'])
    def face_analysis(self):
        resp = send_request(request.files['file'])
        print(resp)
        match_pics = beauty_ugly_match(resp, 'micro_face_analysis.json', top_k=3)

        pil_img = Image.open(request.files['file'])
        path_origin = 'assets/origin/skin_img_origin.jpg'
        pil_img.save(path_origin)
        pil_img.close()
        landmarks = []

        for pic in match_pics:
            landmarks.append(get_landmarks('Images/'+pic))
        user_landmarks = get_landmarks('Images/'+pic, save_plot=True)
        print(match_pics)
        return jsonify({'match_pics':{'0':match_pics[0], '1':match_pics[1], '2':match_pics[2]}})
    
    @route('/facemesh', methods=['POST'])
    def facemesh(self):
        pil_img = Image.open(request.files['file'])
        #pil_img.save('pil_img.jpg')
        numpy_image = np.array(pil_img)
        opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR) 

EcoMaggie.register(app, route_base='/')

if __name__ == '__main__':
    app.run()