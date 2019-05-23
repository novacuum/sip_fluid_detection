import numpy
from PIL import Image
from matplotlib.cm import get_cmap
from numpy import unravel_index
from numpy.matlib import repmat
from skimage.filters import gaussian


def get_adjacency_matrix(img_input):
    # pad image with vertical column on both sides
    img_size = numpy.shape(img_input)
    img = numpy.zeros((img_size[0], img_size[1] + 2))

    img[:, 2: 1 + img_size[1]] = img_input

    # update size of image
    img_size = numpy.shape(img)

    # get vertical gradient image
    y_grad_img = numpy.gradient(img, [1, 1], axis=1)
    y_grad_img = -1 * y_grad_img

    # normalize gradient
    y_grad_img = (y_grad_img - min(y_grad_img)) / (max(y_grad_img) - min(y_grad_img))

    # get the "invert" of the gradient image.
    gradImgMinus = y_grad_img * -1 + 1

    ## generate adjacency matrix, see equation 1 in the refered article.

    # minimum weight
    minWeight = 1E-5

    neighborIterX = [1, 1, 1, 0, 0, -1, -1, -1]
    neighborIterY = [1, 0, -1, 1, -1, 1, 0, -1]

    # get location A (in the image as indices) for each weight.
    adjMAsub = list(range(1, img_size[0])) * img_size[1]

    # convert adjMA to subscripts
    # [adjMAx, adjMAy] = ind2sub(img_size, adjMAsub)
    [adjMAx, adjMAy] = unravel_index(adjMAsub, img_size)

    adjMAsub = adjMAsub
    szadjMAsub = numpy.shape(adjMAsub)

    # prepare to obtain the 8-connected neighbors of adjMAsub
    # repmat to [1,8]
    neighborIterX = repmat(neighborIterX, szadjMAsub[0], 1)
    neighborIterY = repmat(neighborIterY, szadjMAsub[0], 1)

    # repmat to [8,1]
    adjMAsub = repmat(adjMAsub, 1, 8)
    adjMAx = repmat(adjMAx, 1, 8)
    adjMAy = repmat(adjMAy, 1, 8)

    # get 8-connected neighbors of adjMAsub
    # adjMBx,adjMBy and adjMBsub
    adjMBx = adjMAx + neighborIterX(:)'
    adjMBy = adjMAy + neighborIterY(:)'

    # make sure all locations are within the image.
    keepInd = adjMBx > 0 & adjMBx <= img_size[1] & ...
    adjMBy > 0 & adjMBy <= img_size[2]

    # adjMAx = adjMAx(keepInd)
    # adjMAy = adjMAy(keepInd)
    adjMAsub = adjMAsub(keepInd)
    adjMBx = adjMBx(keepInd)
    adjMBy = adjMBy(keepInd)

    adjMBsub = sub2ind(img_size, adjMBx(:), adjMBy(:))'

    # calculate weight
    adjMW = 2 - gradImg(adjMAsub(:)) - gradImg(adjMBsub(:)) + minWeight
    adjMmW = 2 - gradImgMinus(adjMAsub(:)) - gradImgMinus(adjMBsub(:)) + minWeight

    # pad minWeight on the side
    imgTmp = nan(size(gradImg))
    imgTmp(:, 1) = 1
    imgTmp(:, end) = 1
    imageSideInd = ismember(adjMBsub, find(imgTmp(:) == 1))
    adjMW(imageSideInd) = minWeight
    adjMmW(imageSideInd) = minWeight


def getRetinalLayers(img):
    # resize the image if 1st value set to 'true',
    # with the second value to be the scale.
    params = {}

    # parameter for smothing the images.

    # constants used for defining the region for segmentation of individual layer
    params.roughILMandISOS = {}
    params.roughILMandISOS.shrinkScale = 0.2
    params.roughILMandISOS.offsets = range(-20, 20)
    params.ilm_0 = 4
    params.ilm_1 = 4
    params.isos_0 = 4
    params.isos_1 = 4
    params.rpe_0 = 0.05
    params.rpe_1 = 0.05
    params.inlopl_0 = 0.1  # 0.4%
    params.inlopl_1 = 0.3  # 0.5#  
    params.nflgcl_0 = 0.05  # 0.01
    params.nflgcl_1 = 0.3  # 0.1
    params.iplinl_0 = 0.6
    params.iplinl_1 = 0.2
    params.oplonl_0 = 0.05 % 4
    params.oplonl_1 = 0.5 % 4

    # parameters for ploting
    params.txtOffset = -7
    colorarr = get_cmap('jet')
    params.colorarr = colorarr[64:-8: 1, :]

    # a constant (not used in this function, used in 'octSegmentationGUI.m'.)
    params.smallIncre = 2

    # resize image.
    img = numpy.array(Image.fromarray(img).resize(img.shape * .5, Image.BILINEAR))

    # smooth image with specified kernels
    # for denosing
    img = gaussian(img, 5)

    # create adjacency matrices and its elements base on the image.
    [params.adjMatrixW, params.adjMatrixMW, params.adjMA, params.adjMB, params.adjMW, params.adjMmW,
     imgNew] = get_adjacency_matrix(img)
