import pyrootutils
import hydra
from omegaconf import DictConfig
import pytorch_lightning as L
from pytorch_lightning import LightningDataModule

pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from src import utils

logger = utils.get_pylogger()

class test:
    def __init__(self, name) -> None:
        self.name = name

@utils.task_wrapper
def train(cfg: DictConfig):
    # set seed for random number generators in pytorch, numpy and python.random
    if cfg.get("seed"):
        L.seed_everything(cfg.seed, workers=True)

    logger.info(f"Instantiating datamodule <{cfg.data._target_}>")
    datamodule: LightningDataModule = hydra.utils.instantiate(cfg.data)

    return {}, {}

@hydra.main(version_base="1.3", config_path = "../configs", config_name="train_nerf.yaml")
def main(cfg: DictConfig):
    logger.info("hello pytorch nerf..")
    utils.extras(cfg)
    my_test = test("test")
    logger.info(f"test name : {getattr(my_test, 'name')}")
    train(cfg)

if __name__ == "__main__":
    main()