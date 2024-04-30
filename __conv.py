import cv2
import PySimpleGUI as sg

def conv(kernel, img_path, is_gray):
    if(is_gray):
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    else:  
        img = cv2.imread(img_path)
    
    try:
        if img.shape[0] >= kernel.shape[0] and img.shape[1] >= kernel.shape[1]:
            convolved_img = cv2.filter2D(img, -1, kernel)
            write_path = './result/output.jpg'
            cv2.imwrite(write_path, convolved_img)
            return write_path
        else:
            print("Kernel's size is too small")
            return -1
    except:
        sg.popup("檔名可能有空格或是中文字，請先更改")