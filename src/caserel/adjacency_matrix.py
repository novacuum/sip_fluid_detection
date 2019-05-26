import numpy
from numpy.matlib import repmat


def isin(element, test_elements, assume_unique=False, invert=False):
    element = numpy.asarray(element)
    return numpy.in1d(element, test_elements, assume_unique=assume_unique, invert=invert).reshape(element.shape)

def get_adjacency_matrix(img_input, max_radius_lim=None, epsilon=1e-5):
    # construct adjacency matrix later used to create a sparse graph per Chiu et al.
    # https://www.mathworks.com/matlabcentral/fileexchange/43518-graph-based-segmentation-of-retinal-layers-in-oct-images
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3342188/

    # get vertical gradient image
    y_grad_img = numpy.gradient(img_input, 1, axis=0)
    y_grad_img = -1 * y_grad_img
    img = (y_grad_img - numpy.min(y_grad_img)) / (numpy.max(y_grad_img) - numpy.min(y_grad_img))

    adjMAsub = numpy.array(numpy.arange(0, len(img.ravel())))
    adjMAx, adjMAy = numpy.unravel_index(adjMAsub, img.shape)

    adjMAsub = numpy.expand_dims(adjMAsub, axis=-1)
    adjMAx = numpy.expand_dims(adjMAx, axis=-1)
    adjMAy = numpy.expand_dims(adjMAy, axis=-1)

    neighborIterX = numpy.array([[1, 1, 1, 0, 0, -1, -1, -1]])
    neighborIterY = numpy.array([[1, 0, -1, 1, -1, 1, 0, -1]])
    neighborIterX = numpy.repeat(neighborIterX, adjMAsub.shape[0], axis=0)
    neighborIterY = numpy.repeat(neighborIterY, adjMAsub.shape[0], axis=0)

    adjMAsub = numpy.repeat(adjMAsub, 8, axis=1)
    adjMAx = numpy.repeat(adjMAx, 8, axis=1)
    adjMAy = numpy.repeat(adjMAy, 8, axis=1)

    adjMBx = adjMAx + neighborIterX
    adjMBy = adjMAy + neighborIterY

    adjMAsub = adjMAsub.ravel()
    adjMAx = adjMAx.ravel()
    adjMAy = adjMAy.ravel()

    adjMBx = adjMBx.ravel()
    adjMBy = adjMBy.ravel()

    criteria = numpy.array([
        [adjMBx > 0],
        [adjMBx < img.shape[0]],
        [adjMBy > 0],
        [adjMBy < img.shape[1]],
    ])

    keepInd = numpy.all(criteria, axis=0).squeeze()

    adjMAsub = adjMAsub[keepInd == 1]
    adjMAx = adjMAx[keepInd == 1]
    adjMAy = adjMAy[keepInd == 1]

    adjMBx = adjMBx[keepInd == 1]
    adjMBy = adjMBy[keepInd == 1]
    adjMBsub = numpy.ravel_multi_index([adjMBx, adjMBy], img.shape)

    adjMW = 2 - img.ravel()[adjMAsub] - img.ravel()[adjMBsub] + epsilon

    # make side easy
    mask = numpy.zeros(img.shape)
    mask[0, :] = 1
    mask[-1, :] = 1
    side_x, side_y = numpy.where(mask == 1)
    side_ind = numpy.ravel_multi_index([side_x, side_y], img.shape)
    isonsideA = isin(adjMAsub, side_ind)
    # isonsideB = isin(adjMBsub, side_ind) # prolly not needed
    adjMW[isonsideA == 1] = epsilon  # super low weight to force node to be selected as part of path
    # adjMW[isonsideB==1]=epsilon # prolly not needed

    # make bottom hard.
    if max_radius_lim is not None:
        nogo = numpy.zeros(img.shape)
        nogo[2:img.shape[0] - 2, max_radius_lim:] = 1
        nogo_x, nogo_y = numpy.where(nogo == 1)
        nogo_ind = numpy.ravel_multi_index([nogo_x, nogo_y], img.shape)
        isnogoA = isin(adjMAsub, nogo_ind)
        adjMW[isnogoA == 1] = 2  # high weight to prevent node to be select as part of path.

    edge_weights = numpy.array([adjMAsub, adjMBsub, adjMW])

    return edge_weights, adjMAsub, adjMBsub


def get_adjacency_matrix2(img_input):
    # pad image with vertical column on both sides
    img_size = numpy.shape(img_input)
    img = numpy.zeros((img_size[0] + 2, img_size[1]))

    img[1:img_size[1] + 1, :] = img_input

    # update size of image
    img_size = numpy.shape(img)

    # get vertical gradient image
    y_grad_img = numpy.gradient(img, 1, axis=0)
    y_grad_img = -1 * y_grad_img

    # normalize gradient
    y_grad_img = (y_grad_img - min(y_grad_img)) / (max(y_grad_img) - min(y_grad_img))

    # get the "invert" of the gradient image.
    gradImgMinus = y_grad_img * -1 + 1

    ## generate adjacency matrix, see equation 1 in the refered article.

    # minimum weight
    minWeight = 1E-5

    neighbor_iter_x = numpy.array([1, 1, 1, 0, 0, -1, -1, -1])
    neighbor_iter_y = numpy.array([1, 0, -1, 1, -1, 1, 0, -1])

    # get location A (in the image as indices) for each weight.
    adjMAsub = list(range(1, img_size[0])) * img_size[1]

    # convert adjMA to subscripts
    # [adjMAx, adjMAy] = ind2sub(img_size, adjMAsub)
    [adjMAx, adjMAy] = numpy.unravel_index(adjMAsub, img_size)

    adjMAsub = adjMAsub
    szadjMAsub = numpy.shape(adjMAsub)

    # prepare to obtain the 8-connected neighbors of adjMAsub
    # repmat to [1,8]
    neighbor_iter_x = repmat(neighbor_iter_x, szadjMAsub[0], 1)
    neighbor_iter_y = repmat(neighbor_iter_y, szadjMAsub[0], 1)

    # repmat to [8,1]
    adjMAsub = repmat(adjMAsub, 1, 8)
    adjMAx = repmat(adjMAx, 1, 8)
    adjMAy = repmat(adjMAy, 1, 8)

    # get 8-connected neighbors of adjMAsub
    # adjMBx,adjMBy and adjMBsub
    adjMBx = adjMAx + numpy.transpose(neighbor_iter_x[numpy.newaxis,])
    adjMBy = adjMAy + numpy.transpose(neighbor_iter_y[numpy.newaxis,])

    # # make sure all locations are within the image.
    # keepInd = adjMBx > 0 & adjMBx <= img_size[1] & ...
    # adjMBy > 0 & adjMBy <= img_size[2]
    #
    # # adjMAx = adjMAx(keepInd)
    # # adjMAy = adjMAy(keepInd)
    # adjMAsub = adjMAsub(keepInd)
    # adjMBx = adjMBx(keepInd)
    # adjMBy = adjMBy(keepInd)

    # adjMBsub = sub2ind(img_size, adjMBx(:), adjMBy(:))'
    #
    # # calculate weight
    # adjMW = 2 - gradImg(adjMAsub(:)) - gradImg(adjMBsub(:)) + minWeight
    # adjMmW = 2 - gradImgMinus(adjMAsub(:)) - gradImgMinus(adjMBsub(:)) + minWeight
    #
    # # pad minWeight on the side
    # imgTmp = nan(size(gradImg))
    # imgTmp(:, 1) = 1
    # imgTmp(:, end) = 1
    # imageSideInd = ismember(adjMBsub, find(imgTmp(:) == 1))
    # adjMW(imageSideInd) = minWeight
    # adjMmW(imageSideInd) = minWeight