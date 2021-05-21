from src import *
import pdb
import os
from PIL import Image, ImageDraw
import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_classful import FlaskView, route
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
import json
from matplotlib import pyplot as plt
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

        pil_img = Image.open(request.files['file'])
        path_origin = 'assets/origin/skin_img_origin.jpg'
        pil_img.save(path_origin)
        pil_img.close() 
        #landmarks = []

        #for pic in match_pics:
        #    landmarks.append(get_landmarks('Images/'+pic))
        user_landmarks = get_landmarks(path_origin, save_plot=True)

        #for pic_name in match_pics:
        #    json_obj = json.loads(data[pic_name])
        #    face_features_from_meitu = json_obj['media_info_list'][0]['media_extra']['faces'][0]['face_attributes']
        resp_gender = send_request_macro(path_origin)
        json_obj_gender = json.loads(resp_gender)
        gender = json_obj_gender['media_info_list'][0]['media_extra']['faces'][0]['face_attributes']['gender']['value']

        if gender == 0:
            micro_face_analysis_json_path = 'micro_face_analysis.json'
        else:
            micro_face_analysis_json_path = 'micro_face_analysis_male.json'
        
        match_pics = beauty_ugly_match(resp, micro_face_analysis_json_path, top_k=3)
        print(match_pics)


        json_obj = json.loads(resp)
        face_features_from_meitu = json_obj['media_info_list'][0]['media_extra']['faces'][0]['face_attributes']

        analysis_data = face_analysis_landmarks(user_landmarks, face_features_from_meitu)
        court_resp_str, eye_resp_str, nose_resp_str, lips_resp_str = face_comparison(analysis_data, face_features_from_meitu)
        print(
            match_pics,
            court_resp_str, 
            eye_resp_str, 
            nose_resp_str, 
            lips_resp_str
        )
        return jsonify({'match_pics':{'0':match_pics[0], '1':match_pics[1], '2':match_pics[2]}, 
            'court_resp':court_resp_str, 
            'eye_resp':eye_resp_str, 
            'nose_resp':nose_resp_str, 
            'lips_resp':lips_resp_str
            #'steps': steps
            })
    
    @route('/reload_makeup', methods=['POST'])
    def reload_makeup(self):
        makeup_file = 'MakeUp_keypoints.txt'#'makeup_keypoint.txt'
        makeup_ref_image = 'Images/AF02.jpg'
        ref_landmarks = get_landmarks(makeup_ref_image)
        steps, counts, fails = load_makeup(makeup_file, ref_landmarks, strict=True)
        print(counts, fails)
 
        save_json_path = 'C:\\Users\\foxto\\Desktop\\ecohealth_v2\\The-Mountain\\src\\data\\'
        with open(save_json_path + 'makeup_refs.json','w') as outfile:
            json.dump({'steps':steps}, outfile)
        return jsonify({'steps':steps})
    
    @route('/facemesh', methods=['POST'])
    def facemesh(self):
        pil_img = Image.open(request.files['file'])
        #pil_img.save('pil_img.jpg')
        numpy_image = np.array(pil_img)
        opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

EcoMaggie.register(app, route_base='/')

if __name__ == '__main__':
    app.run()