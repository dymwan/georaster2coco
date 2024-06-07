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
TRAIN_IMAGES_DIRECTORY = r'\\172.24.83.111\share2\dymwan\ARCHIVED\coco\train\images'
MC_ANNOTATION_SMALL_PATH = r'\\172.24.83.111\share2\dymwan\ARCHIVED\coco\train\annotation.json'
coco = COCO(MC_ANNOTATION_SMALL_PATH)


category_ids = coco.loadCats(coco.getCatIds())
print(category_ids)

image_ids = coco.getImgIds(catIds=coco.getCatIds())

random_image_id = random.choice(image_ids)

# img = coco.loadImgs(random_image_id)[0]
img = coco.loadImgs(random_image_id)[0]

print(img)

image_path = os.path.join(TRAIN_IMAGES_DIRECTORY, img["file_name"])
I = io.imread(image_path)


annotation_ids = coco.getAnnIds(imgIds=img['id'])
annotations = coco.loadAnns(annotation_ids)

print(annotations)

plt.imshow(I); plt.axis('off')
coco.showAnns(annotations)

plt.show()