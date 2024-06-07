# georaster2coco

## Tutorial
This repo. has two key scripts to convert or visualize. If you need customize your
own georaster dataset to [MS-COCO format](http://cocodataset.org/#home).


## Usage

### `class geo2cocoConvertor`
The `class geo2cocoConvertor` should be initialized firstly by following parameters:
- `dst_root`: the dataset root, in which the internal structure is:  
$\qquad$    |---root <br />
$\qquad$    &emsp;&emsp;|---images<br />
$\qquad$    &emsp;&emsp;| $\qquad$   &emsp;&emsp;|—00001.png<br />
$\qquad$    &emsp;&emsp;| $\qquad$   &emsp;&emsp;|—00002.png<br />
$\qquad$    &emsp;&emsp;| $\qquad$   &emsp;&emsp;|— ...<br />
$\qquad$    &emsp;&emsp;|—annotations.json<br />


- `clip_size`: to crop the raster image and relating vector to patch. Defaual is `None` which means DO NOT clip.

- `clip_stride`: Available if `clip_size` is not `None`. Controls the shifting stride of the window to clip.

- `suffix`: The suffix of the output raster patch, defaul as `'jpg'`

- `prefix`: The prefix of the ouput raster files, defual as `''`

### `coco_utils`

To visualize the dataset, and the demo is listed:
<table>
    <tr>
        <td ><center><img src="figures/001258.png" ></center></td>
        <td ><center><img src="figures/003970.png" ></center></td>
        <td ><center><img src="figures/006498.png" ></center></td>
        <td ><center><img src="figures/005208.png" ></center></td>
        <td ><center><img src="figures/008580.png" ></center></td>
    </tr>
    <tr>
        <td ><center><img src="figures/004245.png" ></center></td>
        <td ><center><img src="figures/006151.png"></center> </td>
        <td ><center><img src="figures/009019.png"></center> </td>
        <td ><center><img src="figures/006893.png"></center> </td>
        <td ><center><img src="figures/005090.png"></center> </td>
    </tr>
    <tr>
        <td ><center><img src="figures/009524.png" ></center></td>
        <td ><center><img src="figures/004489.png"></center> </td>
        <td ><center><img src="figures/003179.png"></center> </td>
        <td ><center><img src="figures/000649.png"></center> </td>
        <td ><center><img src="figures/002674.png"></center> </td>
    </tr>
</table>

# TODO
Enrich.