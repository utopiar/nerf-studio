from torch.utils.data import Dataset
import numpy as np
try:
    from .color_utils import read_image
except:
    from color_utils import read_image
import torch

class BaseDataSet(Dataset):
    def __init__(
            self,
            data_dir: str = "",
            data_type: str = "train",
            downscale: int = 1
    ):
        self.data_dir = data_dir
        self.data_type = data_type
        self.downscale = downscale
        self.ray_sampling_trategy = "all_image" #[all_image, single_image]
        self.batch_size = 64
    
    def __len__(self):
        if self.data_type == "train":
            return 1000
        else:
            return len(self.poses)

    def __getitem__(self, index: int):
        # 为了支持训练时加载图片，目前仅从单一图片中采样
        if self.data_type == "train":
            # if self.ray_sampling_trategy == "all_image":
            #     # 每次训练从所有图片抽样射线
            #     img_idxs = np.random.choice(len(self.poses), self.batch_size)
            # elif self.ray_sampling_trategy == "single_image":
            #     # 每次训练仅从一张图片抽样射线
            #     img_idxs = np.random.choice(len(self.poses), 1)
            img_idxs = np.random.choice(len(self.poses), 1)
            # print(img_idxs)
            imgs_path = [self.sorted_images_path[idx] for idx in img_idxs]
            print(imgs_path)
            rays = []
            for img_path in imgs_path:
                buf = []
                _, img = read_image(img_path, self.img_wh, blend_a=False)
                img = torch.FloatTensor(img)
                buf += [img]

                rays += [torch.cat(buf, 1)]
            rays = torch.stack(rays)

            pix_idxs = np.random.choice(self.img_wh[0]*self.img_wh[1], self.batch_size)
            sample = {'img_idxs': img_idxs, 'pix_idxs': pix_idxs,
                      'rgb': rays}

        else:
            sample = {'pose': self.poses[index], 'img_idxs': index}
            if len(self.sorted_images_path)>0: # if ground truth available
                img_path = self.sorted_images_path[index]
                _, img = read_image(img_path, self.img_wh, blend_a=False)
                rays = img
                sample['rgb'] = rays[:, :3]
                if rays.shape[1] == 4: # HDR-NeRF data
                    sample['exposure'] = rays[0, 3]

        return sample


    def read_intrinsics(self):
        """read camera intrinsics
        """
        raise NotImplementedError
    

if __name__ == "__main__":
    _ = BaseDataSet()