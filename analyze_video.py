# This is where the video file is analyzed
# STEPS: Extract Images -> Find Body Positions -> Identify Distinct Swings -> Recieve Feedback + Pics

import cv2
from cvzone.PoseModule import PoseDetector
from fh_algorithms import *
from bh_algorithms import *
from normalize_points import normalize_pose
import json, os, string, random
from image_process import *
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

def myFunc(e):
    return e[0]

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

# Upload photo to Cloudinary
def pic_to_url(frame):
    letters = string.ascii_letters  # Uppercase and lowercase letters
    id_random = ''.join(random.choice(letters) for _ in range(6))
    cv2.imwrite(f'{id_random}.jpg', frame)
    upload_result = cloudinary.uploader.upload(f'{id_random}.jpg', public_id=id_random)
    os.remove(f'{id_random}.jpg')
    return upload_result["secure_url"]

def analyze_video(frameList, type, number_of_shots):
    fps = 30
    # frameList = frameList[60:]
    # frameList = frameList[:len(frameList)-60]
    global pics
    pics = []

    analysis = {
        'technique_accuracy': 0,
        'consistency': 0,
        'swing_speed': 0,
        'restarts': 0,
        'number_of_frames': 0
    }
    frames = {}
    # Main Loop for Forehand
    if type == 'fh':
        for i in range(number_of_shots):
            feedback = {
                'take_back': {},
                'contact_point': {},
                'follow_through': {}
            }

            frameList, feedback, analysis, found = fh_find_tb(frameList, feedback, analysis)
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
                tb_frame_num = len(frameList)
            else:
                tb_frame_num = False
            #print('Frames Left: ' + str(len(frameList)))
            frameList, feedback, analysis, found = fh_find_cp(frameList, feedback, analysis)
            #print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
            frameList, feedback, analysis, found = fh_find_ft(frameList, feedback, analysis)
            #print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1

            # Add Swing Speed
            if tb_frame_num != False:
                analysis['swing_speed'] = analysis['swing_speed'] + (tb_frame_num - len(frameList))
            frames['Swing ' + str(i)] = feedback

    # Main Loop for Forehand
    if type == 'bh':
        for i in range(number_of_shots):
            feedback = {
                'take_back': {},
                'contact_point': {},
                'follow_through': {}
            }

            frameList, feedback, analysis, found = bh_find_tb(frameList, feedback, analysis)
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
                tb_frame_num = len(frameList)
            else:
                tb_frame_num = False
            #print('Frames Left: ' + str(len(frameList)))
            frameList, feedback, analysis, found = bh_find_cp(frameList, feedback, analysis)
            #print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
            frameList, feedback, analysis, found = bh_find_ft(frameList, feedback, analysis)
            #
            #print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1

            # Add Swing Speed
            if tb_frame_num != False:
                analysis['swing_speed'] = analysis['swing_speed'] + (tb_frame_num - len(frameList))
            else:
                number_of_shots -= 1
            frames['Swing ' + str(i)] = feedback

    print(json.dumps(
        frames,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    ))

    # Create Analysis
    right = 0
    total = 0
    for frame in frames:
        print(frame)
        for part in frames[frame]:
            for items in frames[frame][part]:
                total += 1
                print(frames[frame][part][items])
                if frames[frame][part][items] == "Looks good!":
                    right += 1
    print(total, right)
    analysis['technique_accuracy'] = round((right / total) * 125)

    print(analysis['technique_accuracy'])
    print(analysis['number_of_frames'])
    # analysis['technique_accuracy'] = 100 - (analysis['technique_accuracy']/analysis['number_of_frames'] * 8)
    analysis['swing_speed'] = round((analysis['swing_speed']/(analysis['number_of_frames']))/fps,2)
    analysis['consistency'] = 100 - (analysis['restarts'] * 5)
    # frames = Merge(analysis, frames)
    return frames, pics, analysis


# Backhand Analysis
def bh_find_tb_old(frameList, feedback, analysis, fps):
    prev_index = None
    for frame in frameList:
        if frame is None:
            continue
        lmList = frame[0]
        tb_frame = frame[1]
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        left_hip = next((lm for lm in lmList if lm[0] == 23), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 28), None)
        if right_index and left_hip and right_ankle and nose:
            # print(right_hip[1] - right_index[1])
            # print(0.3 * (right_ankle[2] - nose[2]))
            if prev_index == None:
                prev_index = right_index[1]
                # print(prev_index)
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            # Find Takeback
            if right_index[1] - left_hip[1] > (0.2 * (right_ankle[2] - nose[2])) and direction > 0:
                tb_list, img = normalize_pose(lmList, (1024, 1024), 1000,
                                                r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
                                                (255, 0, 0))
                # Analyze take back frame and give feedback
                arrow, feedback = bh_check_take_back(tb_list, lmList, feedback)
                tb_frame = bh_draw_outline(tb_frame, arrow)
                cv2.imwrite('take_back.jpg', tb_frame)
                #print(feedback)
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList))/fps > 3:
                    analysis['restarts'] += 1
                return newframeList, feedback, analysis, True
    return frameList, feedback, analysis, False

def bh_find_tb(frameList, feedback, analysis):
    print('Looking for Takeback')
    prev_index = None

    for frame in frameList:
        if not frame:
            continue

        lmList, tb_frame = frame
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        left_hip = next((lm for lm in lmList if lm[0] == 23), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 28), None)
        if right_index and left_hip and right_ankle and nose:
            if prev_index == None:
                prev_index = right_index[1]
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            # Find Takeback
            if right_index[1] - left_hip[1] > (0.02 * (right_ankle[2] - nose[2])) and direction > 0:
                print('Found Takeback')
                tb_list = normalize_pose(lmList, (1024, 1024), 1000, (255, 0, 0))
                arrow, feedback = bh_check_take_back(tb_list, lmList, feedback)
                tb_frame = bh_draw_outline(tb_frame, arrow)
                pics.append(pic_to_url(tb_frame))
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList)) / 30 > 3:
                    analysis['restarts'] += 1

                return newframeList, feedback, analysis, True
    return frameList, feedback, analysis, False


def bh_find_cp(frameList, feedback, analysis):
    print('Looking for Contact Point')
    prev_index = None
    for frame in frameList:
        if not frame:
            continue

        lmList, cp_frame = frame
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        right_elbow = next((lm for lm in lmList if lm[0] == 14), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 27), None)
        if right_index and right_hip and right_ankle and nose:
            if prev_index == None:
                prev_index = right_index[1]
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            # Find Contact Point
            if abs(right_index[1] - right_hip[1]) < (0.1 * abs(right_ankle[2] - nose[2])) and abs(right_index[2] - right_hip[2]) < abs(0.25 * (right_ankle[2] - nose[2])):
                print('Found Contact Point')
                cp_list = normalize_pose(lmList, (1024, 1024), 1000, (255, 0, 0))
                arrow, feedback = bh_check_contact_point(cp_list, lmList, feedback)
                cp_frame = bh_draw_outline(cp_frame, arrow)
                pics.append(pic_to_url(cp_frame))
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList)) / 30 > 3:
                    analysis['restarts'] += 1

                return newframeList, feedback, analysis, True
    return frameList, feedback, analysis, False

def bh_find_ft(frameList, feedback, analysis):
    print('Looking for Follow Through')
    prev_index = None
    for frame in frameList:
        if not frame:
            continue

        lmList, ft_frame = frame
        left_shoulder = next((lm for lm in lmList if lm[0] == 12), None)
        left_index = next((lm for lm in lmList if lm[0] == 19), None)
        left_elbow = next((lm for lm in lmList if lm[0] == 13), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 27), None)
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        if left_shoulder and left_shoulder and right_ankle and nose:
            if prev_index == None:
                prev_index = right_index[1]
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            # Find Follow Through Point
            if left_shoulder[1] - left_elbow[1] > 0 and abs(left_shoulder[2] - left_elbow[2]) < (0.2 * abs(right_ankle[2] - nose[2])) and abs(left_shoulder[1] - left_index[1]) < (0.2 * abs(right_ankle[2] - nose[2])):
                print('Found Follow Through')
                ft_list = normalize_pose(lmList, (1024, 1024), 1000, (255, 0, 0))
                arrow, feedback = bh_check_follow_through(ft_list, lmList, feedback)
                ft_frame = bh_draw_outline(ft_frame, arrow)
                pics.append(pic_to_url(ft_frame))
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList)) / 30 > 3:
                    analysis['restarts'] += 1

                return newframeList, feedback, analysis, True
    return frameList, feedback, analysis, False

###########################################################################################
###########################################################################################

# Forehand Analysis
def fh_find_tb(frameList, feedback, analysis):
    print('Looking for Takeback')
    prev_index = None

    for frame in frameList:
        if not frame:
            continue

        lmList, tb_frame = frame
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 28), None)

        if right_index and right_hip and right_ankle and nose:
            if prev_index is None:
                prev_index = right_index[1]
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            if (right_hip[1] - right_index[1] > 0.2 * (right_ankle[2] - nose[2])) and direction > 0:
                print('Found Takeback')
                tb_list = normalize_pose(lmList, (1024, 1024), 1000, (255, 0, 0))
                arrow, feedback = fh_check_take_back(tb_list, lmList, feedback)
                tb_frame = fh_draw_outline(tb_frame, arrow)
                pics.append(pic_to_url(tb_frame))
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList)) / 30 > 3:
                    analysis['restarts'] += 1

                return newframeList, feedback, analysis, True

    return frameList, feedback, analysis, False


def fh_find_cp(frameList, feedback, analysis):
    print('Looking for Contact')
    prev_index = None
    for frame in frameList:
        if frame is None:
            continue
        lmList = frame[0]
        cp_frame = frame[1]
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        right_elbow = next((lm for lm in lmList if lm[0] == 14), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 27), None)
        if right_index and right_hip and right_ankle and nose:
            # print(right_hip[1] - right_index[1])
            # print(0.3 * (right_ankle[2] - nose[2]))
            if prev_index == None:
                prev_index = right_index[1]
                # print(prev_index)
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            # Find Contact Point
            if abs(right_index[1] - right_hip[1]) < (0.1 * (right_ankle[2] - nose[2])) and abs(right_index[2] - right_hip[2]) < (0.25 * (right_ankle[2] - nose[2]))and direction > 0:
                print('Found Contact')
                cp_list = normalize_pose(lmList, (1024, 1024), 1000, (255, 0, 0))
                # print(cp_list)
                # Analyze take back frame and give feedback
                arrow, feedback = fh_check_contact_point(cp_list, lmList, feedback)
                cp_frame = fh_draw_outline(cp_frame, arrow)
                cv2.imwrite('contact_point.jpg', cp_frame)
                pics.append(pic_to_url(cp_frame))
                frameList = frameList[frameList.index(frame):]
                return frameList, feedback, analysis, True
    return frameList, feedback, analysis, False

def fh_find_ft(frameList, feedback, analysis):
    print('Looking for Follow')
    prev_index = None
    for frame in frameList:
        if frame is None:
            continue
        lmList = frame[0]
        ft_frame = frame[1]
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_elbow = next((lm for lm in lmList if lm[0] == 14), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 27), None)
        if right_index and right_elbow and right_ankle and nose:
            if prev_index == None:
                prev_index = right_index[1]
                direction = -1
            else:
                direction = right_index[1] - prev_index
                prev_index = right_index[1]

            # Find Follow Point
            if right_elbow[1] - right_index[1] > (0.05 * (right_ankle[2] - nose[2])) and right_elbow[1] - right_hip[1] > 0 and direction > 0:
                print('Found Follow')
                ft_list = normalize_pose(lmList, (1024, 1024), 1000, (255, 0, 0))
                print(ft_list)
                # Analyze take back frame and give feedback
                arrow, feedback = fh_check_follow_through(ft_list, lmList, feedback)
                ft_frame = fh_draw_outline(ft_frame, arrow)
                cv2.imwrite('follow-through.jpg', ft_frame)
                pics.append(pic_to_url(ft_frame))
                frameList = frameList[frameList.index(frame):]
                return frameList, feedback, analysis, True
    return frameList, feedback, analysis, False

# video_path = (r"C:\Users\shahv\PycharmProjects\Slicer\media\fh_ex.MOV")

# analyze_video(video_path, type='fh', number_of_shots=1)
