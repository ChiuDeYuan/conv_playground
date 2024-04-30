
from PIL import Image,ImageTk
import PySimpleGUI as sg
import numpy as np
import cv2
import ctypes

import __conv
import takepicture

##################################

user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

##################################

kernel = [np.array([[1]]),
          np.array([[1,1,1],[1,-7,1],[1,1,1]]),
          np.array([[0,1,1,2,2,2,1,1,0],[1,2,4,5,5,5,4,2,1],[1,4,5,3,0,3,5,4,1],[2,5,3,-12,-24,-12,3,5,2],[2,5,0,-24,-40,-24,0,5,2],[2,5,3,-12,-24,-12,3,5,2],[1,4,5,3,0,3,4,4,1],[1,2,4,5,5,5,4,2,1],[0,1,1,2,2,2,1,1,0]]),
          np.array([[1,1,1],[0,0,0],[-1,-1,-1]]),
          np.array([[1]]),
          np.array([[1]]),
          np.array([[-1,-2,-1],[-2,13,-2],[-1,-2,-1]]),
          np.array([[100,0,0,0,-100],[0,-100,0,100,0],[0,0,1,0,0],[0,-100,0,100,0],[100,0,0,0,-100]]),
          np.array([[1/81 for _ in range(9)] for __ in range(9)]),
          ]
kernel_now = 0
gray_switch = False

############## GUI ################
sg.theme('LightBlue6')
layout = [
        [sg.Push(),
         sg.Text('卷積處理圖片', size=(20, 1), justification='c', font=('Arial Bold', 32)),
         sg.Push()],
        [sg.Push(),sg.Push(),sg.Push(),
         sg.Image(key="-IMAGE-",size=(350,500),),
         sg.Image(key="-ARROW-",),
         sg.Graph(canvas_size=(330, 330), graph_bottom_left=(0, 0), graph_top_right=(330, 330), key='graph'),
         sg.Image(key="-IMAGE2-",size=(350,500),),
         sg.Push(),sg.Push(),sg.Push(),],
        [sg.Push(),
         sg.Text('灰階 :', font=('sens', 20)),
          sg.Radio('Yes', 'gray', enable_events=True, key='gray_true', font=('sens', 20)),
          sg.Radio('No', 'gray', enable_events=True, key='gray_false', default=True, font=('sens', 20)),
          sg.Push(),],
        [ sg.Push(),
          sg.Text('卷積核 :', font=('sens', 20)),
          sg.Radio('原圖', 'kernel', enable_events=True, key='ori', default=True, font=('sens', 20)),
          sg.Radio('邊緣1', 'kernel', enable_events=True, key='k1', font=('sens', 20)),
          sg.Radio('邊緣2', 'kernel', enable_events=True, key='k3', font=('sens', 20)),
          sg.Radio('拉普拉斯算子', 'kernel', enable_events=True, key='k2', font=('sens', 20)),
          sg.Radio('銳利化', 'kernel', enable_events=True, key='k6', font=('sens', 20)),
          sg.Radio('?', 'kernel', enable_events=True, key='k7', font=('sens', 20)),
          sg.Radio('模糊', 'kernel', enable_events=True, key='k8', font=('sens', 20)),
          sg.Radio('自定義3X3', 'kernel', enable_events=True, key='k5', font=('sens', 20)),
          sg.Radio('自定義5X5', 'kernel', enable_events=True, key='k4', font=('sens', 20)),
          sg.Push(),],
        [sg.Text('',size=(1,2)),],
        [sg.FileBrowse("選擇檔案",target='-GETFILE-', key='-GETFILE-',
         enable_events=True,size=(15,2), font=('sans', 20)),
         sg.Push(),
         sg.Button('拍照', font=('sans', 20), enable_events=True, key='-TAKEPIC-', size=(15,2)),
         sg.Push(),
         sg.Button('OK!', font=('sans', 20), enable_events=True, key='-DOWNLOAD-', size=(15,2))],
    ]

#window = sg.Window('Convolution', layout)
window = sg.Window('Convolution', layout).Finalize()

window['graph'].draw_image(filename='./assets/arrow_rs.png', location=(-13, 250),)
window['graph'].draw_line(point_from=(30,30), point_to=(30,280))
window['graph'].draw_line(point_from=(280,30), point_to=(280,280))
window['graph'].draw_line(point_from=(30,280), point_to=(280,280))
window['graph'].draw_line(point_from=(30,30), point_to=(280,30))
window['graph'].draw_rectangle((30, 30), (280, 280), fill_color='white', line_color='#67b0d1')

window.Maximize()
#################################################

################## Draw Kernel ##################

def draw_kernel(kernel):
    window['graph'].draw_rectangle((30, 30), (280, 280), fill_color='white', line_color='#67b0d1')
    kernel_size = kernel.shape[1]
    padding = 250/kernel_size
    for i in range(1,kernel_size+1):
        window['graph'].draw_line(point_from=(30+i*padding,30), point_to=(30+i*padding,280), color='#67b0d1')
        window['graph'].draw_line(point_from=(30,30+i*padding), point_to=(280,30+i*padding), color='#67b0d1')

    for i,text_i in zip(range(kernel_size),kernel):
        for j,text_j in zip(range(kernel_size),text_i):
            window['graph'].draw_text(round(text_j, 3), font=('sens', 11+int(padding/10)-len(str(round(text_j, 3)))), location=(30+(j+1/2)*padding,280-(i+1/2)*padding))

#################################################

############## Customize Kernel #################

def str_to_float(tar):
    print(tar)
    if tar == '':
        return 1
    elif '/' in tar:
        tar = tar.split('/')
        if(tar[1]==''):
            tar[1] = '1'
        try:
            return float(int(tar[0])/int(tar[1]))
        except:
            return 1
    else:
        try:
            if '.' in tar:
                return float(tar)
            else:
                return int(tar)
        except:
            return 1

def design_kernel_5X5():
    l1 = sg.Text('自訂kernel!!!', key='-OUT-', font=('Arial Bold', 16), expand_x=True, justification='center', size=(10, 2))
    l2 = sg.Text('OR', font=16, expand_x=False, justification='center', size=(6, 1))
    l3 = sg.Text('全部填充', expand_x=False, justification='center', size=(11, 1))
    l4 = sg.Text('', expand_x=False, justification='center')
    t1 = sg.Input('', key='-INPUT1-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t2 = sg.Input('', key='-INPUT2-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t3 = sg.Input('', key='-INPUT3-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t4 = sg.Input('', key='-INPUT4-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t5 = sg.Input('', key='-INPUT5-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t6 = sg.Input('', key='-INPUT6-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t7 = sg.Input('', key='-INPUT7-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t8 = sg.Input('', key='-INPUT8-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t9 = sg.Input('', key='-INPUT9-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t10 = sg.Input('', key='-INPUT10-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t11 = sg.Input('', key='-INPUT11-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t12 = sg.Input('', key='-INPUT12-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t13 = sg.Input('', key='-INPUT13-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t14 = sg.Input('', key='-INPUT14-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t15 = sg.Input('', key='-INPUT15-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t16 = sg.Input('', key='-INPUT16-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t17 = sg.Input('', key='-INPUT17-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t18 = sg.Input('', key='-INPUT18-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t19 = sg.Input('', key='-INPUT19-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t20 = sg.Input('', key='-INPUT20-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t21 = sg.Input('', key='-INPUT21-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t22 = sg.Input('', key='-INPUT22-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t23 = sg.Input('', key='-INPUT23-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t24 = sg.Input('', key='-INPUT24-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t25 = sg.Input('', key='-INPUT25-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t26 = sg.Input('', key='-INPUT26-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    b1 = sg.Button('Ok',  enable_events=True, key='-OK-', font=('Arial', 16), size=(5,1))
    b2 = sg.Button('Exit', font=('Arial', 16), size=(5,1))

    layout = [[l1], 
    [sg.Push(),t1,t2,t3,t4,t5,sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push()],
    [sg.Push(),t6,t7,t8,t9,t10,sg.Push(),sg.Push(),l3,sg.Push(),sg.Push()],
    [sg.Push(),t11,t12,t13,t14,t15,l2,t26,sg.Push(),sg.Push(),sg.Push(),],
    [sg.Push(),t16,t17,t18,t19,t20,sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),],
    [sg.Push(),t21,t22,t23,t24,t25,sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push()], 
    [sg.Text(' ')],
    [sg.Push(), b1, sg.Push(),b2,sg.Push()]]

    custo_kernel = [[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]]

    window = sg.Window('Design a kernel', layout, size=(500, 350), keep_on_top=True)
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            custo_kernel = [[1]]
            break

        if event == '-OK-':
            if values['-INPUT26-'] != '':
                for i in range(5):
                    tmp=i*5
                    for j in range(5):
                        custo_kernel[i][j] = str_to_float(values['-INPUT26-'])

            else:   
                for i in range(5):
                    tmp=i*5
                    for j in range(5):
                        input_key = '-INPUT'+str(tmp+j+1)+'-'
                        custo_kernel[i][j] = str_to_float(values[input_key])

            if custo_kernel==[[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]]:
                custo_kernel = [[1]]
            break
        
    window.close()
    kernel[4] = np.array(custo_kernel)

def design_kernel_3X3():
    l1 = sg.Text('自訂kernel!!!', key='-OUT-', font=('Arial Bold', 16), expand_x=True, justification='center', size=(10, 2))
    l2 = sg.Text('OR', font=16, expand_x=False, justification='center', size=(6, 1))
    l3 = sg.Text('全部填充', expand_x=False, justification='right', size=(11, 1))
    t1 = sg.Input('', key='-INPUT1-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t2 = sg.Input('', key='-INPUT2-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t3 = sg.Input('', key='-INPUT3-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t4 = sg.Input('', key='-INPUT4-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t5 = sg.Input('', key='-INPUT5-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t6 = sg.Input('', key='-INPUT6-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t7 = sg.Input('', key='-INPUT7-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t8 = sg.Input('', key='-INPUT8-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t9 = sg.Input('', key='-INPUT9-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    t10 = sg.Input('', key='-INPUT10-', font=('Arial Bold', 20), expand_x=True, justification='left', size=(1, 2))
    b1 = sg.Button('Ok',  enable_events=True, key='-OK-', font=('Arial', 16), size=(5,1))
    b2 = sg.Button('Exit', font=('Arial', 16), size=(5,1))

    layout = [[l1], 
    [sg.Push(),t1,t2,t3,sg.Push(),l3,sg.Push(),],
    [sg.Push(),t4,t5,t6,l2,t10,sg.Push(),],
    [sg.Push(),t7,t8,t9,sg.Push(),sg.Push(),sg.Push(),sg.Push(),sg.Push(),],
    [sg.Text(' ')],
    [sg.Push(), b1, sg.Push(),b2,sg.Push()]]

    custo_kernel = [[1,1,1],[1,1,1],[1,1,1]]

    window = sg.Window('Design a kernel', layout, size=(400, 300), keep_on_top=True)
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            custo_kernel = [[1]]
            break

        if event == '-OK-':
            if values['-INPUT10-'] != '':
                for i in range(3):
                    tmp=i*3
                    for j in range(3):
                        custo_kernel[i][j] = str_to_float(values['-INPUT10-'])
            else:
                for i in range(3):
                    tmp=i*3
                    for j in range(3):
                        input_key = '-INPUT'+str(tmp+j+1)+'-'
                        custo_kernel[i][j] = str_to_float(values[input_key])

            if custo_kernel==[[1,1,1],[1,1,1],[1,1,1]]:
                custo_kernel = [[1]]
            break
        
    window.close()
    kernel[5] = np.array(custo_kernel)

#################################################

################ Resize Image ###################

def resize(image_file, new_size):
    im = Image.open(image_file)
    im.thumbnail(new_size, Image.Resampling.BILINEAR)
    try:
        im.save('./temp_img/tmp.jpg')
        return "./temp_img/tmp.jpg"
    except:
        im.save('./temp_img/tmp.png')
        return "./temp_img/tmp.png"

size = (350, 500)

#################################################

################ Update Image ###################

def update_img(kernel_idx, is_gray):
    result_path = __conv.conv(kernel[kernel_idx], targe_path, is_gray)
    result = Image.open(result_path)
    convolved_img = ImageTk.PhotoImage(result)
    window['-IMAGE2-'].update(data=convolved_img)
    window['-IMAGE2-'].set_size(window['-IMAGE2-'].get_size())

#################################################

#################### Work #######################

while True:
    event, values = window.read()
    
    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    if event == '-GETFILE-':

        targe_path_ori = values['-GETFILE-']

        targe_path = resize(targe_path_ori, size)
        image = Image.open(targe_path)
        photo_img = ImageTk.PhotoImage(image)
        
        window['-IMAGE-'].update(data=photo_img)
        window['-IMAGE-'].set_size(window['-IMAGE-'].get_size())

        window['ori'].update(value=True)
        window['gray_false'].update(value=True)
        values['ori'] = True
        values['k1'] = False
        values['k2'] = False
        values['k3'] = False
        values['k4'] = False
        values['k5'] = False
        values['k6'] = False
        values['k7'] = False
        values['k8'] = False
        values['gray_false'] = True
        values['gray_true'] = False
        gray_switch = False
        kernel_now = 0
        update_img(0, False)
        draw_kernel(kernel[0])
    
    if (values['ori'] == True) and  (kernel_now != 0) :
        kernel_now = 0
        update_img(0, gray_switch)
        draw_kernel(kernel[0])

    if (values['k1'] == True) and (kernel_now != 1):
        kernel_now = 1
        update_img(1, gray_switch)
        draw_kernel(kernel[1])

    if (values['k2'] == True) and (kernel_now != 2):
        kernel_now = 2
        update_img(2, gray_switch)
        draw_kernel(kernel[2])

    if (values['k3'] == True) and (kernel_now != 3):
        kernel_now = 3
        update_img(3, gray_switch)
        draw_kernel(kernel[3])
    
    if (values['k4'] == True) and  (kernel_now != 4):
        kernel_now = 4
        design_kernel_5X5()
        update_img(4, gray_switch)
        draw_kernel(kernel[4])

    if (values['k5'] == True) and  (kernel_now != 5):
        kernel_now = 5
        design_kernel_3X3()
        update_img(5, gray_switch)
        draw_kernel(kernel[5])

    if (values['k6'] == True) and (kernel_now != 6):
        kernel_now = 6
        update_img(6, gray_switch)
        draw_kernel(kernel[6])    

    if (values['k7'] == True) and (kernel_now != 7):
        kernel_now = 7
        update_img(7, gray_switch)
        draw_kernel(kernel[7])

    if (values['k8'] == True) and (kernel_now != 8):
        kernel_now = 8
        update_img(8, gray_switch)
        draw_kernel(kernel[8])

    if (values['gray_true'] == True) and (gray_switch != True):
        gray_switch = True
        update_img(kernel_now, gray_switch)
        draw_kernel(kernel[kernel_now])
    
    if (values['gray_false'] == True) and (gray_switch != False):
        gray_switch = False
        update_img(kernel_now, gray_switch)
        draw_kernel(kernel[kernel_now])

    if event == '-TAKEPIC-':
        takepicture.pic()
        targe_path_ori = './picture/thepicture.jpg'

        targe_path = resize(targe_path_ori, size)
        image = Image.open(targe_path)
        photo_img = ImageTk.PhotoImage(image)
        
        window['-IMAGE-'].update(data=photo_img)
        window['-IMAGE-'].set_size(window['-IMAGE-'].get_size())

        window['ori'].update(value=True)
        window['gray_false'].update(value=True)
        values['ori'] = True
        values['k1'] = False
        values['k2'] = False
        values['k3'] = False
        values['k4'] = False
        values['k5'] = False
        values['k6'] = False
        values['k7'] = False
        values['k8'] = False
        values['gray_false'] = True
        values['gray_true'] = False
        gray_switch = False
        kernel_now = 0
        update_img(0, False)
        draw_kernel(kernel[0])

    if event == '-DOWNLOAD-':
        result_path = __conv.conv(kernel[kernel_now], targe_path_ori, gray_switch)
        break

window.close()

#################################################