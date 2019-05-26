from PIL import Image
from matplotlib.cm import get_cmap
from skimage.filters import gaussian
from caserel.adjacency_matrix import get_adjacency_matrix
from caserel.libsmop import *
from caserel.retina_layers_core import get_retinal_layers_core


def getRetinalLayers(img):
    # resize the image if 1st value set to 'true',
    # with the second value to be the scale.
    params = {'roughILMandISOS': {}}
    # constants used for defining the region for segmentation of individual layer
    params['roughILMandISOS']['shrinkScale'] = 0.2
    params['roughILMandISOS']['offsets'] = range(-20, 20)
    params['ilm_0'] = 4
    params['ilm_1'] = 4
    params['isos_0'] = 4
    params['isos_1'] = 4
    params['rpe_0'] = 0.05
    params['rpe_1'] = 0.05
    params['inlopl_0'] = 0.1  # 0.4%
    params['inlopl_1'] = 0.3  # 0.5#  
    params['nflgcl_0'] = 0.05  # 0.01
    params['nflgcl_1'] = 0.3  # 0.1
    params['iplinl_0'] = 0.6
    params['iplinl_1'] = 0.2
    params['oplonl_0'] = 0.05 % 4
    params['oplonl_1'] = 0.5 % 4

    # parameters for ploting
    params['txtOffset'] = -7
    colorarr = get_cmap('jet')
    params['colorarr'] = colorarr[64:-8: 1, :]

    # a constant (not used in this function, used in 'octSegmentationGUI.m'.)
    params['smallIncre'] = 2

    # resize image.
    img = numpy.array(Image.fromarray(img).resize(img.shape * .5, Image.BILINEAR))

    # smooth image with specified kernels
    # for denosing
    img = gaussian(img, 5)

    # create adjacency matrices and its elements base on the image.
    [params, img_new] = get_adjacency_matrix(img)

    # obtain rough segmentation of the ilm and isos, then find the retinal
    # layers in the order of 'retinalLayerSegmentationOrder'
    ##vvvvvvvvvvvvvvvDO  NOT  CHANGE BELOW LINE (ORDER OF LAYERS SHALL NOT BE CHANGED)vvvvvvvvvvvvvv##
    retinal_layer_segmentation_order = ['roughILMandISOS', 'ilm', 'isos', 'rpe', 'inlopl', 'nflgcl', 'iplinl', 'oplonl']
    # segment retinal layers
    retinal_layers = {}
    for retinal_layer_segmentation in retinal_layer_segmentation_order:
        get_retinal_layers_core(retinal_layer_segmentation, img_new, params, retinal_layers, nargout=2)

    return retinal_layers