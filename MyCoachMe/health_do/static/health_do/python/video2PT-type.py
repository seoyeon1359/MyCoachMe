# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
import numpy as np
from sys import platform
import argparse

#1.영상으로부터 운동부위 반환하기(각도의 변화량 이용)
#2.운동부위의 범위 알려주기. 여기부터 여기가 ㅇㅇ운동

body_part_names = {
    "L_arm","R_arm",
    "L_elbow","R_elbow",
    "L_waist","R_waist",
    "L_leg","R_leg",
    "L_knee","R_knee"
}

body_part_keypoints = {
    "L_arm"   : [1,5,6],
    "R_arm"   : [1,2,3],
    "L_elbow" : [5,6,7],
    "R_elbow" : [2,3,4],
    "L_waist" : [1,8,12],
    "R_waist" : [1,8,9],
    "L_leg"   : [8,12,13],
    "R_leg"   : [8,4,10],
    "L_knee"  : [12,13,14],
    "R_knee"  : [9,10,11]
}
body_part_scores = {
    "L_arm"   : 0,
    "R_arm"   : 0,
    "L_elbow" : 0,
    "R_elbow" : 0,
    "L_waist" : 0,
    "R_waist" : 0,
    "L_leg"   : 0,
    "R_leg"   : 0,
    "L_knee"  : 0,
    "R_knee"  : 0,
}
    

def point2degree(poseKeypoints):
    #print("point2degree",poseKeypoints.shape)
    p = poseKeypoints[0] 
    k = body_part_keypoints
    degree = {}
    for name in body_part_names:  
        ##print
        rad = np.arctan2(p[k[name][2]][1] - p[k[name][0]][1], p[k[name][2]][0] - p[k[name][0]][0]) - np.arctan2(p[k[name][1]][1] - p[k[name][0]][1], p[k[name][1]][0] - p[k[name][0]][0]) 
        #print(rad) 대부분 -1에서 1이 나옴
        deg = rad * (180 / np.pi)
        degree[name] = 180-abs(deg)
    #print(degree)
    return degree

def compareDegree(before_d,now_d):
    global body_part_scores
    #print("compareDegree")
    for key in now_d:
        dif = abs(before_d[key]-now_d[key])
        if dif>=45:
            print(key,dif,body_part_scores[key])
            body_part_scores[key] += 1

def check_bodyparts(poseKeypoints):
    print(poseKeypoints)

def getScore2rank(scores,thresholds):
    #print(thresholds)
    for key in scores:
        #print(scores[key])
        if scores[key] >= thresholds:
            print(key,end=" ")
        

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../bin/python/openpose/Release');
        
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../x64/Release;' +  dir_path + '/../bin;'
        #print(os.environ['PATH'])
        import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e
    
    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default="../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    parser.add_argument("--video_path", default='../examples/media/221.mp4', help="Process an video. ")
    
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../models/"

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    cap = cv2.VideoCapture(args[0].video_path)
    print("video:",args[0].video_path)
    print('Frame width:', int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
    print('Frame height:', int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print('Frame count:', int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))

    fps = cap.get(cv2.CAP_PROP_FPS)
    print('FPS:', fps)
    
    imgs = {"../examples/media/test.png","../examples/media/test2.png"}
    #좌표는 x좌표. y좌표, 신뢰도 점수
    
    before_degree = {}
    now_degree = {}
    first = True
    
    #1. 디버깅: 두개 이미지로 
    # for img in imgs:
    #     print(img)
    #     imageToProcess = cv2.imread(img)
    #     datum.cvInputData = imageToProcess
    #     opWrapper.emplaceAndPop(op.VectorDatum([datum]))
        
    #     now_degree = point2degree(datum.poseKeypoints)
    #     if first :
    #         first = False
    #     else:     
    #         compareDegree(before_degree,now_degree)
        
    #     before_degree = now_degree

    #2. 영상
    skip_frames = 10
    frame_count = 0
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            break
        frame_count += 1
        if frame_count % skip_frames == 0:
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            datum.cvInputData = frame
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))
            now_degree = point2degree(datum.poseKeypoints)
            if first :
                first = False
            else:     
                compareDegree(before_degree,now_degree)
            before_degree = now_degree
            #프레임 출력해보기
            #cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
            #cv2.imshow('frame',frame)
            
            # if cv2.waitKey(50) & 0xFF == ord('q'):
            #     break
    print(body_part_scores)
    #max_key = max(body_part_scores, key=lambda k: body_part_scores[k])
    #getScore2rank
    print("영상의 운동 부위: ",end = "")
    getScore2rank(body_part_scores,int(cap.get(cv2.CAP_PROP_FRAME_COUNT)/3/skip_frames))
except Exception as e:
    print(e)
    sys.exit(-1)
