import pyrootutils
import hydra
from omegaconf import DictConfig

pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from src import utils

logger = utils.get_pylogger()

@hydra.main(version_base="1.3", config_path = "../configs", config_name="train_nerf.yaml")
def main(cfg: DictConfig):
    logger.info("hello pytorch nerf..")


if __name__ == "__main__":
    main()