import argparse, pathlib
from dataloader import DatasetReader

import open3d as o3d

parser = argparse.ArgumentParser()
parser.add_argument('--folder', type=str, default='./')
parser.add_argument('name', type=str, default='7-Scenes', nargs='?')
parser.add_argument('sequence', type=str, default='kitchen', nargs='?')
parser.add_argument('idx', type=int, default=None, nargs='?')
args = parser.parse_args()


name = args.name
sequence = args.sequence
data_folder = pathlib.Path(args.folder)

dataset = DatasetReader(data_folder, dataset=(name, sequence), pcd_only=True)

meshes = {}
points = []
lines = []

j = 0
previous = None
for i, (pcd, T) in enumerate(dataset):
    if args.idx is not None and i != args.idx:
        continue

    bbox = pcd.get_axis_aligned_bounding_box()
    min_box = min(bbox.get_max_bound() - bbox.get_min_bound())

    scale = min_box / 10
    mesh = o3d.geometry.TriangleMesh.create_coordinate_frame()
    mesh.scale(scale, center=mesh.get_center()).transform(T)
        
    meshes[i * 2] = pcd
    meshes[i * 2 + 1] = mesh
    pcd = pcd.transform(T)

    if previous is None:
        previous = mesh.get_center()
        continue

    p1 = previous
    p2 = mesh.get_center()

    points.append(p1)
    points.append(p2)
    lines.append([2 * j, 2 * j + 1])
    previous = mesh.get_center()
    j += 1
    

points = o3d.utility.Vector3dVector(points)
lines = o3d.utility.Vector2iVector(lines)

lineset = o3d.geometry.LineSet(
    points=points,
    lines=lines,
)

o3d.visualization.draw_geometries([*meshes.values(), lineset], window_name=f"{name} {sequence}")

