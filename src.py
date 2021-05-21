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
import mgp_src as mgp


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

def mapping_facetype(circ, elliptic, long, prism, sq, triangle, weight=5):
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

def send_request_macro(img_path):
    ENCODING = 'utf-8'
    appkey = 'bByf_VwAWYkaLSlf22h3p4LhsJMlRSjZ'#'nOBd1rC7BakVYQJHuT_nSDMTvEr37JXe'
    secret_id = 'bo2Y44zwjMiS9osaoO95enmrAGvAQWOr'#'e4gUfLLz52oGj_7AGmiMJYCxOOdRtaj0'
    url = f'https://openapi.mtlab.meitu.com/v2/macro_facial_analysis?api_key={appkey}&api_secret={secret_id}'
    #image_read = img_FileStorage.read()
    #image_64_encode = base64.encodebytes(image_read).decode('utf-8')
    image = open(img_path, 'rb')
    image_read = image.read()
    image_64_encode = base64.encodebytes(image_read).decode('utf-8')
    image.close()
    body = {
        "parameter": {
            "return_attributes":"gender"
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
                # print('face_landmarks:', face_landmarks)
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACE_CONNECTIONS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)
            cv2.imwrite('assets/results/' + 'user' + '_mesh.jpg', annotated_image)
        print(type(results.multi_face_landmarks[0]))
        return results.multi_face_landmarks[0].landmark

"""
Input: landmarks::landmarks obj # facial landmarks
Output: np arrays [ ]
"""
def face_analysis_landmarks(landmarks, face_features_from_meitu):
    upper_court = (landmarks[8].y - landmarks[10].y) * 1.3
    mid_court = landmarks[2].y - landmarks[8].y
    lower_court = landmarks[152].y - landmarks[2].y

    face_length = upper_court + mid_court + lower_court
    face_width = landmarks[454].x - landmarks[234].x

    left_eye_length = landmarks[130].x - landmarks[243].x
    left_eye_width = max(landmarks[22].y, landmarks[23].y, landmarks[24].y) - \
        min(landmarks[27].y, landmarks[28].y, landmarks[29].y)
    right_eye_length = landmarks[359].x - landmarks[465].x
    right_eye_width = max(landmarks[257].y, landmarks[258].y, landmarks[259].y) - \
        min(landmarks[252].y, landmarks[253].y, landmarks[254].y)
    
    eye_distance = landmarks[465].x - landmarks[243].x
    eye_shape = mapping_eye_shape(face_features_from_meitu['eye_shape']['value'], face_features_from_meitu['eye_shape']['confidence'])

    nose_length = landmarks[2].y - landmarks[168].y
    nose_width = landmarks[327].x - landmarks[98].x
    nose_shape = mapping_nose(face_features_from_meitu['nose_shape']['value'], face_features_from_meitu['nose_shape']['confidence'])
    
    mouth_thickness = mapping_mouth_thickness(face_features_from_meitu['mouth_thickness']['value'], face_features_from_meitu['mouth_thickness']['confidence'])
    mouth_length = landmarks[291].x - landmarks[61].x
    mouth_width = landmarks[291].y - (landmarks[267].y + landmarks[37].y) * 0.5
    nose2lips = landmarks[0].y - landmarks[2].y
    lips2jaw = landmarks[152].y - landmarks[17].y
    lips_peak = mapping_lip_peak(face_features_from_meitu['lip_peak']['value'], face_features_from_meitu['lip_peak']['confidence'])
    
    cheek_shape = mapping_cheek_shape(face_features_from_meitu['cheek_shape']['value'], face_features_from_meitu['cheek_shape']['confidence'])
    cheek_distance = landmarks[288].x - landmarks[58].x
    upper_court_ratio = upper_court / face_length * 100
    mid_court_ratio = mid_court / face_length * 100
    lower_court_ratio = lower_court / face_length * 100
    eye_width_ratio = (left_eye_width + right_eye_width) / face_length * 50
    eye_length_ratio = (left_eye_length + right_eye_length) / face_width * 50
    eye_distance_ratio = eye_distance / face_width * 100
    nose_length_ratio = nose_length / face_length * 100
    nose_width_ratio = nose_width / face_width * 100
    nose2lips_ratio = nose2lips / face_length * 100
    lips2jaw_ratio = lips2jaw / face_length * 100
    mouth_width_ratio = mouth_length / cheek_distance * 100
    cheek_ratio = cheek_distance / face_width * 100
    risorius = float(face_features_from_meitu['risorius_yes']['value'])
    temple = float(face_features_from_meitu['temple_full']['value'])
    eye_arr = np.array([eye_shape, eye_width_ratio, eye_length_ratio, eye_distance_ratio])
    nose_arr = np.array([nose_shape, nose_width_ratio, nose_length_ratio])
    lips_arr = np.array([mouth_thickness, nose2lips_ratio, lips2jaw_ratio, mouth_width_ratio])
    facetype_arr = np.array([cheek_ratio, upper_court_ratio, mid_court_ratio, lower_court_ratio, \
        cheek_shape, risorius, temple])
    
    return eye_arr, nose_arr, lips_arr, facetype_arr





def face_comparison(analysis_data, face_features_meitu):
    user_eye_arr, user_nose_arr, user_lips_arr, user_facetype_arr = analysis_data
    # ratio notification
    three_courts_ratio = user_facetype_arr[1:4] / min(user_facetype_arr[1:4])
    court_res = '三庭五眼分析结果：你的三庭比例为 '
    court_res += '{0:.2f} : {1:.2f} : {2:.2f}'.format(three_courts_ratio[0], three_courts_ratio[1], three_courts_ratio[2])
    if sum(three_courts_ratio) < 3.2:
        court_res += '/n  ' + '你的三庭比例基本合适~'
    else:
        indice = np.argsort(three_courts_ratio)
        thresh_ratio = 1.05
        if three_courts_ratio[indice[0]] > thresh_ratio and three_courts_ratio[indice[1]] < thresh_ratio:
            switcher = {
                0: '你的上庭过长哟',
                1: '你的中庭过长哟',
                2: '你的下庭过长哟'
            }
            court_res += switcher[indice[0]]
        elif three_courts_ratio[indice[0]] > thresh_ratio and three_courts_ratio[indice[1]] > thresh_ratio:
            switcher = {
                0: '你的上庭过短哟',
                1: '你的中庭过短哟',
                2: '你的下庭过短哟'
            }
            court_res += switcher[indice[2]]
    
    # compare with the standard face
    AFstandard_landmarks = get_landmarks('Images/AF_standard.png')
    with open('micro_face_analysis_standard.json') as f:
        micro_face_analysis_dict = json.load(f)
    json_obj = json.loads(micro_face_analysis_dict['AF_standard.png'])
    face_json = json_obj['media_info_list'][0]['media_extra']['faces'][0]['face_attributes']
    eye_arr, nose_arr, lips_arr, facetype_arr = face_analysis_landmarks(AFstandard_landmarks, face_json)

    user_eye_arr, user_nose_arr, user_lips_arr, user_facetype_arr = analysis_data
    
    eye_response, eye_makeup_vec = mgp.eye_comparison(eye_arr, user_eye_arr)
    nose_response, nose_makeup_vec = mgp.nose_comparison(nose_arr, user_nose_arr)
    lip_response, lip_makeup_vec = mgp.lip_comparison(lips_arr, user_lips_arr)

    return court_res, eye_response, nose_response, lip_response

def is_in_poly(p, poly):
    """
    :param p: [x, y]
    :param poly: [[], [], [], [], ...]
    :return: is_in: boolean. True = p in poly
    """
    px, py = p
    is_in = False
    for i, corner in enumerate(poly):
        next_i = i + 1 if i + 1 < len(poly) else 0
        x1, y1 = corner
        x2, y2 = poly[next_i]
        if (x1 == px and y1 == py) or (x2 == px and y2 == py):  # if point is on vertex
            is_in = True
            break
        if min(y1, y2) < py <= max(y1, y2):  # find horizontal edges of polygon
            x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x == px:  # if point is on edge
                is_in = True
                break
            elif x > px:  # if point is on left-side of line
                is_in = not is_in
    return is_in

def get_pt_ref(pt, landmarks):
    """
    :params pt: np.array([x, y]), the location of the point 
    :params landmarks: landmark obj
    :return pt_ref: [np.array([x1, x2, x3]), np.array[idx1, idx2, idx3]]
    :return boolean: True = found the correct solution as pt_ref
    """
    SEARCH_LIST=[[0,1,2], [0,1,3], [0,2,3], [1,2,3], [0,1,4], [0,2,4], [0,3,4], [1,2,4], [1,3,4], [2,3,4], [0,1,5], [0,2,5], [0,3,5], [0,4,5], [1,2,5], [1,3,5], [1,4,5], [2,3,5], [2,4,5],[3,4,5]]
    
    landmarks_arr = np.array([[i.x, i.y] for i in landmarks])
    dist = np.linalg.norm(landmarks_arr - pt, axis = 1)
    sorted_idx = np.argsort(dist)
    for search in SEARCH_LIST:
        poly = landmarks_arr[sorted_idx][search]
        if is_in_poly(pt, poly):
            a = np.array([[poly[0,0], poly[1,0], poly[2,0]],[poly[0,1], poly[1,1], poly[2,1]], [1, 1, 1]])
            b = np.array([pt[0], pt[1], 1])
            ans = np.linalg.solve(a,b)
            pt_ref = [ans[0], ans[1], ans[2], int(sorted_idx[search[0]]), int(sorted_idx[search[1]]), int(sorted_idx[search[2]])]
            return pt_ref, True # Found correct solution
    return [1.0, 0.0, 0.0,  int(sorted_idx[0]), int(sorted_idx[1]), int(sorted_idx[2])], False # Solution not found. Return the nearest point

def get_pt_location(pt_ref, landmarks):
    """
    :params pt_ref: [np.array([x1, x2, x3]), np.array[idx1, idx2, idx3]]
    :params landmarks: landmark obj
    :return np.array([x, y, z])
    """
    landmarks_arr = np.array([[i.x, i.y, i.z] for i in landmarks])
    ref_ratio, ref_idx = pt_ref
    return np.dot(landmarks_arr[ref_idx].T, np.array(ref_ratio))

def load_makeup(file_path, landmarks, strict=False):
    counts = []
    fails = []
    steps = []
    with open(file_path) as fp:
        for line in fp:
            if line.endswith(':\n'):
                step = []
                fail = 0
                count = 0
            elif line == '\n':
                steps.append(step)
                fails.append(fail)
                counts.append(count)
            else:
                x_str, y_str=line.split()
                x = float(x_str)
                y = float(y_str)
                pt = np.array([x, y])
                pt_ref, flag = get_pt_ref(pt, landmarks)

                if strict:
                    if flag:
                        count += 1
                        step.append(pt_ref)
                    else:
                        fail += 1
                else:
                    count += 1
                    step.append(pt_ref)
                    if not flag:
                        fail += 1
    return steps, counts, fails