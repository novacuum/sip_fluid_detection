import glob, os, numpy
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageChops
from skimage import filters, morphology, exposure
from skimage.color import rgb2gray
from skimage.draw import polygon
from skimage.exposure import equalize_adapthist
from skimage.feature import canny
from skimage.filters import threshold_otsu, threshold_yen, threshold_adaptive
from skimage.measure import find_contours
from skimage.io import imread
from skimage.morphology import erosion
from skimage.restoration import denoise_wavelet, denoise_tv_chambolle


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
    image[mask == 0] = 1
    image_pil = Image.fromarray(image)
    return numpy.array(image_pil.crop(bbox))


def create_bg2_mask(image):
    image_grey = rgb2gray(image)
    image_gaussian = filters.gaussian(image_grey, 2)
    # image_gaussian[threshold_adaptive(image_gaussian, block_size=101) > image_gaussian] = 1
    image_gaussian[threshold_yen(image_gaussian, nbins=10) < image_gaussian] = 1
    contours = find_contours(image_gaussian, 0.8, fully_connected='high', positive_orientation='high')

    mask = numpy.zeros_like(image_grey)
    for n, contour in enumerate(contours):
        x, y = polygon(contour[:, 0], contour[:, 1])
        mask[x, y] = 1

    plt.subplot(1, 3, 1)
    plt.imshow(mask, interpolation='nearest', cmap=plt.cm.gray)
    plt.subplot(1, 3, 2)
    plt.imshow(image_gaussian, interpolation='nearest', cmap=plt.cm.gray)
    plt.subplot(1, 3, 3)
    plt.imshow(image)
    plt.show()

    return mask


images = glob.glob(os.path.join('../assets/SRF', '*.png'))
test_set = [
    '../assets/SRF/input_2515_1.png'
    , '../assets/SRF/input_2656_1.png'
]
#for i, path in enumerate(images):
for i, path in enumerate(test_set):
    print(i, path)
    image = imread(path)
    mask = create_bg1_mask(image)
    image_cropped = crop_to_mask(image, mask)
    create_bg2_mask(image_cropped)
    continue
    # image_cropped = exposure.equalize_hist(image_cropped)
    # image_cropped = erosion(image_cropped)
    # image_denoised = denoise_tv_chambolle(image_cropped, weight=0.4, multichannel=True)
    # image_gaussian[threshold_yen(image_gaussian) > image_gaussian] = 0
    # targets = find_contours(image_denoised, 0.8)
    images = [canny(image_cropped, 5, ), image_cropped]
    for image_index in [1]:
        fig, ax = plt.subplots()
        ax.imshow(images[image_index - 1], interpolation='nearest', cmap=plt.cm.gray)

        # for n, contour in enumerate(targets):
        #    ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

        ax.axis('image')
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()
