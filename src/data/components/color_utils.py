import cv2
from einops import rearrange
import imageio
import numpy as np
from typing import List
import multiprocessing
import time
import concurrent.futures

def cost_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} cost time:{time.perf_counter() - t:.8f} s')
        return result

    return fun

def srgb_to_linear(img):
    limit = 0.04045
    return np.where(img>limit, ((img+0.055)/1.055)**2.4, img/12.92)


def linear_to_srgb(img):
    limit = 0.0031308
    img = np.where(img>limit, 1.055*img**(1/2.4)-0.055, 12.92*img)
    img[img>1] = 1 # "clamp" tonemapper
    return img


def read_image(img_path: str, img_wh: tuple, blend_a: bool=True):
    img = imageio.imread(img_path).astype(np.float32)/255.0
    # img[..., :3] = srgb_to_linear(img[..., :3])
    if img.shape[2] == 4: # blend A to RGB
        if blend_a:
            img = img[..., :3]*img[..., -1:]+(1-img[..., -1:])
        else:
            img = img[..., :3]*img[..., -1:]

    img = cv2.resize(img, img_wh)
    img = rearrange(img, 'h w c -> (h w) c')

    return img_path,img

@cost_time
def read_image_mutil_proc(imgs_path: List, imgs_wh: List, blend_a: bool=True):
    pool = multiprocessing.Pool(processes = 10)
    result_list = list()
    img_dict = dict()
    for img_path, img_wh in zip(imgs_path, imgs_wh):
        result_list.append(pool.apply_async(read_image, (img_path, img_wh, blend_a,)))
    pool.close()
    pool.join()
    for result in result_list:
        k, v = result.get()
        print(k, v)
        img_dict[k] = v 
    return img_dict

@cost_time
def read_image_mutil_thread(imgs_path: List, imgs_wh: List, blend_a: bool=True):

    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        result_list = list()
        img_dict = dict()
        for img_path, img_wh in zip(imgs_path, imgs_wh):  # 模拟多个任务
            future = executor.submit(read_image, img_path, img_wh, blend_a,)
            result_list.append(future)
    
        for future in concurrent.futures.as_completed(result_list):  # 并发执行
            k, v = future.result()
            img_dict[k] = v 
            # print(k, v)
    return img_dict



if __name__ == "__main__":
    _, img = read_image("/data1/liangjun/codebase/torch-nerf/data/mipnerf360/garden/images/frame_00001.JPG", (5186, 3360))
    print(img.shape)

    imgs_path = ["/data1/liangjun/codebase/torch-nerf/data/mipnerf360/garden/images/frame_00001.JPG"]*64
    imgs_wh = [(5186, 3360)]*64
    # imgs_ret = read_image_mutil_proc(imgs_path, imgs_wh)

    imgs_ret = read_image_mutil_thread(imgs_path, imgs_wh)