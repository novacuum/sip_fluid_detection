# Generated with SMOP  0.41-beta
import numpy
from PIL import Image
import networkx
from networkx.algorithms.shortest_paths.generic import shortest_path
from caserel.adjacency_matrix import get_adjacency_matrix
from caserel.libsmop import *

def ismember(A, B):
    return [ np.sum(a == B) for a in A ]


# caserel-master/getHyperReflectiveLayers.m

#
#     {{Caserel}}
#     Copyright (C) {{2013}}  {{Pangyu Teng}}
# 
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License along
#     with this program; if not, write to the Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


@function
def getHyperReflectiveLayers(inputImg=None, constants=None, *args, **kwargs):
    # initiate parameters
    shrinkScale = 0.2
    offsets = range(-20, 20)

    szImg = numpy.shape(inputImg)
    procImg = numpy.array(Image.fromarray(inputImg).resize(inputImg.shape * shrinkScale, Image.BILINEAR))

    # create adjacency matrices
    adjMX, adjMY, adjMmW, newImg = get_adjacency_matrix(procImg)

    # create roi for getting shortestest path based on gradient-Y image.
    gx, gy = numpy.gradient(newImg)
    szImgNew = numpy.shape(newImg)
    roiImg = numpy.zeros(szImgNew)
    roiImg[gy > numpy.mean(gy)] = 1

    # find at least 2 layers
    path = [1]
    count = 1
    paths = []
    while len(path) > 0 and count <= 2:
        # add columns of one at both ends of images
        roiImg[:, 1] = 1
        roiImg[:, -1] = 1

        includeX = ismember(adjMX, find(ravel(roiImg) == 1))
        includeY = ismember(adjMY, find(ravel(roiImg) == 1))
        keepInd = logical_and(includeX, includeY)

        adjMatrix = sparse(adjMX(keepInd), adjMY(keepInd), adjMmW(keepInd), numel(ravel(newImg)), numel(ravel(newImg)))
        FG = networkx.Graph()
        FG.add_weighted_edges_from(adjMatrix)

        # get shortest path between 2 points
        sp = shortest_path(FG, source=1, target=numel(ravel(newImg)), weight='weight')

        if logical_not(isempty(path[1])):
            # get rid of first few points and last few points
            pathX, pathY = np.unravel_index(np.array(sp).astype(int), newImg.shape)
            select_gradients = numpy.gradient(pathY) != 0
            pathX = pathX[select_gradients]
            pathY = pathY[select_gradients]
            pathXArr = repmat(pathX, numel(offsets))
            # caserel-master/getHyperReflectiveLayers.m:79
            pathYArr = repmat(pathY, numel(offsets))
            # caserel-master/getHyperReflectiveLayers.m:80
            for i in arange(1, numel(offsets)).reshape(-1):
                pathYArr[i, :] = pathYArr(i, :) + offsets(i)
            # caserel-master/getHyperReflectiveLayers.m:82
            pathXArr = pathXArr(pathYArr > logical_and(0, pathYArr) <= szImgNew(2))
            # caserel-master/getHyperReflectiveLayers.m:85
            pathYArr = pathYArr(pathYArr > logical_and(0, pathYArr) <= szImgNew(2))
            # caserel-master/getHyperReflectiveLayers.m:86
            pathArr = sub2ind(szImgNew, pathXArr, pathYArr)
            # caserel-master/getHyperReflectiveLayers.m:88
            roiImg[pathArr] = 0
            # caserel-master/getHyperReflectiveLayers.m:89
            paths(count).pathX = copy(pathX)
            # caserel-master/getHyperReflectiveLayers.m:91
            paths(count).pathY = copy(pathY)
            # caserel-master/getHyperReflectiveLayers.m:92
            if isPlot:
                subplot(1, 3, 1)
                imagesc(inputImg)
                subplot(1, 3, 2)
                imagesc(gy)
                subplot(1, 3, 3)
                imagesc(roiImg)
                drawnow
                pause
        count = count + 1

    # format paths back to original size
    for i in range(0, len(paths)):
        paths(i).path, paths(i).pathY, paths(i).pathX = resizePath(szImg, szImgNew, constants, paths(i).pathY,
                                                                   paths(i).pathX, nargout=3)
        # caserel-master/getHyperReflectiveLayers.m:118
        paths(i).pathXmean = copy(nanmean(paths(i).pathX))
        # caserel-master/getHyperReflectiveLayers.m:119
        paths(i).name = copy([])
    # caserel-master/getHyperReflectiveLayers.m:120

    # name each path (numel(paths) should equal to 2)
    if numel(paths) != 2:
        paths = cellarray([])
        # caserel-master/getHyperReflectiveLayers.m:126
        display('error')
        return paths

    # based on the mean location detemine the layer type.
    if paths(1).pathXmean < paths(2).pathXmean:
        paths(1).name = copy('ilm')
        # caserel-master/getHyperReflectiveLayers.m:133
        paths(2).name = copy('isos')
    # caserel-master/getHyperReflectiveLayers.m:134
    else:
        paths(1).name = copy('isos')
        # caserel-master/getHyperReflectiveLayers.m:136
        paths(2).name = copy('ilm')
    # caserel-master/getHyperReflectiveLayers.m:137

    if isPlot:
        imagesc(inputImg)
        axis('image')
        colormap('gray')
        hold('on')
        for i in arange(1, numel(paths)).reshape(-1):
            cola = rand(1, 3)
            # caserel-master/getHyperReflectiveLayers.m:146
            plot(paths(i).pathY, paths(i).pathX, 'r-', 'linewidth', 3)
            text(paths(i).pathY(end()), paths(i).pathX(end()) - 15, paths(i).name, 'color', rand(1, 3))
            drawnow
        hold('off')
