from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import rmtk
import rmtk.plotting.common.parse_loss_maps as parselm
import rmtk.plotting.common.parse_exposure as parsee 
import rmtk.plotting.common.parse_vulnerability as parseev

def build_map(plotting_type,risk_map,bounding_box,exposure_model,export_map_to_csv):
	
    exposure_path = os.path.dirname(rmtk.__file__) + "/plotting/input_models/" + exposure_model
		
    agg_losses = True
    if plotting_type == 1:
        agg_losses = False

    data = parselm.parse_risk_maps(risk_map,agg_losses,export_map_to_csv)
    box = define_bounding_box(bounding_box,data[0])

    if plotting_type == 0 or plotting_type == 2:
        locations = np.array(data[1][0])
        losses = np.array(data[1][1])
      	plot_single_map(locations,losses,box,'Aggregated losses per location',1)

    if plotting_type == 1 or plotting_type == 2:
        individualLosses = data[0]
        idTaxonomies = np.array(parsee.extractIDTaxonomies(exposure_path,False))
        uniqueTaxonomies = extractUniqueTaxonomies(idTaxonomies[:,1])
        for i in range(len(uniqueTaxonomies)):
            locations,losses = processLosses(uniqueTaxonomies[i],idTaxonomies,individualLosses)
            plot_single_map(locations,losses,box,'Loss map for '+uniqueTaxonomies[i],i+2)

def define_bounding_box(bounding_box,data):

    locations=[]
    for asset in data:
        locations.append(asset[1:3])
    locations = np.array(locations)

    box = {"lon_0": None, "lat_0": None, "lon_1": None, 
        "lat_1": None, "lon_2": None, "lat_2": None}

    if bounding_box == 0:
        maxCoordinates = locations.max(axis=0)
        minCoordinates = locations.min(axis=0)
	lengthLon = abs(maxCoordinates[0]-minCoordinates[0])
	lengthLat = abs(maxCoordinates[1]-minCoordinates[1])

    box["lon_0"] = (minCoordinates[0]+maxCoordinates[0])/2
    box["lat_0"] = (minCoordinates[1]+maxCoordinates[1])/2
    box["lon_1"] = minCoordinates[0]-0.1*lengthLon
    box["lat_1"] = minCoordinates[1]-0.1*lengthLat
    box["lon_2"] = maxCoordinates[0]+0.1*lengthLon
    box["lat_2"] = maxCoordinates[1]+0.1*lengthLat

    return box

def plot_single_map(locations,losses,box,title,figNo):

    plt.figure(figNo, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    map = Basemap(llcrnrlon=box["lon_1"],llcrnrlat=box["lat_1"],
        urcrnrlon=box["lon_2"],urcrnrlat=box["lat_2"],projection='mill')

    x, y = map(locations[:,[0]],locations[:,[1]])
    # map.shadedrelief()
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='white',lake_color='aqua')
    plt.scatter(x,y,s=80,c=losses,zorder=4,cmap='bwr')
    if locations.shape[0] > 1:
        cbar = map.colorbar(location='right',pad="5%")
        cbar.set_label('EUR')
    plt.title(title)
    plt.show()

def extractUniqueTaxonomies(taxonomies):

    uniqueTaxonomies = []
    for taxonomy in taxonomies:
        if taxonomy not in uniqueTaxonomies:
            uniqueTaxonomies.append(taxonomy)

    return uniqueTaxonomies

def processLosses(uniqueTaxonomy,idTaxonomies,individualLosses):

    locations = []
    losses = []
    assetIDs = idTaxonomies[:,0]
    assetTax = idTaxonomies[:,1]
    selAssetIDs = assetIDs[np.where(assetTax==uniqueTaxonomy)]
    for individualLoss in individualLosses:
        if individualLoss[0] in selAssetIDs:
            locations.append(individualLoss[1:3])
            losses.append(individualLoss[3])

    return np.array(locations),np.array(losses)

