# -*- coding: utf-8 -*-
"""
Created on Wed May 27 10:27:55 2015
plot flat pictures about 7 sites` depth
@author: zhaobin
"""
import numpy as np
import matplotlib.pyplot as plt
#from pydap.client import open_url
import netCDF4
from utilities import lat2str, lon2str
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from conversions_old import dm2dd
import pandas as pd
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import pylab
def basemap_detail(fig,lat,lon,bathy,draw_parallels,TD,Bin,ALL=False,*parallels_interval):
    ## plot the coastline
    url='http://geoport.whoi.edu/thredds/dodsC/bathy/gom03_v1_0' # no longer gom03_v03
    def get_index_latlon(url):# use the function to calculate the minlat,minlon,maxlat,maxlon location
        try:
          dataset=netCDF4.Dataset(url)
        except:
          print("please check your url!")
          sys.exit(0)
        basemap_lat=dataset.variables['lat'][:]
        basemap_lon=dataset.variables['lon'][:]
        basemap_topo=dataset.variables['topo'][:]
        # add the detail of basemap
        minlat=min(lat)-0.01
        maxlat=max(lat)+0.01
        minlon=min(lon)+0.01
        maxlon=max(lon)-0.01
        index_minlat=int(round(np.interp(minlat,basemap_lat,range(0,basemap_lat.shape[0]))))
        index_maxlat=int(round(np.interp(maxlat,basemap_lat,range(0,basemap_lat.shape[0]))))
        index_minlon=int(round(np.interp(minlon,basemap_lon,range(0,basemap_lon.shape[0]))))
        index_maxlon=int(round(np.interp(maxlon,basemap_lon,range(0,basemap_lon.shape[0]))))
        return index_minlat,index_maxlat,index_minlon,index_maxlon,basemap_lat,basemap_lon,basemap_topo
    index_minlat,index_maxlat,index_minlon,index_maxlon,basemap_lat,basemap_lon,basemap_topo = get_index_latlon(url)
    #print basemap_lat[index_minlat],basemap_lat[index_maxlat],basemap_lon[index_minlon],basemap_lon[index_maxlon]
    min_index_lat=min(index_minlat,index_maxlat)
    max_index_lat=max(index_minlat,index_maxlat)
    X,Y=np.meshgrid(basemap_lon[index_minlon-15:index_maxlon+15],basemap_lat[min_index_lat-15:max_index_lat+15])
    # You can set negative contours to be solid instead of dashed:
    matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    #plot the bathy
    depth=basemap_topo[min_index_lat-15:max_index_lat+15,index_minlon-15:index_maxlon+15]
    print(np.amin(depth),np.amax(depth))
    if TD==True:
        if bathy==True:
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, depth, rstride=10, cstride=10, cmap=plt.cm.rainbow,
                linewidth=0, antialiased=False)
            ax.zaxis.set_major_locator(LinearLocator(10))
            cbar=fig.colorbar(surf, shrink=0.5, aspect=5)
    else:
        ax = plt.gca()
        cs=plt.contourf(X,Y,depth,[0,1000],colors='grey')
        if bathy==True:
            if Bin>5:
                CS=plt.contourf(X,Y,depth,np.arange(round(np.amin(depth))-1,1,2),cmap=plt.cm.rainbow,
                     vmax=1, vmin=round(np.amin(depth)))
            else:

                if np.amax(depth)>0:
                    CS=plt.contourf(X,Y,depth,np.arange(round(np.amin(depth))-1,1),cmap=plt.cm.rainbow,
                            vmax=1, vmin=round(np.amin(depth)))
                if np.amax(depth)<0:
                    CS=plt.contourf(X,Y,depth,np.arange(round(np.amin(depth))-1,np.max(depth)+2),cmap=plt.cm.rainbow,
                          vmax=round(np.amax(depth)), vmin=round(np.amin(depth)))
        if ALL==True:
            v = np.linspace(-350, 0, 8, endpoint=True)
            cbar=plt.colorbar(CS,ticks=v)
        else:
            cbar=plt.colorbar(CS)
        cbar.ax.tick_params(labelsize=20)
        cbar.ax.set_ylabel('Depth(m)', fontsize=20)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    #set up the map in a Equidistant Cylindrical projection
    
    if draw_parallels==True:
      from mpl_toolkits.basemap import Basemap
      m = Basemap(projection='cyl',llcrnrlat=min(lat),urcrnrlat=max(lat),\
          llcrnrlon=min(lon),urcrnrlon=max(lon),resolution='h',suppress_ticks=False)#,fix_aspect=False)
      if len(parallels_interval)<1:
        parallels_interval=1
        #draw parallels     
        m.drawparallels(np.arange(int(min(lat)),int(max(lat)),float(parallels_interval)),labels=[1,0,0,0],fmt=lat2str,dashes=[2,2])
        #draw meridians
        m.drawmeridians(np.arange(int(min(lon)),int(max(lon)),float(parallels_interval)),labels=[0,0,0,1],fmt=lon2str,dashes=[2,2])     
      else:
        parallels_interval=parallels_interval[0]
        #draw parallels
        m.drawparallels(np.arange(round(min(lat),2),round(max(lat),2),parallels_interval),labels=[1,0,0,0],fmt=lat2str,dashes=[2,2])
        #draw meridians
        m.drawmeridians(np.arange(round(min(lon),2),round(max(lon),2),parallels_interval),labels=[0,0,0,1],fmt=lon2str,dashes=[2,2]) 
    return np.amax(depth),np.amin(depth),ax,depth
############################################################################
one_minute=1.0/60
sites=[[207,271],[247,278],[443,327],[264,369],[245,370]]   #different sites to plot
data=pd.read_csv('binned_td_FVCOM.csv')
lat,lon=dm2dd(data['LATITUDE'],data['LONGITUDE']) #convert ddmm.m to dd.ddd
lat_i=np.arange(min(lat),max(lat),one_minute)   
lon_i=np.arange(min(lon),max(lon),one_minute)
fig=plt.figure(figsize=(12,10))
basemap_detail(fig,[41,44],[-71.31,-67.18],True,True,False,10,True,1)
for i in range(len(sites)):
    plt.scatter(lon_i[sites[i][0]],lat_i[sites[i][1]],s=200,c='red',marker='*')
    plt.annotate('site'+str(i+3),xy=(lon_i[sites[i][0]],lat_i[sites[i][1]]),xytext=(lon_i[sites[i][0]]+0.1,lat_i[sites[i][1]]),
           arrowprops=dict(arrowstyle='->'),fontsize=12)
plt.title('All sites ',fontsize=20)
plt.savefig('Site_all.png')
for i in range(len(sites)):
    fig=plt.figure(figsize=(12,10))   #plot flat
    if i+3==3:      #want to plot site 3 bigger
        basemap_detail(fig,[lat_i[sites[i][1]-11],lat_i[sites[i][1]+30]],[lon_i[sites[i][0]-11],lon_i[sites[i][0]+20]],True,True,False,10,10*one_minute)
    else:
        basemap_detail(fig,[lat_i[sites[i][1]-11],lat_i[sites[i][1]+20]],[lon_i[sites[i][0]-11],lon_i[sites[i][0]+20]],True,True,False,10,10*one_minute)
    plt.scatter(lon_i[sites[i][0]],lat_i[sites[i][1]],s=200,c='red',marker='*')
    plt.title('Site '+str(i+3),fontsize=20)
    plt.savefig('Site_'+str(i+3)+'_version_1.png')
    fig=plt.figure(figsize=(12,10))
    basemap_detail(fig,[lat_i[sites[i][1]-5],lat_i[sites[i][1]+5]],[lon_i[sites[i][0]-5],lon_i[sites[i][0]+5]],True,True,False,5,2*one_minute)
    plt.scatter(lon_i[sites[i][0]],lat_i[sites[i][1]],s=200,c='red',marker='*')
    plt.title('Site '+str(i+3),fontsize=20)
    plt.savefig('Site_'+str(i+3)+'_version_2.png')
    if i+3==5:    #plot 3d
        fig=plt.figure(figsize=(12,10))
        depth_max,depth_min,ax,ccc=basemap_detail(fig,[lat_i[sites[i][1]-5],lat_i[sites[i][1]+5]],[lon_i[sites[i][0]-5],lon_i[sites[i][0]+5]],True,False,True,5,2*one_minute)
        ax.scatter(lon_i[sites[i][0]],lat_i[sites[i][1]],depth_max,s=200,c='red',marker='*')
        ax.set_zlim3d(round(depth_min,-1),round(depth_max,-1))
        ax.set_zticks(np.arange(round(depth_min,-1),round(depth_max,-1),50))
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Depth(M)')
        plt.title('Site '+str(i+3),fontsize=20)
        #plt.savefig('Site_'+str(i+3)+'_3D.png')
plt.show()
