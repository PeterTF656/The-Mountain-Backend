import urllib.request
import urllib.error
import time
import cv2
import mediapipe as mp
import time
import base64
import linecache
import json
import requests
import numpy as np

def send_request_skin_facepp(img_path):
    http_url = 'https://api-cn.faceplusplus.com/facepp/v1/skinanalyze_advanced'
    key = "6lpBvWVZ_UxyWdUXwY8GyaNOccbTbRjm"
    secret = "E8rpN30qAUdJi35wFEElYnIE1cu0UZ78"

    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(secret)
    data.append('--%s' % boundary)
    fr = open(img_path, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(fr.read())
    fr.close()
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_rect_confidence')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append(
        "gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus")
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=5)
        # get response
        qrcont = resp.read()
        # if you want to load as json, you should decode first,
        # for example: json.loads(qrount.decode('utf-8'))
        return qrcont.decode('utf-8')
    except urllib.error.HTTPError as e:
        return (e.read().decode('utf-8'))
        

def mapping_eye_shape(eye_shape, confidence, weight=5, mapping_dict={'ba01':0, 'ba02':-1, 'ba03':2, 'ba04':0, 'ba05':-2}):
    return weight*mapping_dict[eye_shape]*confidence

def mapping_eye_dist(eye_distance, confidence, weight=5, mapping_dict={'ad01':1, 'ad02':-1, 'ad03':0}):
    return weight*mapping_dict[eye_distance]*confidence

def mapping_nose(nose_shape, confidence, weight=5, mapping_dict={'ca01':-1, 'ca02':0, 'ca03':1, 'ca04':2}):
    return weight*mapping_dict[nose_shape]*confidence

def mapping_mouth_thickness(mouth, confidence, weight=3, mapping_dict={'da01':0, 'da02':1, 'da03':2, 'da04':-1, 'da05':-2}):
    return weight*mapping_dict[mouth]*confidence

def mapping_cheek_shape(cheek, confidence, weight=5, mapping_dict={'ea01':1, 'ea02':-1}):
    return weight*mapping_dict[cheek]*confidence

def mapping_facetype(circ, elliptic, long, prism, sq, triangle, weight=20):
    templist = [circ['value'], elliptic['value'], long['value'], prism['value'], sq['value'], triangle['value']]
    return [float(x) * weight for x in templist]

def mapping_lip_peak(lip_peak, confidence, weight=1, mapping_dict={'db01':0, 'db02':2, 'db03':1}):
    return weight*mapping_dict[lip_peak]*confidence

def mapping_face_vec(face_json):
    vec = [0, 0, 0, 0, 0]
    vec[0] = mapping_eye_shape(face_json['eye_shape']['value'], face_json['eye_shape']['confidence'])
    vec[1] = mapping_eye_dist(face_json['eye_distance']['value'], face_json['eye_distance']['confidence'])
    vec[2] = mapping_nose(face_json['nose_shape']['value'], face_json['nose_shape']['confidence'])
    vec[3] = mapping_mouth_thickness(face_json['mouth_thickness']['value'], face_json['mouth_thickness']['confidence'])
    vec[4] = mapping_cheek_shape(face_json['cheek_shape']['value'], face_json['cheek_shape']['confidence'])
    vec.extend(mapping_facetype(face_json['facetype_circular'], face_json['facetype_elliptic'], 
        face_json['facetype_long'], face_json['facetype_prism'], face_json['facetype_square'], face_json['facetype_triangle']))
    return vec

def beauty_ugly_match(user_json, json_path, top_k=2):
    with open(json_path) as f:
        data = json.load(f)
    
    pic_name_list = []
    vec_arr = []
    num = 0
    for pic_name in data.keys():
        pic_name_list.append(pic_name)
        json_obj = json.loads(data[pic_name])
        face_json = json_obj['media_info_list'][0]['media_extra']['faces'][0]['face_attributes']
        vec = mapping_face_vec(face_json)
        vec_arr.append(vec)

    face_array = np.array(vec_arr)
    json_obj = json.loads(user_json)
    face_json = json_obj['media_info_list'][0]['media_extra']['faces'][0]['face_attributes']
    
    user_vec = np.array(mapping_face_vec(face_json))
    norm = []
    for i in range(face_array.shape[0]):
        vec = face_array[i,:]
        norm.append(np.linalg.norm(vec-user_vec))
    norm = np.array(norm)
    sorted_index = np.argsort(norm)
    most_similar = sorted_index[:top_k]
    return [pic_name_list[x] for x in most_similar]

def send_request(img_FileStorage):
    ENCODING = 'utf-8'
    appkey = 'bByf_VwAWYkaLSlf22h3p4LhsJMlRSjZ'#'nOBd1rC7BakVYQJHuT_nSDMTvEr37JXe'
    secret_id = 'bo2Y44zwjMiS9osaoO95enmrAGvAQWOr'#'e4gUfLLz52oGj_7AGmiMJYCxOOdRtaj0'
    url = f'https://openapi.mtlab.meitu.com/v1/micro_facial_analysis?api_key={appkey}&api_secret={secret_id}'
    image_read = img_FileStorage.read()
    image_64_encode = base64.encodebytes(image_read).decode('utf-8')
    body = {
        "parameter": {
            "return_attributes":"facial_analysis"
        },
        "extra": {},
        "media_info_list": [{
            "media_data": image_64_encode,
            "media_profiles": {
                "media_data_type": "jpg"
            }
        }]
    }
    jsoned = json.dumps(body)
    headers = {"Content-Type":"application/json"}
    x = requests.post(url, data = jsoned, headers = headers)
    resp = json.dumps(x.json())
    return resp

def get_landmarks(pic_path, save_plot=False):
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        min_detection_confidence=0.5) as face_mesh:

        image = cv2.imread(pic_path)
        # Convert the BGR image to RGB before processing.
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Print and draw face mesh landmarks on the image.
        if save_plot:
            annotated_image = image.copy()
            for face_landmarks in results.multi_face_landmarks:
                #print('face_landmarks:', face_landmarks)
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACE_CONNECTIONS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)
                cv2.imwrite('/assets/results/' + 'user' + '_mesh.jpg', annotated_image)
        return results