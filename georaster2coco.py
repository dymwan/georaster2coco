'''
convert the pair of tiff image and shapefile to jpg and annotations
'''

import os
import numpy as np
from PIL import Image
from osgeo import gdal
import geopandas as gpd
# from shapely.geometry.polygon import Polygon
from shapely.geometry import Polygon, MultiPolygon
import rasterio as rio
import json

INIT = {
    
    "info":{
        "contributor": "dymwan@gmail.com",
        "about": "desc",
        "date_created": None,
        "description": "desc",
        "url": "https://github.com/dymwan",
        "version": "1.0",
        "year": 2024
        },
    "categories": [
        {
            "id": 100, 
            "name": "fieldparcel",
            "supercategory": "agriculture"
        }
    ],
    "images": [],
    "annotations": [],
    
}


class vector:
    def __init__(self):
        self.gdf = None
        self.crs = None
        
        self.is_empty = True
        
    def register(self, vec_path:str):
        
        if not self.is_empty:
            self.__init__()
            
        self.gdf = gpd.read_file(vec_path)
        self.crs = self.gdf.crs
        
    def clip(self, xs, xe, ys, ye):
        
        clipped = self.gdf.clip_by_rect(xs, ye, xe, ys)
        
        clipped = clipped[~clipped.is_empty]
        
        return clipped
        
    
    def prj_align(self, refds:gdal.Dataset):
        pass


class raster:
    clip_size   = None
    clip_stride = None
    def __init__(self) -> None:
        
        self.raster = None #gdal.Open(raster_path)

        # init shape info
        self.rnb = None #self.raster.RasterCount
        self.col = None #self.raster.RasterXSize
        self.row = None #self.raster.RasterYSize

        # init geo info
        self.gt = None #self.raster.GetGeoTransform()
        self.prj= None #self.raster.GetProjection()
        
        self.is_empty = True
        
        self.clip_map = None
    
    def register_clipper(self, clip_size=None, clip_stride=None):
        if clip_size is None:
            assert self.row == self.col
            self.clip_size = self.row
        else:
            self.clip_size = clip_size
            self.clip_stride = clip_stride
    
    def register_file(self, raster_path):
        if not self.is_empty:
            self._flush() # may be redundent
            self.__init__()
        
        self.raster:gdal.Dataset    = gdal.Open(raster_path)
        if self.raster is None:
            raise IOError("Loading raster {raster_path} failed.")
        
        self.rnb                    = self.raster.RasterCount 
        self.row                    = self.raster.RasterXSize
        self.col                    = self.raster.RasterYSize
        self.gt                     = self.raster.GetGeoTransform()
        self.prj                    = self.raster.GetProjection()
        
        self.is_empty = False
        
        self.get_clipping_map(self.clip_size, self.clip_stride)
        # print(self.raster is None)

    def get_clipping_map(self, clipsize, clipstride):
        # clipstride = 0 if clipstride is None else clipstride
        assert self.clip_size > 0, 'use register_clipper first'
        self.clip_map = _get_clipping_map(
            self.col, self.row, clipsize, clipstride
        )
    
    def xy2coords(self, x, y):
        lon = self._x2lon(x)
        lat = self._y2lat(y)
        return lon, lat
    
    def _x2lon(self, x):
        return self.gt[0] + x * self.gt[1]

    def _y2lat(self, y):
        return self.gt[3] + y * self.gt[5]
    
    def get_sub_gt_by_xy(self, xoff, yoff, xscale=None, yscale=None):
        gt = list(self.gt)
        
        gt[0] += xoff * gt[1]
        gt[3] += yoff * gt[-1]
        
        
        if xscale is not None:
            gt[1] *= xscale
        if yscale is not None:
            gt[-1] *= yscale
            
        return gt
    
    def clipper(self):
        # print(self.col, self.row)
        for xs, xe, ys, ye in self.clip_map:
            patch = self.raster.ReadAsArray(xs, ys, abs(xe-xs), abs(ye-ys))
            yield patch, [
                xs, xe, ys, ye,
                self._x2lon(xs),
                self._x2lon(xe),
                self._y2lat(ys),
                self._y2lat(ye),
            ]
    
    def _flush(self):
        self.raster = None
        
        

class geo2cocoConvertor:
    def __init__(   
                    self, 
                    dst_root,
                    clip_size       =None, 
                    clip_stride     =None, 
                    prefix          ='',
                    suffix          ='jpg',
                    phase           ='train'
                    
                    ):
        self.root = dst_root
        self.im_folder = make_folder(self.root, 'images')
        
        self.prefix = prefix
        self.suffix = suffix
        
        self.clip_size = clip_size; self.clip_stride = clip_stride
        
        # self.rst_f = raster_format
        # self.vec_f = vec_format
        
        self.r = raster()
        self.v = vector()

        self.r.register_clipper(clip_size, clip_stride)
        # self.v.register()
        
        self.im_index = 1
        self.poly_index = 1
        
        #TODO update INIT here
    
    def __call__(self, raster_path:str, vec_path):
        self.r.register_file(raster_path)
        self.v.register(vec_path)
        
        for patch, [xs, xe, ys, ye, lonmin, lonmax, latmax, latmin] in self.r.clipper():
            new_gt = self.r.get_sub_gt_by_xy(xoff=xs, yoff=ys)
            
            filename = self.prefix + '{:0>6d}.{}'.format(self.im_index, self.suffix.lstrip('.'))
            
            im_info = get_im_coco(
                self.im_index, filename, patch.shape[-2:]
            )
            INIT['images'].append(im_info)
            
            
            dst_im_path = os.path.join(self.im_folder, filename)
            save_tifarr_to_jpg(patch, dst_im_path)
            
            
            # save_tifarr_to_jpg(patch, dst_dir)
            clipped_poly = self.v.clip(lonmin, lonmax, latmax, latmin)
            
            # print(clipped_poly)
            for p in clipped_poly:
                if isinstance(p, Polygon):
                    anno_info=parse_polygon_to_coco(
                        p, new_gt, self.poly_index, self.im_index, catid=100
                        )
                    
                    INIT['annotations'].append(anno_info)
                    self.poly_index += 1
                elif isinstance(p, MultiPolygon):
                    for pp in p.geoms:
                        anno_info=parse_polygon_to_coco(
                        pp, new_gt, self.poly_index, self.im_index, catid=100
                        )
                    
                        INIT['annotations'].append(anno_info)
                        self.poly_index += 1
            self.im_index += 1
        
        
    def dump_json(self):
        with open(os.path.join(self.root, 'annotation.json'), 'w') as f:
            json.dump(INIT, f)


def parse_polygon_to_coco(p:Polygon, gt, pid, iid, catid, is_crowded=0):
    lons, lats = p.exterior.coords.xy
    y = _lon2y(list(lons), gt)
    x = _lat2x(list(lats), gt)
    
    pnew = Polygon(zip(x,y))
    
    blonmin, blatmin, blonmax, blatmax = p.bounds
    bbox = _lat2x([blatmin, blatmax], gt) + _lon2y([blonmax, blonmin], gt)
    
    seg = []
    for xi, yi in zip(x,y): seg+=[yi, xi]
    
    return {
        "id"            : pid,
        "image_id"      : iid,
        "segmentation"  : [seg],
        "area"          : pnew.area,
        "bbox"          : bbox,
        "category_id"   : catid,
        "iscrowd"       : is_crowded,
    }
    
def get_im_coco(iid, filename, size):
    return {
        "id"        : iid,
        "file_name" : filename,
        "width"     : size[0],
        "height"    : size[1]
    }
    
def save_tifarr_to_jpg(patch, dst_path):
    I = Image.fromarray(patch.transpose(1,2,0)).convert("RGB")
    I.save(dst_path)
    
def save_tiffpatch(patch, dst_path, gt, prj):
    '''
    save multi-band now TODO
    '''
    n, y, x = patch.shape
    
    drv:gdal.Driver = gdal.GetDriverByName('GTiff')
    ods:gdal.Dataset= drv.Create(dst_path, x, y, n, gdal.GDT_Byte)
    # print(gt)
    ods.SetGeoTransform(gt)
    ods.SetProjection(prj)
    for bi in range(n):
        band = ods.GetRasterBand(bi + 1)
        band.WriteArray(patch[bi, :, :])
    
    ods = None
    
def save_to_shp(polygons, dst_path, crs=None):
    ogdf = gpd.GeoDataFrame(
        {"geometry": polygons}, crs=crs
    )
    ogdf.to_file(dst_path)

def _lon2y(lon, gt):
    if isinstance(lon, float):
        y = (lon - gt[0]) / gt[1]
    elif isinstance(lon, list):
        y = [(e - gt[0]) / gt[1] for e in lon]
    else:
        raise NotImplementedError
    return y

def _lat2x(lat, gt):
    if isinstance(lat, float):
        x = (lat - gt[3]) / gt[-1]
    elif isinstance(lat, list):
        x = [(e - gt[3]) / gt[-1] for e in lat]
    else:
        raise NotImplementedError
    return x

def _get_clipping_map(col, row, clipsize, clipstride=None):

    assert clipsize <= col and clipsize <= row

    clipstride = clipsize if clipstride is None else clipstride
    
    _po = clipsize - clipstride # patch offset
    xbound =  [] if (row-_po)%clipstride==0 else [row-clipsize]
    xss = [(e) * clipstride for e in range((row-_po)//clipstride)] + xbound
    
    ybound =  [] if (col-_po)%clipstride==0 else [col-clipsize]
    yss = [(e) * clipstride for e in range((col-_po)//clipstride)] + ybound
    
    cliping_map = []
    
    for xs in xss:
        for ys in yss:
            cliping_map.append(
                [xs, xs + clipsize, ys, ys +clipsize]
            )
    
    return cliping_map

def make_folder(*args):
    fn = os.path.join(*args)
    if not os.path.isdir(fn):
        os.makedirs(fn)
    return fn
        

if __name__ == '__main__':
    
    from tqdm import tqdm
    
    img_root    = r''
    poly_root   = r''

    train_c = geo2cocoConvertor(clip_size=512, clip_stride=None, dst_root=r'')

    files = [e for e in os.listdir(img_root) if e.startswith('yn_gog2')]
    files = files[:200]
    
    tbar = tqdm(files, total=len(files), ncols=100)
    # for filename in os.listdir(img_root):
        # if not filename.startswith('yn_gog1'):
        #     continue
        
    
    for filename in tbar:
        basename = filename.rstrip('.tif')
        
        
        im_path = os.path.join(img_root, filename)
        vec_path= os.path.join(poly_root, basename+'.shp')

        if not os.path.isfile(im_path) or not os.path.isfile(vec_path):
            continue

        train_c(im_path, vec_path)
    
    train_c.dump_json()
    
    #---------------------------------------------------------------------------
    