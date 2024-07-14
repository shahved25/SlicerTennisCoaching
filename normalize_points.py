import numpy as np
import cv2
from cvzone.PoseModule import PoseDetector
import math

"""Normalizes human pose coordinates.

   This function spatially aligns coordinates estimated at different resolutions to the
   same size and location.

   Args:
   pose: A list of (x, y) coordinates of the human pose.
   standard_coordinate: The standard coordinate (x, y) to which the pose will be
     normalized.
   standard_height: The standard height to which the pose will be normalized.

   Returns:
   A list of (x, y) coordinates of the normalized human pose.
   """

def normalize_pose(pose, standard_coordinate, target_height, img, color):
    real_color = color
    img = cv2.imread(str(img))

    standard_height = abs(pose[0][2] - pose[32][2])
    # Calculate the ratio between the standard height and the target height.
    ratio = target_height/standard_height

    # Calculate the distance between the standard coordinates and the resized root joint of the target pose.
    resized_root_joint = (pose[12][1] * ratio, pose[12][2] * ratio)
    dx = round(standard_coordinate[0] - resized_root_joint[0], 0)
    dy = round(standard_coordinate[1] - resized_root_joint[1], 0)

    # Normalize the X coordinates of each target joint.
    normalized_pose = []
    for joint in pose:
        if joint[0] == 12:
            color = (255,0,255)
        else:
            color = real_color
        normalized_joint = (pose.index(joint), int(round((joint[1] * ratio) + dx, 0)), int(round((joint[2] * ratio) + dy, 0)))
        normalized_pose.append(normalized_joint)
        # Unchanged pose
        #cv2.circle(img, (int(joint[1]), int(joint[2])), 10, color, cv2.FILLED)
        # Normalized pose
        #cv2.circle(img, (int(normalized_joint[1]), int(normalized_joint[2])), 10, color, cv2.FILLED)

    return normalized_pose, img

# # Setup
# user_pose = [[0, 537, 229, -157], [1, 541, 217, -143], [2, 545, 216, -143], [3, 548, 216, -144], [4, 530, 218, -138], [5, 527, 218, -138], [6, 524, 218, -138], [7, 555, 218, -41], [8, 522, 223, -10], [9, 545, 239, -115], [10, 532, 241, -106], [11, 590, 260, -29], [12, 505, 298, 85], [13, 618, 338, -80], [14, 538, 373, 85], [15, 634, 414, -220], [16, 601, 412, -12], [17, 644, 433, -270], [18, 618, 430, -44], [19, 640, 433, -290], [20, 626, 426, -67], [21, 634, 427, -231], [22, 619, 419, -22], [23, 595, 431, -80], [24, 541, 441, 80], [25, 578, 560, -194], [26, 518, 565, 47], [27, 678, 641, -53], [28, 549, 684, 133], [29, 699, 638, -44], [30, 567, 701, 134], [31, 687, 698, -139], [32, 501, 713, 30]]
#
# detector = PoseDetector()
# pro = cv2.VideoCapture(r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\pro_bh_contact.mp4')
# if pro.isOpened():
#     ret, proframe = pro.read()
#     pro.release()
#     img_pro = detector.findPose(proframe)
#     pro_pose, bboxInfo = detector.findPosition(img_pro)
#     cv2.imwrite('pro_backhand1.jpg', proframe)
#     pro_height = abs(pro_pose[0][2] - pro_pose[32][2])
# #
# user_pose = [(0, 989, 914), (1, 997, 888), (2, 1003, 886), (3, 1012, 884), (4, 987, 890), (5, 983, 890), (6, 981, 890), (7, 1038, 886), (8, 997, 896), (9, 1005, 935), (10, 991, 937), (11, 1085, 961), (12, 1024, 1024), (13, 1022, 1033), (14, 965, 1175), (15, 977, 1088), (16, 875, 1255), (17, 975, 1088), (18, 844, 1267), (19, 977, 1086), (20, 848, 1265), (21, 979, 1086), (22, 858, 1267), (23, 1110, 1349), (24, 1036, 1365), (25, 1097, 1600), (26, 985, 1606), (27, 1295, 1757), (28, 1050, 1851), (29, 1342, 1755), (30, 1087, 1888), (31, 1318, 1879), (32, 944, 1914)]
#
#
# # Run
# reset = cv2.imread(r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png')
# cv2.imwrite('new_blank.png', reset)
#
# normalized_user_pose, img = normalize_pose(user_pose, (1024,1024), 1000, r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\Solid_white_bordered.svg.png', (255,0,0))
# cv2.imwrite('new_blank.png', img)
#
# normalized_pro_pose, img = normalize_pose(pro_pose, (1024,1024), 1000, r'C:\Users\shahv\.vscode\.venv\Scripts\playground2\new_blank.png', (0,255,0))
# cv2.imwrite('new_blank.png', img)
# print(normalized_pro_pose)
# check_take_back(normalized_user_pose)





#
# def cosine_similarity(normalized_user_pose, normalized_pro_pose):
#     similarity = []
#     for point in zip(normalized_user_pose, normalized_pro_pose):
#         # Calculate dot product
#         dot_product = point[0][0] * point[1][0] + point[0][1] * point[1][1]
#
#         # Calculate magnitudes
#         magnitude1 = math.sqrt(point[0][0] ** 2 + point[0][1] ** 2)
#         magnitude2 = math.sqrt(point[1][0] ** 2 + point[1][1] ** 2)
#
#         # Calculate cosine similarity
#         if magnitude1 == 0 or magnitude2 == 0:
#             return None  # Avoid division by zero
#         else:
#             s = dot_product / (magnitude1 * magnitude2)
#             similarity.append(s)
#
#     return similarity
#
#
# # Example usage
# similarity = cosine_similarity(normalized_user_pose, normalized_pro_pose)
# print("Cosine Similarity:", similarity)
