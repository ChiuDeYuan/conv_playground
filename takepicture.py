import cv2
import numpy as np
import ctypes

def pic():
    user32 = ctypes.windll.user32
    screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    output_image = np.zeros((screen_height,screen_width,3),dtype='uint8')

    cap = cv2.VideoCapture(0)

    cv2.namedWindow("press space to take a picture", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("press space to take a picture",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    
    while True:
        ret, frame = cap.read()
        frame_height, frame_width, _ = frame.shape
        frh = frame_height//2
        frw = frame_width//2
        frame = cv2.flip(frame, 1)
        output_image[screen_height//2-frh : screen_height//2-frh+frame_height, screen_width//2-frw : screen_width//2-frw+frame_width] = frame

        cv2.putText(output_image,'Press space to take a picture',(0,screen_height-50),cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,255),1,cv2.LINE_AA)
        cv2.imshow('press space to take a picture',output_image)

        if cv2.waitKey(1) == ord(' '):
            filename = './picture/thepicture.jpg'
            cv2.imwrite(filename,frame)
            cap.release()
            cv2.destroyAllWindows()
            return