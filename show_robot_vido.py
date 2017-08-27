#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
import simplejson as json
import base64
import cv2
import numpy as np
import time

def decodeB64(b64, depth=3):
    """base64 to OpenCV"""
    ii = base64.b64decode(b64)
    ii = np.fromstring(ii, dtype=np.uint8)
    img = cv2.imdecode(ii, depth)
    return img


def read(filename, depth=3):
    data = {}
    with open(filename, 'rb') as f:
        data = json.load(f)

    for key in data['stringified']:
        tmp = []
        for b64, datestamp in data[key]:
            img = decodeB64(b64, depth)
            tmp.append((img, datestamp))
        data[key] = tmp

    return data

# depth: 1 - grayscale, 3 - color
sensors = read('robot.json', 3)
imgs = sensors['camera']
imu = sensors['imu']
create = sensors['create']

length = len(imgs)
print('Camera Images: {}'.format(length))
i, ts0 = imgs[0]
i, ts1 = imgs[length-1]
len_time = ts1-ts0
print('Time span: {} sec'.format(len_time))
fps = length/len_time
print('fps: {}'.format(fps))

dt = int(1000/fps)
print('Time step between frames: {} msec'.format(dt))

for img, ts in imgs:
    cv2.imshow('img', img)
    cv2.waitKey(dt)

cv2.destroyAllWindows()