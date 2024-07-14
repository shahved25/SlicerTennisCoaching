import cv2
from cvzone.PoseModule import PoseDetector
from fh_algorithms import *
from bh_algorithms import *
from normalize_points import normalize_pose
import math, base64, json

def myFunc(e):
    return e[0]

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def analyze_video(video_path, type, number_of_shots):
    detector = PoseDetector()
    frameList = []
    cap = cv2.VideoCapture(video_path)
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    print('FPS: ' + str(fps))
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        img = detector.findPose(frame)
        lmList, bboxInfo = detector.findPosition(img)

        # Check for person, add lm locations to frame list
        if bboxInfo:
            frameList.append((lmList, frame))

    cap.release()
    t_time = len(frames)
    print('Frames: ' + str(t_time))

    analysis = {
        'technique_accuracy': 0,
        'consistency': 0,
        'swing_speed': 0,
        'restarts': 0,
        'number_of_frames' : 0
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

            frameList, feedback, analysis, found = fh_find_tb(frameList, feedback, analysis, fps)
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
                tb_frame_num = len(frameList)
            else:
                tb_frame_num = False
            print('Frames Left: ' + str(len(frameList)))
            frameList, feedback, analysis, found = fh_find_cp(frameList, feedback, analysis)
            print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
            frameList, feedback, analysis, found = fh_find_ft(frameList, feedback, analysis)
            print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1

            # Add Swing Speed
            if tb_frame_num != False:
                analysis['swing_speed'] = analysis['swing_speed'] + (tb_frame_num - len(frameList))
            frames[str(i)] = feedback

    # Main Loop for Forehand
    if type == 'bh':
        for i in range(number_of_shots):
            feedback = {
                'take_back': {},
                'contact_point': {},
                'follow_through': {}
            }

            frameList, feedback, analysis, found = bh_find_tb(frameList, feedback, analysis, fps)
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
                tb_frame_num = len(frameList)
            else:
                tb_frame_num = False
            print('Frames Left: ' + str(len(frameList)))
            frameList, feedback, analysis, found = bh_find_cp(frameList, feedback, analysis)
            print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1
            frameList, feedback, analysis, found = bh_find_ft(frameList, feedback, analysis)
            print('Frames Left: ' + str(len(frameList)))
            if found == True:
                analysis['number_of_frames'] = analysis['number_of_frames'] + 1

            # Add Swing Speed
            if tb_frame_num != False:
                analysis['swing_speed'] = analysis['swing_speed'] + (tb_frame_num - len(frameList))
            frames[str(i)] = feedback

    # Create Analysis
    # print(analysis['technique_accuracy'])
    # print(analysis['number_of_frames'])
    analysis['technique_accuracy'] = 100 - (analysis['technique_accuracy']/analysis['number_of_frames'] * 8)
    analysis['swing_speed'] = (analysis['swing_speed']/(analysis['number_of_frames']/3))/fps
    analysis['consistency'] = 100 - (analysis['restarts'] * 5)
    frames = Merge(analysis, frames)

    print(json.dumps(
        frames,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    ))

    return frames


# Backhand Analysis
def bh_find_tb(frameList, feedback, analysis, fps):
    prev_index = None
    for frame in frameList:
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
                analysis['technique_accuracy'] = analysis['technique_accuracy'] + len(feedback['take_back'])
                tb_frame = bh_draw_outline(tb_frame, arrow)
                cv2.imwrite('take_back.jpg', tb_frame)
                #print(feedback)
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList))/fps > 3:
                    analysis['restarts'] += 1
                return newframeList, feedback, analysis, True
    return frameList, feedback, analysis, False

def bh_find_cp(frameList, feedback, analysis):
    prev_index = None
    for frame in frameList:
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
                cp_list, img = normalize_pose(lmList, (1024, 1024), 1000,
                                                r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
                                                (255, 0, 0))
                # Analyze take back frame and give feedback
                arrow, feedback = bh_check_contact_point(cp_list, lmList, feedback)
                analysis['technique_accuracy'] = analysis['technique_accuracy'] + len(feedback['contact_point'])
                cp_frame = bh_draw_outline(cp_frame, arrow)
                cv2.imwrite('contact_point.jpg', cp_frame)
                #print(feedback)
                frameList = frameList[frameList.index(frame):]
                return frameList, feedback, analysis, True
    return frameList, feedback, analysis, False

def bh_find_ft(frameList, feedback, analysis):
    prev_index = None
    for frame in frameList:
        lmList = frame[0]
        ft_frame = frame[1]
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_elbow = next((lm for lm in lmList if lm[0] == 14), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 27), None)
        if right_index and right_elbow and right_ankle and nose:
            # print(right_elbow[1] - right_index[1])
            # print(0.05 * (right_ankle[2] - nose[2]))
            if prev_index == None:
                prev_index = right_index[1]
                # print(prev_index)
                direction = -1
            else:
                direction = right_index[1] - prev_index
                #print('direction: ' + str(direction))
                prev_index = right_index[1]

            # Find Follow Through Point
            if right_elbow[1] - right_index[1] > (0.05 * (right_ankle[2] - nose[2])) and right_elbow[1] - right_hip[1] > 0 and direction > 0:
                ft_list, img = normalize_pose(lmList, (1024, 1024), 1000,
                                                r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
                                                (255, 0, 0))
                # Analyze take back frame and give feedback
                arrow, feedback = bh_check_follow_through(ft_list, lmList, feedback)
                analysis['technique_accuracy'] = analysis['technique_accuracy'] + len(feedback['follow_through'])
                ft_frame = bh_draw_outline(ft_frame, arrow)
                cv2.imwrite('follow-through.jpg', ft_frame)
                frameList = frameList[frameList.index(frame):]
                return frameList, feedback, analysis, True
    return frameList, feedback, analysis, False

###########################################################################################
###########################################################################################

# Forehand Analysis
def fh_find_tb(frameList, feedback, analysis, fps):
    prev_index = None
    for frame in frameList:
        lmList = frame[0]
        tb_frame = frame[1]
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 28), None)
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

            # Find Takeback
            if right_hip[1] - right_index[1] > (0.2 * (right_ankle[2] - nose[2])) and direction > 0:
                tb_list, img = normalize_pose(lmList, (1024, 1024), 1000,
                                                r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
                                                (255, 0, 0))
                # Analyze take back frame and give feedback
                arrow, feedback = fh_check_take_back(tb_list, lmList, feedback)
                analysis['technique_accuracy'] = analysis['technique_accuracy'] + len(feedback['take_back'])
                tb_frame = fh_draw_outline(tb_frame, arrow)
                cv2.imwrite('take_back.jpg', tb_frame)
                #print(feedback)
                newframeList = frameList[frameList.index(frame):]
                if (len(frameList) - len(newframeList))/fps > 3:
                    analysis['restarts'] += 1
                return newframeList, feedback, analysis, True
    return frameList, feedback, analysis, False

def fh_find_cp(frameList, feedback, analysis):
    prev_index = None
    for frame in frameList:
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
                cp_list, img = normalize_pose(lmList, (1024, 1024), 1000,
                                                r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
                                                (255, 0, 0))
                # Analyze take back frame and give feedback
                arrow, feedback = fh_check_contact_point(cp_list, lmList, feedback)
                analysis['technique_accuracy'] = analysis['technique_accuracy'] + len(feedback['contact_point'])
                cp_frame = fh_draw_outline(cp_frame, arrow)
                cv2.imwrite('contact_point.jpg', cp_frame)
                #print(feedback)
                frameList = frameList[frameList.index(frame):]
                return frameList, feedback, analysis, True
    return frameList, feedback, analysis, False

def fh_find_ft(frameList, feedback, analysis):
    prev_index = None
    for frame in frameList:
        lmList = frame[0]
        ft_frame = frame[1]
        right_index = next((lm for lm in lmList if lm[0] == 20), None)
        right_elbow = next((lm for lm in lmList if lm[0] == 14), None)
        right_hip = next((lm for lm in lmList if lm[0] == 24), None)
        nose = next((lm for lm in lmList if lm[0] == 0), None)
        right_ankle = next((lm for lm in lmList if lm[0] == 27), None)
        if right_index and right_elbow and right_ankle and nose:
            # print(right_elbow[1] - right_index[1])
            # print(0.05 * (right_ankle[2] - nose[2]))
            if prev_index == None:
                prev_index = right_index[1]
                # print(prev_index)
                direction = -1
            else:
                direction = right_index[1] - prev_index
                #print('direction: ' + str(direction))
                prev_index = right_index[1]

            # Find Contact Point
            if right_elbow[1] - right_index[1] > (0.05 * (right_ankle[2] - nose[2])) and right_elbow[1] - right_hip[1] > 0 and direction > 0:
                ft_list, img = normalize_pose(lmList, (1024, 1024), 1000,
                                                r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
                                                (255, 0, 0))
                # Analyze take back frame and give feedback
                arrow, feedback = fh_check_follow_through(ft_list, lmList, feedback)
                analysis['technique_accuracy'] = analysis['technique_accuracy'] + len(feedback['follow_through'])
                ft_frame = fh_draw_outline(ft_frame, arrow)
                cv2.imwrite('follow-through.jpg', ft_frame)
                #print(feedback)
                frameList = frameList[frameList.index(frame):]
                return frameList, feedback, analysis, True
    return frameList, feedback, analysis, False
#
# video_path = (r'C:\Users\shahv\PycharmProjects\kivy-app\media\bh_ex_3shots (2).mov')
#
# analyze_video(video_path, type='bh', number_of_shots=3)
#
#


# # else:
            #     continue
            # if distance < (0.02 * measure):
            #     tb_frame = frame
            #
            #     # Normalize points
            #     tb_list, img = normalize_pose(lmList, (1024, 1024), 1000,
            #                                   r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png',
            #                                   (255, 0, 0))
            #     # Analyze take back frame and give feedback
            #     arrow, feedback = fh_check_take_back(tb_list, lmList, feedback)
            #     tb_frame = fh_draw_outline(tb_frame, arrow)
            #     cv2.imwrite('take_back.jpg', tb_frame)
#             #     return feedback
# tb_dis.append((right_index[1] - right_hip[1], lmList, frame))
#     #         cp_dis.append((abs(right_hip[1] - right_index[1]),lmList, frame))
    #         ft_dis.append((abs(right_shoulder[1]-right_index[1]), lmList, frame))
    #
    # tb_dis.sort(key=myFunc)
    # tb_frames = tb_dis[:number_of_shots]
    # cv2.imwrite('take_back.jpg', tb_frames[0][2])
