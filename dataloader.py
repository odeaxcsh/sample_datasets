

import open3d as o3d
import numpy as np
import networkx as nx

from tqdm import tqdm
from pathlib import Path
from io import StringIO


def estimateAbsTransformation(transformations):
    g = nx.DiGraph()
    for (i, j), T in transformations.items():
        g.add_edge(i, j, T=T)
        g.add_edge(j, i, T=np.linalg.inv(T))

    assert nx.is_weakly_connected(g), 'Graph is not strongly connected'
    root = sorted(g.nodes)[0]
    Ts = {root: np.eye(4)}
    for node in g.nodes:
        path = nx.shortest_path(g, root, node)
        T = np.eye(4)
        for j in range(len(path) - 1):
            T = T @ g[path[j]][path[j + 1]]['T']

        Ts[node] = T
    return Ts



class DatasetReader(object):
    def __init__(self, data_folder, dataset, name_only=False, pcd_only=False):
        self.dataset = dataset 
        self._data_folder = Path(data_folder)
        self._name_only = name_only
        self._pcd_only = pcd_only

        self._scans = {}
        name, sequence = dataset
        root = self._data_folder / name / sequence
        data = open(root / 'gt.log', 'r').readlines()
        n = len(data) // 5

        
        for i in range(n):
            idx1, idx2, m = [x for x in data[i * 5].split()]
            if name != 'KITTI':
                idx1, idx2 = int(idx1), int(idx2)
            
            self._scans[(idx1, idx2)] = np.loadtxt(
                StringIO(''.join(data[i * 5 + 1:i * 5 + 5]))
            )

        self._Ts = estimateAbsTransformation(self._scans)
        self._indices = sorted(self._Ts.keys())

    
    def __iter__(self, pbar=True):
        name, sequence = self.dataset
        frames = (self._Ts if self._pcd_only else self._scans).keys()
        inner_pbar = tqdm(sorted(frames), colour='blue') if pbar else iter(sorted(frames))
        
        for index in inner_pbar:
            if isinstance(index, int) or isinstance(index, str):
                index = [index]
            
            if pbar:
                inner_pbar.set_description(f'{name}/{sequence}/scan_{index}')

            if self._name_only:
                yield index
            
            else:
                yield self.get(*index)

    def get(self, idx1, idx2=None, reindex=False):
        name, sequence = self.dataset
        def read_pcd(root, cld, idx):
            if cld.endswith('.ply'):
                return o3d.io.read_point_cloud((root / cld.format(idx)).__str__())
            
            elif cld.endswith('.bin'):
                X = np.fromfile((root / cld.format(idx)).__str__(), dtype=np.float32)
                X = X.reshape(-1, 4)[:, :3]
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(X)
                return pcd

            
        if reindex:
            idx1 = self._indices[idx1]
            idx2 = self._indices[idx2]
        
        cld = {
            'RESSO': 'part{}.ply',
            'ETH': 'Hokuyo_{}.ply',
            'Sun3D': 'cloud_bin_{}.ply',
            '7-Scenes': 'cloud_bin_{}.ply',
            'KITTI': '{}.bin',
        }[name]

        root = self._data_folder / name / sequence
        feat1 = read_pcd(root, cld, idx1)
        T1 = self._Ts[idx1]
        
        if idx2 is None:
           return feat1, T1

        feat2 = read_pcd(root, cld, idx2)
        T2 = self._Ts[idx2]
        T = self._scans[(idx1, idx2)]

        return feat1, feat2, T
    

    def __len__(self):
        if self._pcd_only:
            return len(self._Ts)
        return len(self._scans)
    
    
    def __getitem__(self, idx):
        if self._pcd_only:
            return self.get(sorted(self._Ts.keys())[idx], reindex=False)
        
        idx1, idx2 = sorted(self._scans.keys())[idx]
        return self.get(idx1, idx2)

