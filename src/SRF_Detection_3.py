# -*- coding: utf-8 -*-
"""
Created on Thu May 23 07:35:54 2019

@author: anyam
"""

import glob, os, numpy, sys
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

def fit_line(points):

    m = 0
    c = 0
    
    x0,y0,x1,y1 = points[0][0], points[0][1], points[1][0], points[1][1]
    
    if x0 != x1:
        m = (y0 - y1)/(x0 - x1)
    else:
        m = (y0 - y1)/(x0 - x1 + sys.float_info.epsilon)
    
    c =  y1 - m*x1

    return m, c



def point_to_line_dist(m, c, x0, y0):

    dist = 0
    x1 = (y0 + x0/m - c)/(m + 1/m)
    y1 = m*x1 + c
    dist = ((x0 - x1)**2 + (y0 - y1)**2)**(1/2)
    return dist

def ransac(x, first_notmask_x, image_cropped):
    mat = numpy.empty((len(x), 2))
    mat[:,0] = first_notmask_x
    mat[:, 1] = x
    edge_pts = mat

    edge_pts_xy = edge_pts[:, ::-1]
    
    ransac_iterations = 500
    ransac_threshold = 0.9
    n_samples = 2
    
    plotted = False
    ratio = 0.8
    model_m = 0
    model_c = 0
    
    # perform RANSAC iterations
    for it in range(ransac_iterations):
    
        all_indices = numpy.arange(edge_pts.shape[0])
        numpy.random.shuffle(all_indices)
    
        indices_1 = all_indices[:n_samples]
        indices_2 = all_indices[n_samples:]
    
        maybe_points = edge_pts_xy[indices_1, :]
        test_points = edge_pts_xy[indices_2, :]
    
        # find a line model for these points
        m, c = fit_line(maybe_points)
        num = 0
    
        # find distance to the model for all testing points
        for ind in range(test_points.shape[0]):
    
            x0 = test_points[ind, 0]
            y0 = test_points[ind, 1]
    
            # distance from point to the model
            dist = point_to_line_dist(m, c, x0, y0)
    
            # check whether it's an inlier or not
            if dist < ransac_threshold:
                num += 1
    
        # in case a new model is better - cache it
        if num / float(n_samples) > ratio:
            ratio = num / float(n_samples)
            model_m = m 
            model_c = c
    num =0
    x_new = x
    y = model_m * x_new + model_c
    for i in range(image_cropped.shape[1]):
        if 0 <(y[i] - first_notmask_x[i])<20:
            num += 1

    if num/ image_cropped.shape[1] > 0.52:
        plotted = True
    return plotted

def srf_detector(image):
    if_detected = False
    mask = create_bg1_mask(image)
    image_cropped_1, bbox = crop_to_mask(image, mask)
    image_cropped = rgb2gray(image_cropped_1)
    image_cropped = denoise_bilateral(image_cropped, sigma_spatial=2, multichannel=False)
    image_cropped = equalize_adapthist(image_cropped)

    x = numpy.arange(image_cropped.shape[1])
    first_notmask_x = [first_notmask(i, mask, bbox, image_cropped) for i in x]
    plotted = ransac(x, first_notmask_x, image_cropped)
    
    if plotted:
        result = 'No SRF detected'

    if plotted == False: 
        x_tot, y_tot = image_cropped.shape[0], image_cropped.shape[1]
    
        blobs_doh = blob_doh(image_cropped, max_sigma=50, threshold=.0045)
    
        plt.rcParams['image.cmap'] = 'gray'
        result = 'No SRF detected'
        fig, ax = plt.subplots(1, 1, figsize=(9, 3), sharex=True, sharey=True)
        for blob in blobs_doh:
            ax.set_title('Detected SRF in red')
            ax.imshow(image_cropped, cmap=plt.cm.gray, interpolation='nearest')
            y, x, r = blob
            #c = plt.Circle((x, y), r, color='blue', linewidth=2, fill=False)
            #ax.add_patch(c)
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
    value = srf_detector(image)
    number = 0
    if value==True:
        number = 1  
    results[i,:] = (os.path.basename(path), number)
    i +=1 

numpy.savetxt('results.csv', results, fmt="%s,%i", delimiter=",")
