from analyze_video import analyze_video
import cv2
import numpy as np
import requests
import tempfile
import os
from cvzone.PoseModule import PoseDetector
import concurrent.futures


def process_frame(frame, detector):
    img = detector.findPose(frame)
    lmList, bboxInfo = detector.findPosition(img)

    # Check for person, add lm locations to frame list
    if bboxInfo:
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each frame in parallel
        futures = [executor.submit(process_frame, frame, detector) for frame in frames]

        for future in concurrent.futures.as_completed(futures):
            frameList.append(future.result())

    print(frameList)
    # frames = analyze_video(frameList, type='fh', number_of_shots=1)
    # print(frames)
    return frameList
#
# # Example usage
# video_url = 'https://user-temporary-uploads.s3.eu-central-1.amazonaws.com/01J52DY8KG1GDNVD7DMZ031S73?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIA5B2PC3KUVAXJDCRQ%2F20240812%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20240812T043559Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEI3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDGV1LWNlbnRyYWwtMSJIMEYCIQCiF162NJoi7P4gc0quNxjEJye%2B3aLYHLdJ4sOFgTw9agIhAIWvmwfRl3nhWaMo8JR6l94QIIScUPv3LeiMFhFDshhzKpsDCIb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQBBoMODk3Mjc3MTU2MDA5IgwnqyCyG%2Beb3FhRQvQq7wI78ys3oJGvGoKtKer0hlqV%2F4VCfxTQeIe4APU3AtipwwOn0PplmcMA2eUSg8L3uXIynsyH3ZQpl2p%2FJHonBISRyzUKKPhZSpEv%2BoSWED1H2O25igB64xWVfhUUY%2BZUmyXpUpLahGN7gobpBcwhtU0zPoLG5fLlm0V1TnSfeMG64e42qgOoCvEqZhBUruX%2FSaSxjq3Hqw2NWaAOle%2BlIvVYCQfnB0oczgUif3yeWUEeCctZhT2aGPC9I6EnnPyuelVTRoEUxN%2FY8hwOlLfaOHFv1muN9jFxudEu2mMpgXnz6mmVVr13ho%2FcoEalArMRBONz6TfhcUD1sXQ8y3eDMrHJkMXlc7%2BtKG8YZEsNVN6G8CKFpS9krIYTs2RWQzgo3BintgecdV1STv6DEaMVjiiZ5qA3JXWmqLZfP%2BKa%2BqEs1BjKZzT%2Bf80Yd9ZG0n5P7BUsoTiK%2BTFOb4GjRNVU45MXM06EOEKkjxn2W%2FWp7bDaMK6i5rUGOpwBmIYmvqx8GPus3mSxaBK5M81KfiGFy7SpR2d4JRIkfTz%2BDwV%2BVEHmR%2Fbszz2UD50YfxFOywAMth4qnogMGfnZrZux6xduaK%2Fq2RJ2F3qXnNzhq0aPlHeHQ0DBRRh8f1z7Tu1AMTygZdmDlb3t1X1TKCMhdhzeRi1ivWI1HjMeSaS9YNt7IEzGz6%2FmbBf%2FU2VtYVBmguFQAZqUuJEk&X-Amz-Signature=8fa0362bf4ae944b14712fdf7a792ea24e069d89ddb92dd0b7887add2f8ad80f&X-Amz-SignedHeaders=host&x-id=GetObject'
# handle_aws_file(video_url)
