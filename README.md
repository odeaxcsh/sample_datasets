
## About
This is a simple repository containing a few datasets and a few links as a starting point for the point cloud registration project.

### Requirements
Install requirements using `pip install -r requirements.txt` but if you got any errors try running `pip install networkx, open3d, numpy, tqdm` (we don't care about versions right now)


### Datasets
**How to use reconstruct.py**:
Run  `python reconstruct.py <Dataset> <Sequence> [--idx idx]` to visualize a dataset (if idx is not specified all the scans will be loaded)


**How to use dataloader.py**:

This is a simple dataloader that can be used to load the point clouds from the datasets provided here.
Import the class
```py
from dataloader import DatasetReader
dataroot = 'path/to/dataset'
dataset = ('7-Scenes', 'kitchen')
reader = DatasetReader(dataroot, dataset)
```

Get a pair of scans
```
P, Q, T = reader[i] # get the i-th pair of scans
```


Iterate over pairs of scans with adequate overlap
```py
for P, Q, T in reader:
    # point clouds P, Q and transformation T
    # P, Q: open3d.geometry.PointCloud
    # T: np.ndarray (4, 4) [R, t; 0, 1]
```


Iterate over each scan individually 
```py
reader = DatasetReader(dataroot, dataset, pcd_only=True)
for P, T in reader:
    # point cloud P and transformation T
    # P: open3d.geometry.PointCloud
    # T: np.ndarray (4, 4) [R, t; 0, 1]
```

List of datasets contained in this repo:
```py
datasets = [ # [(dataset_name, sequence_name), ...]

    ('7-Scenes', 'kitchen'),

    ('Sun3D', 'sun3d-home_at-home_at_scan1_2013_jan_1'),
    ('Sun3D', 'sun3d-mit_76_studyroom-76-1studyroom2'),
    ('Sun3D', 'sun3d-hotel_uc-scan3'),

    ('ETH', 'gazebo_summer'),
    ('ETH', 'wood_autmn'),
    ('ETH', 'gazebo_winter'),
    ('ETH', 'wood_summer'),


    *[
        ('RESSO', f'figure_{s}')
        for s in ['6b', '6e', '6f', '6g', '6h', '6i', '6j', '7a', '7b', '7c', '7d', '7e']
    ]
]

```

### Tutorials
Try to implement an registration algorithm to align the point clouds using open3d. You can use the dataloder to test your algorithm on different datasets.

Open3D documentation:
- [ICP Registration (refinement)](https://www.open3d.org/html/tutorial/pipelines/icp_registration.html)
- [Global Registration (initial/rough registration)](https://www.open3d.org/html/tutorial/pipelines/global_registration.html)


Finally if you are interested in learning more, you can check out the following too (very optional):
- [Multiway Registration (to register multiple point clouds together/reconstruction)](https://www.open3d.org/html/tutorial/pipelines/multiway_registration.html)


### Tasks
- Implement a rough registration algorithm to align the point clouds using open3d (Global Registration)
- Implement a refinement algorithm to improve the alignment using open3d (ICP Registration)
- Compare the results of the estimated transformation with the ground truth(T) and calculate the rotation and translation errors (use chatgpt for definition the error metric)
- Test your algorithm on different datasets
