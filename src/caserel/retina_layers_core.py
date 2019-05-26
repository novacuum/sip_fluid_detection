# Generated with SMOP  0.41-beta
import numpy

from caserel.libsmop import *

# caserel-master/getRetinalLayersCore.m

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
middle_layers = ['nflgcl', 'inlopl', 'ilm', 'isos', 'oplonl', 'iplinl', 'rpe']


@function
def get_retinal_layers_core(layerName=None, img=None, params=None, retinalLayers=None, *args, **kwargs):
    szImg = numpy.shape(img)

    if 'roughILMandISOS' == layerName:
        imgOld = img[1:-1, :]
        pathsTemp = getHyperReflectiveLayers(imgOld, params.roughILMandISOS)
        retinalLayers = copy(pathsTemp)
        return retinalLayers, img
    else:
        if layerName in middle_layers:
            adjMA = params.adjMA
            adjMB = params.adjMB
            adjMW = params.adjMW
            adjMmW = params.adjMmW
        if layerName in middle_layers:
            adjMA = params.adjMA
            adjMB = params.adjMB
            adjMW = params.adjMW
            adjMmW = params.adjMmW

    roiImg = numpy.zeros(szImg)

    # avoid the top part of image
    roiImg[1:20, :] = 0

    # caserel-master/getRetinalLayersCore.m:69
    # select region of interest based on layers priorly segmented.
    for k in range():
        if 'nflgcl' == layerName:
            # define a region (from 'startInd' to 'endInd') between 'ilm'
            # and 'inlopl'.
            indPathX = find(retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:80
            startInd0 = retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:81
            indPathX = find(retinalLayers(strcmp('inlopl', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:82
            endInd0 = retinalLayers(strcmp('inlopl', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:83
            startInd = startInd0 - ceil(dot(params.nflgcl_0, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:85
            endInd = endInd0 - round(dot(params.nflgcl_1, (endInd0 - startInd0)))
        # caserel-master/getRetinalLayersCore.m:86
        if 'rpe' == layerName:
            indPathX = find(retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:90
            startInd0 = retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:93
            endInd0 = startInd0 + round(
                (retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathXmean - retinalLayers(
                    strcmp('ilm', cellarray([retinalLayers.name]))).pathXmean))
            # caserel-master/getRetinalLayersCore.m:94
            startInd = startInd0 + round(dot(params.rpe_0, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:96
            endInd = endInd0 - round(dot(params.rpe_1, (endInd0 - startInd0)))

        if 'inlopl' == layerName:
            # define a region (from 'startInd' to 'endInd') between 'ilm'
            # and 'isos'.
            indPathX = find(retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:103
            startInd0 = retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:104
            indPathX = find(retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:105
            endInd0 = retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:106
            startInd = startInd0 + round(dot(params.inlopl_0, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:108
            endInd = endInd0 - round(dot(params.inlopl_1, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:109
        if cellarray(['ilm']) == layerName:
            # define a region (from 'startInd' to 'endInd') near 'ilm'.
            indPathX = find(retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:114
            startInd = retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathX(indPathX(1)) - params.ilm_0
            # caserel-master/getRetinalLayersCore.m:116
            endInd = retinalLayers(strcmp('ilm', cellarray([retinalLayers.name]))).pathX(indPathX(1)) + params.ilm_1
            # caserel-master/getRetinalLayersCore.m:117

        if cellarray(['isos']) == layerName:
            # define a region (from 'startInd' to 'endInd') near 'isos'.
            indPathX = find(retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:122
            startInd = retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathX(
                indPathX(1)) - params.isos_0
            # caserel-master/getRetinalLayersCore.m:124
            endInd = retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathX(
                indPathX(1)) + params.isos_1
            # caserel-master/getRetinalLayersCore.m:125

        if cellarray(['iplinl']) == layerName:
            # define a region (from 'startInd' to 'endInd') between
            # 'nflgcl' and 'inlopl'.
            indPathX = find(retinalLayers(strcmp('nflgcl', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:131
            startInd0 = retinalLayers(strcmp('nflgcl', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:132
            indPathX = find(retinalLayers(strcmp('inlopl', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:133
            endInd0 = retinalLayers(strcmp('inlopl', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:134
            startInd = startInd0 + round(dot(params.iplinl_0, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:136
            endInd = endInd0 - round(dot(params.iplinl_1, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:137

        if cellarray(['oplonl']) == layerName:
            # define a region (from 'startInd' to 'endInd') between
            # 'inlopl' and 'isos'.
            indPathX = find(retinalLayers(strcmp('inlopl', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:144
            startInd0 = retinalLayers(strcmp('inlopl', cellarray([retinalLayers.name]))).pathX(
                indPathX(1))
            # caserel-master/getRetinalLayersCore.m:145
            indPathX = find(retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathY == k)
            # caserel-master/getRetinalLayersCore.m:146
            endInd0 = retinalLayers(strcmp('isos', cellarray([retinalLayers.name]))).pathX(indPathX(1))
            # caserel-master/getRetinalLayersCore.m:147
            #           startInd = startInd0 + params.oplonl_0;
            #           endInd = endInd0 - params.oplonl_1;
            startInd = startInd0 + round(dot(params.oplonl_0, (endInd0 - startInd0)))
            # caserel-master/getRetinalLayersCore.m:151
            endInd = endInd0 - round(dot(params.oplonl_1, (endInd0 - startInd0)))
    # caserel-master/getRetinalLayersCore.m:152
    # error checking
    if startInd > endInd:
        startInd = endInd - 1
    # caserel-master/getRetinalLayersCore.m:157
    if startInd < 1:
        startInd = 1
    # caserel-master/getRetinalLayersCore.m:161
    if endInd > szImg(1):
        endInd = szImg(1)
    # caserel-master/getRetinalLayersCore.m:165
    # set region of interest at column k from startInd to endInd
    roiImg[arange(startInd, endInd), k] = 1


# caserel-master/getRetinalLayersCore.m:169

# ensure the 1st and last column is part of the region of interest.
roiImg[arange(), 1] = 1
# caserel-master/getRetinalLayersCore.m:174
roiImg[arange(), end()] = 1
# caserel-master/getRetinalLayersCore.m:175
# include only region of interst in the adjacency matrix
includeA = ismember(adjMA, find(ravel(roiImg) == 1))
# caserel-master/getRetinalLayersCore.m:178
includeB = ismember(adjMB, find(ravel(roiImg) == 1))
# caserel-master/getRetinalLayersCore.m:179
keepInd = logical_and(includeA, includeB)
# caserel-master/getRetinalLayersCore.m:180
#     #alternative to ismember,
#     roiImgOne = find(roiImg(:) == 1)';
#     includeA = sum(bsxfun(@eq,adjMA(:),roiImgOne),2);
#     includeB = sum(bsxfun(@eq,adjMB(:),roiImgOne),2);
#     keepInd = includeA & includeB;

# get the shortestpath
if cellarray(['rpe', 'nflgcl', 'oplonl', 'iplinl']) == layerName:
    adjMatrixW = sparse(adjMA(keepInd), adjMB(keepInd), adjMW(keepInd), numel(ravel(img)), numel(ravel(img)))
    # caserel-master/getRetinalLayersCore.m:192
    __, path = graphshortestpath(adjMatrixW, 1, numel(ravel(img)), nargout=2)
# caserel-master/getRetinalLayersCore.m:193
# for i = 1:numel(path)-1,dist(i)=adjMatrixW(path(i),path(i+1));end
# dark to bright
else:
    if cellarray(['inlopl', 'ilm', 'isos']) == layerName:
        adjMatrixMW = sparse(adjMA(keepInd), adjMB(keepInd), adjMmW(keepInd), numel(ravel(img)), numel(ravel(img)))
        # caserel-master/getRetinalLayersCore.m:198
        __, path = graphshortestpath(adjMatrixMW, 1, numel(ravel(img)), nargout=2)
# caserel-master/getRetinalLayersCore.m:199
# for i = 1:numel(path)-1,dist(i)=adjMatrixMW(path(i),path(i+1));end

# convert path indices to subscript
pathX, pathY = ind2sub(szImg, path, nargout=2)
# caserel-master/getRetinalLayersCore.m:205
# if name layer existed, overwrite it, else add layer info to struct
matchedLayers = strcmpi(layerName, cellarray([ravel(retinalLayers).name]))
# caserel-master/getRetinalLayersCore.m:208
layerToPlotInd = find(matchedLayers == 1)
# caserel-master/getRetinalLayersCore.m:209
if isempty(layerToPlotInd):
    layerToPlotInd = numel(retinalLayers) + 1
    # caserel-master/getRetinalLayersCore.m:211
    retinalLayers(layerToPlotInd).name = copy(layerName)
# caserel-master/getRetinalLayersCore.m:212

# save data.
retinalLayers(layerToPlotInd).path = copy(path)
# caserel-master/getRetinalLayersCore.m:216
# rPaths(layerToPlotInd).dist = dist;
retinalLayers(layerToPlotInd).pathX = copy(pathX)
# caserel-master/getRetinalLayersCore.m:218
retinalLayers(layerToPlotInd).pathY = copy(pathY)
# caserel-master/getRetinalLayersCore.m:219
retinalLayers(layerToPlotInd).pathXmean = copy(
    mean(retinalLayers(layerToPlotInd).pathX(gradient(retinalLayers(layerToPlotInd).pathY) != 0)))
# caserel-master/getRetinalLayersCore.m:220
# create an additional smoother layer for rpe
isSmoothRpe = 1
# caserel-master/getRetinalLayersCore.m:223
if isSmoothRpe:
    if cellarray(['rpe']) == layerName:
        # find lines where pathY is on the image
        rpePathInd = gradient(pathY) != 0
        # caserel-master/getRetinalLayersCore.m:229
        lambda_ = 1e-06
        # caserel-master/getRetinalLayersCore.m:232
        pathXpoly = copy(pathX)
        # caserel-master/getRetinalLayersCore.m:233
        pathYpoly = copy(pathY)
        # caserel-master/getRetinalLayersCore.m:234
        pathXpoly(rpePathInd), __ = csaps(pathY(rpePathInd), pathX(rpePathInd), lambda_, pathY(rpePathInd),
                                          nargout=2)
        # caserel-master/getRetinalLayersCore.m:236
        #             [pathXpoly(rpePathInd), ~] = csaps_pt(pathY(rpePathInd),pathX(rpePathInd),...
        #                lambda,pathY(rpePathInd));
        # add layer info to struct
        # layerToPlotInd = numel(rPaths)+1;
        # rPaths(layerToPlotInd).name = 'rpeSmooth';
        # update rpw layer info to struct
        retinalLayers(layerToPlotInd).pathX = copy(round(pathXpoly))
        # caserel-master/getRetinalLayersCore.m:246
        retinalLayers(layerToPlotInd).pathY = copy(round(pathYpoly))
        # caserel-master/getRetinalLayersCore.m:247
        retinalLayers(layerToPlotInd).path = copy(
            sub2ind(szImg, retinalLayers(layerToPlotInd).pathX, retinalLayers(layerToPlotInd).pathY))
        # caserel-master/getRetinalLayersCore.m:248
        retinalLayers(layerToPlotInd).pathXmean = copy(
            mean(retinalLayers(layerToPlotInd).pathX(gradient(retinalLayers(layerToPlotInd).pathY) != 0)))
# caserel-master/getRetinalLayersCore.m:249
