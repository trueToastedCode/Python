from PIL import Image, ImageDraw, ImageFont
import textwrap

wPercent = 90
hPercent = 100
dPercent = 2
font = './BebasNeue-Regular.ttf'

def text2image(text, img, color):
    draw = ImageDraw.Draw(img)
    imgW, imgH = img.size
    desired_dist = int(dPercent*imgH/100)

    fnt_size = 1
    lines = textwrap.wrap(text, 5) # Change to higher number for sentences or use a function
    leng = len(lines)

    # find proper font size to attributes and parameters
    img_w_one_percent, img_h_one_percent = imgW / 100, imgH / 100
    x = 0
    data = []
    y = None

    while True:
        fnt = ImageFont.truetype(font, fnt_size)
        # calculate dimensions for current font size
        total_h = 0
        biggest_w = 0
        for i in range(leng):
            w, h = draw.textsize(lines[i], fnt)
            offset_x, offset_y = fnt.getoffset(lines[i])

            h -= offset_y
            total_h += h
            if (i+1) != leng:
                total_h += desired_dist

            if x == 0:
                w = w-offset_x
                if w > biggest_w:
                    if w/img_w_one_percent > wPercent:
                        x = 1
                        break
                    else:
                        biggest_w = w
            else:
                if y is None:
                    y = offset_y
                data.append(((imgW-(w+offset_x))/2, h))

        if x == 2:
            break
        elif x == 1 or total_h/img_h_one_percent > hPercent:
            x = 2
            fnt_size -= 1
        else:
            fnt_size += 1

    y = (imgH-total_h)/2-y

    for i in range(leng):
        draw.text((data[i][0], y), lines[i], font=fnt, fill=color)
        if (i+1) != leng:
            y += desired_dist+data[i][1]

    return img

# text2image('SPACE WALK', Image.new('RGB', (1000, 1000)), (255, 255, 255)).show()
