from pycocotools.coco import COCO
from pycocotools import mask as cocomask
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
import pylab
import random
import os



# TRAIN_IMAGES_DIRECTORY = r'D:\ThirdPartyDataset\val\images'
# MC_ANNOTATION_SMALL_PATH = r'D:\ThirdPartyDataset\val\annotation-small.json'
TRAIN_IMAGES_DIRECTORY = r'\\172.24.83.111\share2\dymwan\ARCHIVED\coco\mapping_challenge_dataset\raw\train\images'
MC_ANNOTATION_SMALL_PATH = r'\\172.24.83.111\share2\dymwan\ARCHIVED\coco\mapping_challenge_dataset\raw\train\annotation.json'
SAMPLE_NUM = 20
DST_FOLDER = r'D:\MyGitHub\georaster2coco-master\georaster2coco\figures'

coco = COCO(MC_ANNOTATION_SMALL_PATH)


category_ids = coco.loadCats(coco.getCatIds())


image_ids = coco.getImgIds(catIds=coco.getCatIds())


for i in range(SAMPLE_NUM):
    
    
    random_image_id = random.choice(image_ids)
    
    dst_path = os.path.join(DST_FOLDER, '{:0>6d}.png'.format(random_image_id))
    
    img = coco.loadImgs(random_image_id)[0]
    
    image_path = os.path.join(TRAIN_IMAGES_DIRECTORY, img["file_name"])
    I = io.imread(image_path)

    annotation_ids = coco.getAnnIds(imgIds=img['id'])
    annotations = coco.loadAnns(annotation_ids)

    plt.imshow(I); plt.axis('off')
    coco.showAnns(annotations)
    plt.tight_layout()
    plt.savefig(dst_path, dpi=500, bbox_inches = 'tight')
    plt.clf()

# random_image_id = random.choice(image_ids)


# img = coco.loadImgs(random_image_id)[0]
# imgs = coco.loadImgs(random_image_id)



# image_path = os.path.join(TRAIN_IMAGES_DIRECTORY, img["file_name"])
# I = io.imread(image_path)


# annotation_ids = coco.getAnnIds(imgIds=img['id'])
# annotations = coco.loadAnns(annotation_ids)

# print(annotations)

# plt.imshow(I); plt.axis('off')
# coco.showAnns(annotations)

# plt.show()