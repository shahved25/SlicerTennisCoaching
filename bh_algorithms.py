# File for swing analysis and feedback
import math
import cv2
from normalize_points import normalize_pose

def bh_check_take_back(tb_list, tb_unnorm, feedback):
    pro_bh = [(0, 1017, 898), (1, 1027, 868), (2, 1034, 866), (3, 1042, 862), (4, 1015, 873), (5, 1014, 874), (6, 1013, 875), (7, 1083, 860), (8, 1038, 878), (9, 1044, 912), (10, 1025, 919), (11, 1229, 930), (12, 1024, 1024), (13, 1323, 1082), (14, 1178, 1147), (15, 1444, 1190), (16, 1360, 1199), (17, 1481, 1208), (18, 1417, 1222), (19, 1484, 1204), (20, 1431, 1207), (21, 1469, 1199), (22, 1420, 1200), (23, 1250, 1314), (24, 1100, 1320), (25, 1362, 1584), (26, 998, 1507), (27, 1536, 1814), (28, 997, 1815), (29, 1542, 1843), (30, 1024, 1851), (31, 1573, 1897), (32, 947, 1898)]
    standard_height = int(abs(tb_unnorm[0][2] - tb_unnorm[32][2]))
    arrow = []
    print('TAKE BACK POINT ANALYSIS')
    # Gather body part positions
    right_foot = next((rf for rf in tb_list if rf[0] == 28), None)
    left_foot = next((lf for lf in tb_list if lf[0] == 27), None)
    knee = next((rf for rf in tb_list if rf[0] == 25), None)
    right_hip = next((rf for rf in tb_list if rf[0] == 24), None)
    left_hip = next((lf for lf in tb_list if lf[0] == 23), None)
    right_index = next((ri for ri in tb_list if ri[0] == 20), None)
    left_shoulder = next((ls for ls in tb_list if ls[0] == 11), None)
    right_shoulder = next((rs for rs in tb_list if rs[0] == 12), None)

    # Check if hand is behind hip
    if right_index and left_hip:
        print(right_index, pro_bh[20])
        distance = right_index[1] - pro_bh[20][1]
        if distance > -100:
            print('- Racquet position looks good')
            feedback['take_back']['Hand Position'] = 'Looks good!'
        else:
            print('- Bring your racquet back farther')
            feedback['take_back']['Hand'] = 'Bring your acquet back farther'
            arrow.append([(tb_unnorm[20][1], tb_unnorm[20][2]), (int(tb_unnorm[20][1] + (standard_height *.1)), tb_unnorm[20][2])])

    # Check right foot
    if right_foot:
        distance_rf = abs(right_foot[1] - pro_bh[28][1])
        if distance_rf < 100:
            print('- Right foot is well positioned')
            feedback['take_back']['Right Foot'] = 'Looks good!'
        else:
            print('- Bring the right foot farther out')
            feedback['take_back']['Right Foot'] = 'Bring the right foot forward'
            arrow.append([(tb_unnorm[32][1], tb_unnorm[32][2]), (int(tb_unnorm[32][1] - (standard_height *.1)), tb_unnorm[32][2])])

    # Check left foot
    if left_foot:
        distance = abs(left_foot[1] - pro_bh[27][1])
        if distance < 160:
            print('- Left foot is well positioned')
            feedback['take_back']['Left Foot'] = 'Looks good!'
        else:
            print('- Bring the left foot farther back')
            feedback['take_back']['Left Foot'] = 'Bring the left foot farther back'
            arrow.append([(tb_unnorm[31][1], tb_unnorm[31][2]), (int(tb_unnorm[31][1] + (standard_height *.1)), tb_unnorm[31][2])])

    # Check if hips are apart
    if right_hip and left_hip:
        distance_hip = abs(right_hip[1] - left_hip[1])
        if distance_hip > 150:
            print('- Hips are well aligned')
            feedback['take_back']['Hips Alignment'] = 'Looks good!'
        else:
            print('- Turn your hips towards the left')
            feedback['take_back']['Hips'] = 'Turn your hips towards the left'
            arrow.append([(tb_unnorm[24][1], tb_unnorm[24][2]), (int(tb_unnorm[24][1] + (standard_height *.1)), tb_unnorm[24][2])])

    # Check if shoulders are aligned
    if right_shoulder and left_shoulder:
        distance_shoulder = abs(right_shoulder[2] - left_shoulder[2])
        if distance_shoulder < 100:
            print('- Shoulders are well balanced')
            feedback['take_back']['Shoulder Balance'] = 'Looks good!'
        else:
            print('- Keep your shoulders balanced')
            feedback['take_back']['Shoulder Balance'] = 'Keep your shoulders balanced'
            arrow.append([(tb_unnorm[12][1], tb_unnorm[12][2]), (tb_unnorm[12][1], int(tb_unnorm[12][2] + (standard_height *.1)))])

    # Check if shoulders are apart
    if right_shoulder and left_shoulder:
        distance_shoulder = abs(right_shoulder[1] - left_shoulder[1])
        if distance_shoulder > 160:
            print('- Shoulders are well aligned')
            feedback['take_back']['Shoulder Alignment'] = 'Looks good!'
        else:
            print('- Keep your shoulders in-line with the court')
            feedback['take_back']['Shoulder Alignment'] = 'Keep your shoulders in-line with the court'
            arrow.append([(tb_unnorm[12][1], tb_unnorm[12][2]), (int(tb_unnorm[12][1] + (standard_height *.1)), tb_unnorm[12][2])])

    return arrow, feedback

def bh_check_contact_point(cp_list, c_unnorm, feedback):
    pro_bh = [(0, 1018, 962), (1, 1024, 932), (2, 1032, 930), (3, 1041, 927), (4, 1010, 932), (5, 1006, 931), (6, 1004, 930), (7, 1075, 921), (8, 1026, 925), (9, 1043, 981), (10, 1025, 982), (11, 1163, 1044), (12, 1024, 1024), (13, 1006, 1215), (14, 912, 1154), (15, 852, 1320), (16, 807, 1300), (17, 819, 1355), (18, 780, 1341), (19, 810, 1351), (20, 785, 1341), (21, 820, 1341), (22, 797, 1331), (23, 1220, 1405), (24, 1108, 1406), (25, 1288, 1640), (26, 1056, 1631), (27, 1485, 1800), (28, 1157, 1883), (29, 1507, 1799), (30, 1194, 1924), (31, 1539, 1910), (32, 1067, 1962)]
    print('CONTACT POINT ANALYSIS')
    standard_height = int(abs(c_unnorm[0][2] - c_unnorm[32][2]))
    arrow = []
    # Gather body part positions
    right_foot = next((rf for rf in cp_list if rf[0] == 28), None)
    left_foot = next((lf for lf in cp_list if lf[0] == 27), None)
    left_knee = next((rf for rf in cp_list if rf[0] == 25), None)
    right_hip = next((rf for rf in cp_list if rf[0] == 24), None)
    left_hip = next((lf for lf in cp_list if lf[0] == 23), None)
    right_index = next((ri for ri in cp_list if ri[0] == 20), None)
    left_shoulder = next((ls for ls in cp_list if ls[0] == 11), None)
    right_shoulder = next((rs for rs in cp_list if rs[0] == 12), None)
    right_elbow = next((re for re in cp_list if re[0] == 14), None)

    # Check if right foot  are in the correct position
    if right_foot:
        distance_feet = abs(right_foot[1] - pro_bh[32][1])
        if distance_feet < 80:
            print('- Feet are well positioned')
            feedback['contact_point']['Right Foot'] = 'Looks good!'
        else:
            print('- Bring your right foot forward')
            feedback['contact_point']['Right Foot'] = 'Bring your right foot forward'
            arrow.append([(c_unnorm[32][1], c_unnorm[32][2]), (int(c_unnorm[32][1] - (standard_height *.1)), c_unnorm[32][2])])


    # Check if left foot  are in the correct position
    if left_foot:
        distance_feet = abs(left_foot[1] - pro_bh[31][1])
        if distance_feet < 80:
            print('- Feet are well positioned')
            feedback['contact_point']['Left Foot'] = 'Looks good!'
        else:
            print('- Bring your left foot back')
            feedback['contact_point']['Left Foot'] = 'Bring your left foot back'
            arrow.append([(c_unnorm[31][1], c_unnorm[31][2]), (int(c_unnorm[31][1] + (standard_height *.1)), c_unnorm[31][2])])


    # Check if hips are aligned properly
    if right_hip and left_hip:
        distance_hip = abs(right_hip[1] - left_hip[1])
        if distance_hip > 100:
            print('- Hips are properly aligned at the contact point')
            feedback['contact_point']['Hips'] = 'Looks good!'
        else:
            print('- Ensure your hips are aligned towards the target during the contact point')
            feedback['contact_point']['Hips'] = 'Ensure your hips are aligned'
            arrow.append([(c_unnorm[24][1], c_unnorm[24][2]), (int(c_unnorm[24][1] - (standard_height *.1)), c_unnorm[24][2])])


    # Check if shoulders are aligned properly
    if right_shoulder and left_shoulder:
        distance_shoulder = abs(right_shoulder[2] - left_shoulder[2])
        if distance_shoulder < 100:
            print('- Shoulders are well aligned at the contact point')
            feedback['contact_point']['Shoulders'] = 'Looks good!'
        else:
            print('- Maintain proper shoulder alignment')
            feedback['contact_point']['Shoulders'] = 'Maintain proper shoulder alignment'
            arrow.append([(c_unnorm[12][1], c_unnorm[12][2]), (c_unnorm[12][1], int(c_unnorm[12][2] - (standard_height *.1)))])


    # Check angle between shoulder, arm, and elbow
    if right_shoulder and right_elbow and right_index:
        point1 = right_shoulder[1:]
        point2 = right_elbow[1:]
        point3 = right_index[1:]
        vector1 = (point1[0] - point2[0], point1[1] - point2[1])
        vector2 = (point3[0] - point2[0], point3[1] - point2[1])

        # Calculate dot product and magnitudes
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.hypot(*vector1)
        magnitude2 = math.hypot(*vector2)

        # Calculate angle in radians and convert to degrees
        angle_rad = math.acos(dot_product / (magnitude1 * magnitude2))
        angle_deg = math.degrees(angle_rad)

        # Check if angle is too small
        if angle_deg < 140 or angle_deg > 220:  # Adjust threshold as needed
            print('- Straighten your arm for better form during the contact point')
            feedback['contact_point']['Arm Angle'] = 'Straighten your arm'
            arrow.append([(c_unnorm[12][1], c_unnorm[12][2]), (c_unnorm[16][1], c_unnorm[16][2])])

        else:
            print('- Arm angle looks good at the contact point')
            feedback['contact_point']['Arm Angle'] = 'Looks good!'

    return arrow, feedback

def bh_check_follow_through(ft_list, f_unnorm, feedback):
    pro_bh = [(0, 913, 924), (1, 923, 902), (2, 925, 902), (3, 927, 902), (4, 923, 904), (5, 927, 904), (6, 931, 904), (7, 946, 908), (8, 956, 908), (9, 921, 941), (10, 923, 943), (11, 962, 982), (12, 1024, 1024), (13, 904, 1017), (14, 1055, 1102), (15, 888, 1019), (16, 1053, 1108), (17, 880, 1028), (18, 1059, 1112), (19, 896, 1028), (20, 1059, 1104), (21, 900, 1028), (22, 1051, 1102), (23, 991, 1333), (24, 976, 1355), (25, 1075, 1586), (26, 954, 1609), (27, 1244, 1778), (28, 995, 1867), (29, 1290, 1784), (30, 1030, 1902), (31, 1240, 1891), (32, 902, 1924)]
    arrow = []
    standard_height = int(abs(f_unnorm[0][2] - f_unnorm[32][2]))

    print('FOLLOW-THROUGH POINT ANALYSIS')
    # Gather body part positions
    right_foot = next((rf for rf in ft_list if rf[0] == 28), None)
    left_foot = next((lf for lf in ft_list if lf[0] == 27), None)
    left_knee = next((lk for lk in ft_list if lk[0] == 25), None)
    right_hip = next((rf for rf in ft_list if rf[0] == 24), None)
    left_hip = next((lf for lf in ft_list if lf[0] == 23), None)
    left_ankle = next((ri for ri in ft_list if ri[0] == 27), None)
    left_toes = next((ls for ls in ft_list if ls[0] == 31), None)

    if right_foot:
        distance_feet = abs(right_foot[1] - pro_bh[32][1])
        if distance_feet < 80:
            print('- Feet are well positioned')
            feedback['follow_through']['Right Foot'] = 'Looks good!'
        else:
            print('- Bring your right foot forward')
            arrow.append([(f_unnorm[32][1], f_unnorm[32][2]), (int(f_unnorm[32][1] - (standard_height *.1)), f_unnorm[32][2])])
            feedback['follow_through']['Right Foot'] = 'Bring your right foot forward'

    # Check if left foot  are in the correct position
    if left_foot:
        distance_feet = abs(left_foot[1] - pro_bh[31][1])
        if distance_feet < 80:
            print('- Feet are well positioned')
            feedback['follow_through']['Left Foot'] = 'Looks good!'
        else:
            print('- Bring your left foot back')
            arrow.append([(f_unnorm[31][1], f_unnorm[31][2]), (int(f_unnorm[31][1] + (standard_height *.1)), f_unnorm[31][2])])
            feedback['follow_through']['Left Foot'] = 'Bring your left foot back'


    # Check if hips are aligned properly
    if right_hip and left_hip:
        distance_hip = abs(right_hip[1] - left_hip[1])
        if distance_hip > 100:
            print('- Hips are properly aligned at the contact point')
            feedback['follow_through']['Hips'] = 'Looks good!'
        else:
            print('- Ensure your hips are aligned towards the target during the contact point')
            arrow.append([(f_unnorm[24][1], f_unnorm[24][2]), (int(f_unnorm[24][1] - (standard_height *.1)), f_unnorm[24][2])])
            feedback['follow_through']['Hips'] = 'Ensure your hips are aligned towards the target'


    # Check angle between left_ankle, left_knee, and left_hip
    if left_ankle and left_knee and left_hip:
        point1 = left_hip[1:]
        point2 = left_knee[1:]
        point3 = left_ankle[1:]
        vector1 = (point1[0] - point2[0], point1[1] - point2[1])
        vector2 = (point3[0] - point2[0], point3[1] - point2[1])

        # Calculate dot product and magnitudes
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.hypot(*vector1)
        magnitude2 = math.hypot(*vector2)

        # Calculate angle in radians and convert to degrees
        angle_rad = math.acos(dot_product / (magnitude1 * magnitude2))
        angle_deg = math.degrees(angle_rad)
        #print('leg leg angle = ' + str(angle_deg))
        # Check if angle is too small
        if angle_deg > 160:  # Adjust threshold as needed
            print('- Left leg angle looks good')
            feedback['follow_through']['Left Leg Angle'] = 'Looks good!'

        else:
            print('- Straighten your left leg')
            feedback['follow_through']['Left Leg Angle'] = 'Straighten your left leg'
            arrow.append([(f_unnorm[24][1], f_unnorm[24][2]), (f_unnorm[28][1], f_unnorm[28][2])])


    # Check angle between left_toes, left_ankle, and left_knee
    if left_ankle and left_knee and left_toes:
        point1 = left_toes[1:]
        point2 = left_ankle[1:]
        point3 = left_knee[1:]
        vector1 = (point1[0] - point2[0], point1[1] - point2[1])
        vector2 = (point3[0] - point2[0], point3[1] - point2[1])

        # Calculate dot product and magnitudes
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.hypot(*vector1)
        magnitude2 = math.hypot(*vector2)

        # Calculate angle in radians and convert to degrees
        angle_rad = math.acos(dot_product / (magnitude1 * magnitude2))
        angle_deg = math.degrees(angle_rad)
        #print('left ankle angle = ' + str(angle_deg))
        # Check if angle is too small
        if angle_deg > 130:  # Adjust threshold as needed
            print('- Extension of the toes looks good')
            feedback['follow_through']['Left Ankle Angle'] = 'Looks good!'
        else:
            print('- Keep your left foot on its toes')
            feedback['follow_through']['Left Ankle Angle'] = 'Keep your left foot on its toes'
            arrow.append([(f_unnorm[29][1], f_unnorm[29][2]), (f_unnorm[29][1], int(f_unnorm[29][2] - (standard_height *.1)))])

    return arrow, feedback


def bh_draw_outline(img, arrow):
    if arrow:
        for a in arrow:
            cv2.arrowedLine(img, a[0], a[1], (122,212,245), 5)
    return img