import os
import torch

try:
    from .base_dataset import BaseDataSet
    from .ray_utils import *
    from .colmap_utils import (read_images_binary, 
                               read_points3d_binary, 
                               read_cameras_binary)
except:
    from base_dataset import BaseDataSet
    from ray_utils import *
    from colmap_utils import (read_images_binary, 
                               read_points3d_binary, 
                               read_cameras_binary)

class ColmapDataset(BaseDataSet):
    def __init__(
            self,
            data_dir: str = "",
            data_type: str = "train",
            downscale: int = 1
    ) -> None:
        super().__init__(data_dir, data_type, downscale)
        self.read_intrinsics()
        self.read_extrinsics()

    def read_intrinsics(self):
        """读取相机内参,假定所有照片内参一样

        Returns:
            _type_: _description_
        """
        camera_data = read_cameras_binary(os.path.join(self.data_dir, "sparse/0/cameras.bin"))
        camera_w = int(camera_data[1].width/self.downscale)
        camera_h = int(camera_data[1].height/self.downscale)
        self.img_wh = (camera_w, camera_h)

        if camera_data[1].model in ("SIMPLE_RADIAL"):
            fx = fy = camera_data[1].params[0]/self.downscale
            cx = camera_data[1].params[1]/self.downscale
            cy = camera_data[1].params[2]/self.downscale
        elif camera_data[1].model in ("PINHOLE", "OPENCV"):
            fx = camera_data[1].params[0]/self.downscale
            fy = camera_data[1].params[1]/self.downscale
            cx = camera_data[1].params[2]/self.downscale
            cy = camera_data[1].params[3]/self.downscale
        else:
            raise ValueError(f"Please parse the intrinsics for camera model {camera_data[1].model}!")
        
        # 相机内参
        self.K = torch.FloatTensor([[fx, 0, cx],
                                    [0,  fy, cy],
                                    [0,  0,  1]
                                    ])
        self.directions = get_ray_directions(camera_h, camera_w, self.K)

    def read_extrinsics(self):
        """读取相机外参
            * camera2world transform matrix
            * 3d point position
            * ray attributes, eg: color
        """
        images_data = read_images_binary(os.path.join(self.data_dir, "sparse/0/images.bin"))
        images_name = [images_data[i].name for i in images_data]
        imgs_idx = np.argsort(images_name)
        if self.downscale != 1:
            folder = f"images_{self.downscale}"
        else:
            folder = "images"
        self.sorted_images_path = [
            os.path.join(self.data_dir, folder, name) for name in sorted(images_name)
        ]
        
        # load camera pose
        w2c_mats = [] # word2camera transform matrix
        bottom = np.array([[0, 0, 0, 1]])
        for k in images_data:
            R = images_data[k].qvec2rotmat()
            t = images_data[k].tvec.reshape(3, 1)
            w2c_mats += [np.concatenate([np.concatenate([R, t], 1), bottom], 0)]
        w2c_mats = np.stack(w2c_mats, 0)
        poses = np.linalg.inv(w2c_mats)[imgs_idx, :3]  # N*3*4

        # load point3D
        points3d_data = read_points3d_binary(os.path.join(self.data_dir, "sparse/0/points3D.bin"))
        points3d = np.stack([points3d_data[k].xyz for k in points3d_data], 0)

        self.poses, self.points3d = center_poses(poses, points3d)
        scale = np.linalg.norm(self.poses[..., 3]).min()
        self.poses /= scale
        self.points3d /= scale
        self.poses = torch.FloatTensor(self.poses) 



if __name__ == "__main__":
    colmap_dataset = ColmapDataset(data_dir="/data1/liangjun/codebase/torch-nerf/data/mipnerf360/garden")
    # colmap_dataset.ray_sampling_trategy = "single_image"
    colmap_dataset.data_type = "train"
    for i in range(10):
        print(colmap_dataset[i])
    # print(colmap_dataset.K)
    # print(colmap_dataset.directions)