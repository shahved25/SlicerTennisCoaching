import cv2
import numpy as np
import requests
import tempfile
from cvzone.PoseModule import PoseDetector
import os


def process_frame(frame, detector):
    img = detector.findPose(frame)
    lmList, bboxInfo = detector.findPosition(img)

    # Check for person, add lm locations to frame list
    if bboxInfo:
        # for i in lmList:
        #     i.insert(0, lmList.index(i))

        return (lmList, frame)

    else:
        return None


def handle_aws_file(video_url):
    detector = PoseDetector()
    frameList = []

    session = requests.Session()

    response = session.get(video_url, stream=True)
    if response.status_code != 200:
        print("Error: Unable to stream video.")
        return

    bytes_stream = b''
    for chunk in response.iter_content(chunk_size=1024):
        bytes_stream += chunk

    np_array = np.frombuffer(bytes_stream, np.uint8)

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(np_array)
        tmp_file_path = tmp_file.name

    cap = cv2.VideoCapture(tmp_file_path)
    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return False

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    os.remove(tmp_file_path)

    # Process frames sequentially instead of in parallel
    for frame in frames:
        result = process_frame(frame, detector)
        if result:
            frameList.append(result)

    # print(len(frameList))
    # frames = analyze_video(frameList, type='fh', number_of_shots=1)
    #print(frames)
    return frameList

# # Example usage
# video_url = 'https://user-temporary-uploads.s3.eu-central-1.amazonaws.com/01J7VRJQ255KHMMXN9CZH9FV5D?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIA5B2PC3KUVMB5K7SM%2F20240915%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20240915T211420Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEM3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDGV1LWNlbnRyYWwtMSJIMEYCIQDvCrHNk%2FEkf7Rzb2PjrawG6Hvqtdct%2BOUbZGlBy91c5QIhAPJwYaDb5rA6gbSFr1K03mJzjHIA%2B5dJeM0R%2FlX%2BniyyKpsDCPb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQBBoMODk3Mjc3MTU2MDA5IgxQ6S1rs8wUdiMS1Ggq7wK8jOqu4wGliJSyMLhZcM7DJe4GTNES6t8Ve1B%2FblassQLRgnCOCAmzJ%2FNzBZz6WOBYdz3OjI0Ial0EsKLqf%2F9oCwDBWx2GTuklvf9PQ21Tih1v6%2FznK8WHYqQwK994k1yZKWRZnkqtCfbmnCncE86qazf87cuXv6neKGqhS5Id4o%2FNSE%2F31aa8j6lClwpJwdzwLoJQ5luSXt0OCyOFsctT03k9y9AVDGa8OqGJbZQtdi85R%2FlfmSzsOv7gsrZTIDZ4TVQW%2BucWsIyGP67hbjzE2bBfY3XZHCeyQPM5Sk3%2BoTbnmVJP4MDnTXe0MoJJgZuVtfWHOY56oEEhKKCB41oZ6e264G8KC8R0czNe%2B8Jyg9w%2F3aD64MY5mcJ0KerPsSJaGKWoGvx8ujISBt1NmCePLk5yHkku56SjTwuYfC%2BhTDKwjWuFFmlChQvOHTsJdEKYT6tJP%2B8w7LD4Muxm7RRlR9Fw%2FRsmNs8hdcfA5BIQMOiXnbcGOpwBJMqauEtmIJqvJgKM%2B6wAFmjA8dWEzaof4geo3FzlNTT4pjDG5Bd5hSMgGRDEBh613c3FpyskdlVLlOMTjxmDuVyXnTczQz5%2FE54pJueDerZnfdSRP8cURCrU%2FlqWQKAXoi%2Fj1BDZEmBRkFCMSSDn32tfcgdpHsfeJOzkDvzroa4vTX%2F03Rn2aeWI3WuEHf5lEmEE8yPoPN%2BVCKJZ&X-Amz-Signature=8786a7c3287c3afa4c105147575881d4bac79475203af44a7a477b97d46b6cce&X-Amz-SignedHeaders=host&x-id=GetObject'
# handle_aws_file(video_url)
