# -*- coding: utf-8 -*-
"""
Created on Thu May 23 07:35:54 2019

@author: anyam
"""

import glob, os, numpy
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
from skimage import filters
from skimage.color import rgb2gray
from skimage.draw import polygon
from skimage.measure import find_contours
from skimage.filters import threshold_yen, median, threshold_otsu
from skimage.io import imread
from skimage.feature import blob_doh, canny
from skimage.restoration import (denoise_tv_chambolle, denoise_bilateral,
                                 denoise_wavelet, estimate_sigma)
from skimage.exposure import equalize_adapthist
from skimage import util

def create_bg1_mask(image):
    image_grey = rgb2gray(image)
    image_grey[image_grey >= 0.9] = 0
    image_grey = equalize_adapthist(image_grey)
    image_gaussian = median(image_grey) 
    for i in range(1,5):
        image_gaussian = denoise_bilateral(image_gaussian, sigma_spatial=2, multichannel=False)
    #image_gaussian = filters.gaussian(image_denoised, 8)
    #image_gaussian = image_denoised
    image_gaussian[threshold_otsu(image_gaussian) > image_gaussian] = 0
    #image_gaussian[threshold_yen(image_gaussian) > image_gaussian] = 0
    #image_gaussian[image_gaussian < 0.3] = 0
    outer_masks = find_contours(image_gaussian, 0.01)
    mask = numpy.zeros_like(image_grey)

    for n, contour in enumerate(outer_masks):
        if len(contour) > 1000:
            x, y = polygon(contour[:, 0], contour[:, 1])
            mask[x, y] = 1
#    plt.subplot(1,2,1)
#    plt.imshow(mask, interpolation='nearest', cmap=plt.cm.gray)
#    plt.subplot(1,2,2)
#    plt.imshow(image_gaussian, interpolation='nearest', cmap=plt.cm.gray)
#    plt.show()

    return mask

def crop_to_mask(image, mask):
    mask_pil = Image.fromarray(mask).convert('L')
    bg = Image.new(mask_pil.mode, mask_pil.size, mask_pil.getpixel((0, 0)))
    diff = ImageChops.difference(mask_pil, bg)
    bbox = diff.getbbox()
    image = numpy.copy(image)
    image[mask == 0] = 1
    image_pil = Image.fromarray(image)
    return numpy.array(image_pil.crop(bbox)), bbox

def first_notmask(x, mask, bbox, image_cropped):
    value = image_cropped.shape[0]
    for i in range(image_cropped.shape[0]-1, 0, -1):
       if (mask[i+bbox[1], x+bbox[0]]==1):
           value = i
    return value

def last_notmask(x, mask, bbox, image_cropped):
    value = image_cropped.shape[0]
    for i in range(0, image_cropped.shape[0]):
       if (mask[i+bbox[1], x+bbox[0]]==1):
           value = i
    return value


def srf_detector(image):
    if_detected = False
    mask = create_bg1_mask(image)
    image_cropped_1, bbox = crop_to_mask(image, mask)
    image_cropped = rgb2gray(image_cropped_1)
    image_cropped = denoise_bilateral(image_cropped, sigma_spatial=2, multichannel=False)
    image_cropped = equalize_adapthist(image_cropped)
#    image_cropped = median(image_cropped)
#    for i in range(1,1):
#        image_cropped = denoise_bilateral(image_cropped, sigma_spatial=2, multichannel=False)
#    image_cropped_2 = canny(image_cropped, sigma = 6)
#    plt.imshow(image_cropped_2)
#    plt.show()
    #image_cropped_2[image_cropped >= 0.8] = 1
    #image_cropped_2[image_cropped <= 0.75] = 0
#    outer_masks = find_contours(image_cropped_2, 0.01)
#    total = 0
#    for n, contour in enumerate(outer_masks):
#        if len(contour) > 1000:
#            total +=1
#    if total ==2:
#        if_detected=True
#        print('SRF detected')
#    fig, ax = plt.subplots()
#    ax.imshow(image_cropped, interpolation='nearest', cmap=plt.cm.gray)
#
#    for n, contour in enumerate(outer_masks):
#        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
#    plt.show()
    
#    
    x_tot, y_tot = image_cropped.shape[0], image_cropped.shape[1]

    blobs_doh = blob_doh(image_cropped, max_sigma=50, threshold=.0045)

    plt.rcParams['image.cmap'] = 'gray'
    result = 'no SRF detected'
    fig, ax = plt.subplots(1, 1, figsize=(9, 3), sharex=True, sharey=True)
    for blob in blobs_doh:
        ax.set_title('Detected SRF in red')
        ax.imshow(image_cropped, cmap=plt.cm.gray, interpolation='nearest')
        y, x, r = blob
        c = plt.Circle((x, y), r, color='blue', linewidth=2, fill=False)
        ax.add_patch(c)
        p = True
        f_x = first_notmask(int(x), mask, bbox, image_cropped)
        if (r >1) and (r <20) and (x > 30) and (x < y_tot-30) and (y > 50) and (y < x_tot -50) and image_cropped[int(y), int(x)]<0.2 and (y > f_x + (1/4)*(image_cropped.shape[0]-x)):
            for i in range(-int(r)-3, int(r)+1+3):
                for j in range(-int(r)-3, int(r)+1+3):
                    if (mask[int(y)+bbox[1]+i, int(x)+bbox[0]+j]==0):
                       p = False
            if p:
                c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
                ax.add_patch(c)
                result = 'SRF detected'
                if_detected = True
    print(result)
    plt.show()
    return if_detected

results = numpy.empty(())
#images = glob.glob(os.path.join('./Train-Data/NoSRF', '*.png'))
images = glob.glob(os.path.join('./handout', '*.png'))
results = numpy.empty((len(images), 2), dtype=object)
i=0
for path in images:
    image = imread(path)
    srf_detector(image)
    number = 0
    if srf_detector(image)==True:
        number = 1  
    results[i,:] = (os.path.basename(path), number)
    i +=1 

numpy.savetxt('results.csv', results, fmt="%s,%i", delimiter=",")
