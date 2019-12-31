import torch
import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
    """
    The module for the network.
    """

    def __init__(self):
        super(nn.Module, self).__init__()
        self.convnet: nn.Sequential = nn.Sequential(
            nn.Conv2d(4, 16, (8, 8), stride=4),
            nn.ReLU(),
            nn.Conv2d(16, 32, (4, 4), stride=2),
            nn.ReLU(),
        )

        self.densenet: nn.Sequential = nn.Sequential(
            nn.Linear(32, 256),
            nn.Linear(256, 2)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Performs forward pass.
        
        Args:
            x (torch.Tensor): The input image
        
        Returns:
            torch.Tensor: The output of the network
        """

        conv_out = self.convnet(x)
        return self.densenet(conv_out)