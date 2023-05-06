from lightning import LightningDataModule
from typing import Tuple
from torch.utils.data import Dataset, DataLoader
from lightning.pytorch.utilities.types import EVAL_DATALOADERS, TRAIN_DATALOADERS
import torch

class ColmapDataModule(LightningDataModule):
    def __init__(
            self,
            data_set: Dataset,
            train_val_test_split: Tuple[int, int, int] = (55_000, 5_000, 10_000),
            batch_size: int = 64,
            num_workers: int = 0,
            pin_memory: bool = False
    ) -> None:
        super().__init__()
        self.save_hyperparameters(logger=False)
        print(f"data dir: {self.hparams}")

    
    def prepare_data(self):
        # download data, only called on 1GPU/TPU
        pass

    def setup(self, stage):
        # split  val/train/test data
        pass

    def train_dataloader(self) -> TRAIN_DATALOADERS:
        return DataLoader(self.hparams.data_set, 
                          self.hparams.batch_size,
                          num_workers=16,
                          persistent_workers=True,
                          batch_size=None,
                          pin_memory=True)
    
    def val_dataloader(self) -> EVAL_DATALOADERS:
        return super().val_dataloader()

    def test_dataloader(self) -> EVAL_DATALOADERS:
        return super().test_dataloader()
    
    def teardown(self, stage: str) -> None:
        return super().teardown(stage)