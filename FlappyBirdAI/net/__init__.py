import random
import logging
import argparse
from collections import deque
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn

from torchvision import transforms

from tensorboardX import SummaryWriter

import numpy as np

from game import Emulator
from net.utils import CheckpointManager

logger = logging.getLogger()

class Solver:
    # number of valid actions
    NUM_ACTIONS: int = 2

    def __init__(self, args: argparse.Namespace, checkpoint_mgr: CheckpointManager):
        # initializing args
        self.args = args

        # setting checkpoint manager
        self.checkpoint_mgr = checkpoint_mgr

        # enabling builtin cudnn auto tuner
        cudnn.benchmark = True

        # choosing device
        self.device = torch.device("cuda:0" if args.cuda else "cpu")
        
        # creating the model
        self.model: Model = Model(input_dim=(84, 84)).to(self.device)

        # optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=args.lr)

        # restoring checkpoint, if any
        self.start_frame, self.start_epsilon = checkpoint_mgr.restore(self.model, self.optimizer)

        # checking if the values returned by restoring checkpoint are None
        if self.start_frame is None:
            self.start_frame = 0
        if self.start_epsilon is None:
            self.start_epsilon = args.initial_epsilon

        # setting up connection to emulator
        self.emulator: Emulator = Emulator()

        # setting up replay memory size and replay memory
        self.max_replay: int = args.max_replay
        self.D: deque = deque()

        # loss function
        self.loss_func = F.mse_loss

        # constructing the transform, to pre process the image
        self.preprocess: transforms.Transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Grayscale(),
            transforms.Resize((84, 84)),
            transforms.ToTensor()
        ])

        # creating summary writer to log values
        self.writer = SummaryWriter(logdir=checkpoint_mgr.out_dir)

    def train_network(self) -> None:
        # Retrieving the first state by doing nothing:

        actions_t: torch.Tensor = torch.zeros(Solver.NUM_ACTIONS).to(self.device)
        actions_t[0] = 1 # setting the action to "no flap"
        
        # stepping the emulator
        frame: np.array
        frame, _, _, _ = self.emulator.step(actions_t.tolist())

        # preprocessing frame
        frame_p: torch.Tensor = self.preprocess(frame).to(self.device)

        # creating state_t, which is the preprocessed frame stacked
        # 4 times. Done to infer information such as velocity, etc.
        state_t: torch.Tensor = torch.stack([frame_p for _ in range(4)]).to(self.device)

        # initializing epsilon, the probability of selecting a random 
        # action
        epsilon: float = self.start_epsilon

        # initializing the count for frames
        num_frames: int = self.start_frame

        # initializing action index
        action_index: int = 0

        # initializing previous action index
        prev_action_index: int = 0

        # the list to store the minibatch
        minibatch: List[Tuple[torch.Tensor, torch.Tensor, float, torch.Tensor, bool]]

        logger.info("Observing game for %d frames...", self.args.observe_for)
        while True:
            # Populating replay memory:

            # forward passing the network, getting rewards for
            # each action
            output: torch.Tensor = self.model(state_t)

            # initializing actions array
            actions_t = torch.zeros(Solver.NUM_ACTIONS).to(self.device)
            
            # if an action can be performed in this frame
            if num_frames % self.args.frames_per_action == 0:
                if torch.rand(1) <= epsilon:
                    # choosing a random action
                    action_index = torch.randint(Solver.NUM_ACTIONS, (1,))

                else:
                    # choosing action with the highest reward
                    action_index = torch.argmax(output[-1])

                actions_t[action_index] = 1
            else:
                # previous action should be performed
                actions_t[prev_action_index] = 1

            # running action in the emulator
            reward_t: float
            is_terminal: bool
            frame, reward_t, is_terminal, score = self.emulator.step(actions_t.tolist())

            # pre processing frame
            frame_p: torch.Tensor = self.preprocess(frame).to(self.device)

            # constructing state_t1, by adding the new frame to the end
            # of the state_t and dropping the first frame in state_t
            state_t1: torch.Tensor = torch.cat((
                state_t[1:, :, :, :],
                frame_p.unsqueeze(0)  # adding new dimension at the beginning
            ), dim=0)

            # storing transition in replay memory
            # storing the last frame of state_t since the frame related to the reward should be stored. Similarily for state_t1.
            # Extra dimensions were added using unsqueeze function so that the list comprehension passed in torch.cat below 
            # gives a result with the correct shape
            self.D.append((state_t[-1].unsqueeze(0), actions_t.unsqueeze(0), reward_t, state_t1[-1].unsqueeze(0), is_terminal))

            # checking the size of the replay memory
            if len(self.D) >= self.args.max_replay:
                self.D.popleft()

            # training
            if num_frames > self.args.observe_for:
                # scaling epsilon down linearly
                if epsilon > self.args.final_epsilon:
                    epsilon -= (self.args.initial_epsilon - self.args.final_epsilon) / self.args.explore

                # sampling a minibatch from replay memory
                minibatch = random.sample(self.D, self.args.batch_size)

                # extracting the variables from batch
                state_ts: torch.Tensor = torch.cat([d[0] for d in minibatch]) # converting tuple of tensors to tensor of tensors
                actions_ts: torch.Tensor = torch.cat([d[1] for d in minibatch])
                reward_ts: List[float] = [d[2] for d in minibatch]
                state_t1s: torch.Tensor = torch.cat([d[3] for d in minibatch])
                is_terminals: List[bool] = [d[4] for d in minibatch]

                # initializing variable to store optimal values
                y: torch.Tensor = torch.Tensor().to(self.device)

                # performing a forward pass on the state_ts, getting the rewards
                # for all actions
                out_state_ts: torch.Tensor = self.model(state_ts)

                # performing a forward pass on the state_t1s, getting the rewards
                # for all actions
                out_state_t1s: torch.Tensor = self.model(state_t1s)

                # calculating the optimal rewards
                for i in range(self.args.batch_size):

                    # if the state is a terminal state, the optimal reward
                    # is the terminal reward
                    if is_terminals[i]:
                        y = torch.cat((
                            y,
                            torch.Tensor([reward_ts[i]]).to(self.device) # converting reward value to tensor
                        ))

                    # else, the optimal reward is given by:
                    # reward_j + gamma * max(Q(state_j1))
                    else:
                        y = torch.cat((
                            y,
                            reward_ts[i] + self.args.gamma * torch.max(out_state_t1s[i], dim=0, keepdim=True)[0]
                        ))
                
                # out_state_ts contains rewards for all the possible actions, hence a 
                # multidimensional array (in this case, shape: [batch_size, 2]). However,
                # the optimal rewards, y, is calculated only for the chosen action, 
                # and thus, a linear array (in this case, shape: [batch_size]). To 
                # get the rewards for the actions that were performed, the out_state_ts
                # is multiplied with actions_ts (since actions_ts contains only 1's and 0's,
                # 1 when an action is performed and 0 when it is not, only the reward for the
                # performed action will remain in the final product, the other element will 
                # be 0.) and summed row wise, producing the required 1D array.
                reduced_out_state_ts: torch.Tensor = torch.sum(out_state_ts * actions_ts, dim=1)

                # calculating loss
                loss = self.loss_func(reduced_out_state_ts, y)

                # computing gradients
                loss.backward()

                # stepping optimizer
                self.optimizer.step()

                # checkpointing
                self.checkpoint_mgr.save(module=self.model, optimizer=self.optimizer, frame=num_frames, epsilon=epsilon)

                # logging
                if num_frames % self.args.log_freq == 0:
                    logger.info(
                        "Frame: %d, epsilon: %.4f, action: %s, reward: %d, Q value: %.4f",
                        num_frames, epsilon, "'flap'" if action_index == 1 else "'no flap'",
                        reward_t, torch.max(output)
                    )

                # logging summary
                if num_frames % self.args.summary_freq == 0:
                    self.writer.add_scalar("loss", loss, num_frames)
                    self.writer.add_scalar("reward", np.mean(reward_ts), num_frames)
                    self.writer.add_scalar("score", score)

            # updating variables
            num_frames += 1
            state_t = state_t1
            prev_action_index = action_index


class Model(nn.Module):
    """
    The module for the network.
    """

    def __init__(self, input_dim: Tuple[int, int]):
        super(Model, self).__init__()
        self.convnet: nn.Sequential = nn.Sequential(
            nn.Conv2d(1, 16, (8, 8), stride=4),
            nn.ReLU(),
            nn.Conv2d(16, 32, (4, 4), stride=2),
            nn.ReLU(),
        )

        # computing the final width of the image after the convolutional layers
        # function is called two times as there are two conv2d layers
        width_convnet_out = self._conv2d_size_out(self._conv2d_size_out(input_dim[0], 8, 4), 4, 2)

        # computing the final height of the image after the convolutional layers
        # function is called two times as there are two conv2d layers
        height_convnet_out = self._conv2d_size_out(self._conv2d_size_out(input_dim[1], 8, 4), 4, 2)

        self.densenet: nn.Sequential = nn.Sequential(
            Flatten(),
            nn.Linear(32 * width_convnet_out * height_convnet_out, 256),
            nn.Linear(256, 2)
        )

    def _conv2d_size_out(self, size, kernel_size, stride):
            return (size - (kernel_size - 1) - 1) // stride  + 1

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

class Flatten(nn.Module):
    def __init__(self):
        super(Flatten, self).__init__()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x.view(x.size(0), -1)