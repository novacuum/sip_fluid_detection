# -*- coding: utf-8 -*-
"""
Try to integrate the caserel library written in "matlab"

@author: grotti, hiller, parker
"""


import glob, os
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy
from PIL import Image, ImageChops
from skimage import filters
from skimage.color import rgb2gray
from skimage.draw import polygon
from skimage.filters import threshold_yen
from skimage.io import imread
from skimage.measure import find_contours

os.environ.setdefault('OCTAVE_EXECUTABLE', os.path.abspath('../vendors/octave-5.1.0-w64/mingw64/bin/octave-cli.exe'))

from oct2py import octave
octave.addpath('../vendors/caserel-master/')
octave.addpath('../vendors/networks-toolbox/')


def create_bg1_mask(image):
    image_grey = rgb2gray(image)
    image_grey[image_grey == 1] = 0
    image_gaussian = filters.gaussian(image_grey, 8)
    image_gaussian[threshold_yen(image_gaussian) > image_gaussian] = 0
    outer_masks = find_contours(image_gaussian, 0.2)
    mask = numpy.zeros_like(image_grey)

    for n, contour in enumerate(outer_masks):
        if len(contour) > 1000:
            x, y = polygon(contour[:, 0], contour[:, 1])
            mask[x, y] = 1

    # plt.subplot(1,2,1)
    # plt.imshow(mask, interpolation='nearest', cmap=plt.cm.gray)
    # plt.subplot(1,2,2)
    # plt.imshow(image, interpolation='nearest', cmap=plt.cm.gray)
    # plt.show()

    return mask


def crop_to_mask(image, mask):
    mask_pil = Image.fromarray(mask).convert('L')
    bg = Image.new(mask_pil.mode, mask_pil.size, mask_pil.getpixel((0, 0)))
    diff = ImageChops.difference(mask_pil, bg)
    bbox = diff.getbbox()
    image = numpy.copy(image)
    image_pil = Image.fromarray(image)
    return numpy.array(image_pil.crop(bbox))


images = glob.glob(os.path.join('../assets/SRF', '*.png'))
test_set = [
    '../assets/SRF/input_2515_1.png'
    , '../assets/SRF/input_2656_1.png'
]

colors = cm.get_cmap('jet')
for i, path in enumerate(images):
    #for i, path in enumerate(test_set):
    print(i, path)
    image = imread(path)
    mask = create_bg1_mask(image)
    image_cropped = crop_to_mask(image, mask)

    try:
        retina_layers = octave.getRetinalLayers(rgb2gray(image_cropped))
        plt.imshow(image_cropped, interpolation='nearest')

        for index, retina_layer in enumerate(retina_layers[0]):
            rangeX = retina_layer.pathY[0]
            rangeY = retina_layer.pathX[0]
            plt.plot(rangeX/.355, rangeY/.355, 'go--', linewidth=1, markersize=1, color=colors(index*10))
        plt.show()
    except:
        print('failed')
