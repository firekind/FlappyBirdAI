import os
import glob
from pathlib import Path
from typing import Union, Tuple, List

import torch
import torch.nn as nn
import torch.optim as optim

class CheckpointManager:
    def __init__(self, name: str, out_dir: str, exp_name: str, frequency: int = 1, retain: int=5):
        self._name = name
        self._retain = retain
        self._out_home = os.path.join(out_dir, exp_name)
        self._checkpoints_dir = os.path.join(self._out_home, "checkpoints")
        self._is_resume = os.path.exists(self._checkpoints_dir)
        self._frequency = frequency

        # creating directory if it doesnt exist
        Path(self._checkpoints_dir).mkdir(parents=True, exist_ok=True)


        
    def save(self, module: nn.Module, optimizer: optim.Optimizer, frame: int, epsilon: float) -> None:
        # checking whether to checkpoint or not, based on frequency
        if frame % self._frequency != 0:
            return

        # removing old checkpoints, if present
        if frame - (self._retain * self._frequency) >= 0:
            try:
                os.remove(self._create_path(int(frame - (self._retain * self._frequency))))
            except FileNotFoundError:
                pass

        # constructing the data to save
        data = {
            'state_dict': module.state_dict(),
            'frame': frame,
            'optimizer': optimizer.state_dict(),
            'epsilon': epsilon
        }

        # saving the data
        torch.save(data, self._create_path(frame))

    def restore(self, module: nn.Module, optimizer: optim.Optimizer) -> Union[Tuple[None, None], Tuple[int, float]]:
        # getting files in the checkpoints folder
        files = self._get_files_in_dir()

        # if there are no files, return False
        if not files:
            return None, None

        # getting the latest checkpoint file
        checkpoint_file = files[0]

        # loading the data
        data = torch.load(checkpoint_file)

        # loading data to module and optimizer
        module.load_state_dict(data['state_dict'])
        optimizer.load_state_dict(data['optimizer'])

        # returning frame and epsilon
        return data['frame'], data['epsilon']
        

    def _get_files_in_dir(self) -> List[str]:
        # getting the files in the checkpoint folder
        files = [f for f in glob.glob(os.path.join(self._checkpoints_dir, self._name + "*")) if os.path.isfile(f)]

        # sorting files according to modification time
        files.sort(key=os.path.getmtime, reverse=True)

        return files

    def _create_path(self, frame: int) -> str:
        return os.path.join(
            self._checkpoints_dir,
            self._name + "_frame_" + str(frame) + ".pth.tar"
        )

    @property
    def out_dir(self):
        return self._out_home
    
    @property
    def checkpoints_dir(self):
        return self._checkpoints_dir
