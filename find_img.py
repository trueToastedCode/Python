import cv2
import numpy as np
from PIL import Image, PngImagePlugin
from pyautogui import screenshot
import time

"""
find_image by trueToastedCode
version = 1.1
"""

methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
method = methods[1]
threshold = 0.98
get_middle= True
mode = 0 # above threshold + 0 = best or 1 = all above

def find_img(larger_img, smaller_img, result_fname = None):
    smaller_img = np.array(smaller_img)
    larger_img = np.array(larger_img)

    # get size of smaller image
    smaller_h, smaller_w = smaller_img.shape[:-1]

    if get_middle:
        smaller_h_half = int(smaller_h / 2)
        smaller_w_half = int(smaller_w / 2)

    # template matching
    res = cv2.matchTemplate(larger_img, smaller_img, eval(method))
    coordinates = []

    if mode == 0:
        # get the minimum squared difference
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # filter maxLoc
        if max_val >= threshold:
            # save coordinates
            coordinates.append((max_loc[0], max_loc[1]))
        else:
            return None
    elif mode == 1:
        # filter results
        match_loc = np.where(res >= threshold)

        if match_loc is not None:
            for (x, y) in zip(match_loc[1], match_loc[0]):
                coordinates.append((x, y))
        else:
            return None
    else:
        print('Mode', mode, 'does not exist!')
        return None

    # set middle and save
    if get_middle or result_fname is not None:
        for pos in range(len(coordinates)):
            x, y = coordinates[pos]
            if result_fname is not None:
                larger_img = cv2.rectangle(larger_img, (x, y), (x + smaller_w, y + smaller_h), (0, 0, 255), 2)
            if get_middle:
                coordinates[pos] = (x + smaller_w_half, y + smaller_h_half)

        if result_fname is not None:
            cv2.imwrite(result_fname, larger_img)

    if mode == 0:
        return coordinates[0]
    return coordinates

region = None

def get_screenshot():
    return screenshot(region = (region))

wait_apperance_in_s = 5
attempts = 1

def find_img_on_screen(img, result_fname = None):

    is_list = None
    if type(img) != list:
        is_list = False
        img = [img]
    else:
        is_list = True

    # prepare for formatting
    if result_fname != None:
        found = False
        for i in range(len(result_fname)-1, -1, -1):
            if result_fname[i] == '.':
                result_fname = result_fname[:i] + '{}' + result_fname[i:]
                found = True
                break
        if found == False:
            result_fname += '{}'

    coordinates = []

    for attempt in range(attempts):
        screen = get_screenshot()

        for i in range(len(img)):
            if attempt == 0:
                coordinates.append(None)

            # get result
            if result_fname == None:
                res = find_img(screen, img[i], None)
            else:
                res = find_img(screen, img[i], result_fname.format(i))

            if res == None:
                print('Image {}/{} not found!'.format(i + 1, len(img)))
            else:
                coordinates[i] = res


        # return results
        if attempt + 1 == attempts:
            if is_list:
                return coordinates
            elif coordinates[0] == None:
                return None
            elif type(coordinates[0]) == list:
                return coordinates[0]
            return coordinates[0][0], coordinates[0][1]

        if wait_apperance_in_s != None and wait_apperance_in_s != 0:
            print('Next Attempt: {}/{}, sleep {}s'.format(attempt + 2, attempts, wait_apperance_in_s))
            time.sleep(wait_apperance_in_s)


#print(find_img_on_screen([Image.open('find.PNG'), Image.open('find2.PNG')], 'test.png'))