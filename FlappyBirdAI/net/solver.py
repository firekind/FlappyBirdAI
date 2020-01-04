import random
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn

from torchvision import transforms

import numpy as np

from net import Model
from game import GameState

class Solver:
    # number of valid actions
    NUM_ACTIONS: int = 2

    def __init__(self, args):
        # initializing args
        self.args = args

        # enabling builtin cudnn auto tuner
        cudnn.benchmark = True
        
        # creating the model
        self.model: Model = Model()

        # setting up connection to emulator
        self.emulator: GameState = GameState()

        # setting up replay memory size and replay memory
        self.max_replay: int = args.max_replay
        self.D: deque = deque()

        # loss function
        self.loss_func = F.mse_loss

        # optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=args.lr)

        # constructing the transform, to pre process the image
        self.preprocess: transforms.Transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Grayscale(),
            transforms.Resize((84, 84)),
            transforms.ToTensor()
        ])

        


    def train_network(self) -> None:
        # Retrieving the first state by doing nothing:

        actions_t: torch.Tensor = torch.zeros(Solver.NUM_ACTIONS)
        actions_t[0] = 1 # setting the action to "not flap"
        
        # stepping the emulator
        frame, _, _ = self.emulator.step(actions_t.tolist())

        # preprocessing frame
        frame_p = self.preprocess(frame)

        # creating state_t, which is the preprocessed frame stacked
        # 4 times. Done to infer information such as velocity, etc.
        state_t = torch.stack([frame_p for _ in range(4)])

        # initializing epsilon, the probability of selecting a random 
        # action
        epsilon = self.args.initial_epsilon

        # initializing the count for frames
        num_frames = 0

        # initializing action index
        action_index = 0

        # initializing previous action index
        prev_action_index = 0
    
        while True:
            # Populating replay memory:

            # forward passing the network, getting rewards for
            # each action
            output = self.model(state_t)

            # initializing actions array
            actions_t = torch.zeros(Solver.NUM_ACTIONS)
            
            # if an action can be performed in this frame
            if num_frames % self.args.frames_per_action == 0:
                if torch.rand(1) <= epsilon:
                    # choosing a random action
                    action_index = torch.randint(Solver.NUM_ACTIONS, (1,))

                else:
                    # choosing action with the highest reward
                    action_index = torch.argmax(output)

                actions_t[action_index] = 1
            else:
                # previous action should be performed
                actions_t[prev_action_index] = 1

            # running action in the emulator
            frame, reward_t, is_terminal = self.emulator.step(actions_t.tolist())

            # pre processing frame
            frame_p = self.preprocess(frame)

            # constructing state_t1, by adding the new frame to the end
            # of the state_t and dropping the first frame in state_t
            state_t1 = torch.cat((
                state_t[1:, :, :, :],
                frame_p.unsqueeze(0)  # adding new dimension at the beginning
            ), dim=0)

            # storing transition in replay memory
            self.D.append((state_t, actions_t, reward_t, state_t1, is_terminal))
            
            # checking the size of the replay memory
            if len(self.D) > self.args.max_replay:
                self.D.popleft()

            # training
            if num_frames > self.args.observe_for:
                # scaling epsilon down linearly
                if epsilon > self.args.final_epsilon:
                    epsilon -= (self.args.initial_epsilon - self.args.final_epsilon) / self.args.explore

                # sampling a minibatch from replay memory
                batch = random.sample(self.D, self.args.batch_size)

                # extracting the variables from batch
                state_ts, actions_ts, reward_ts, state_t1s, is_terminals = zip(*batch)

                # initializing variable to store optimal values
                y = torch.FloatTensor()

                # performing a forward pass on the state_ts, getting the rewards
                out_state_ts = self.model(state_ts)

                # performing a forward pass on the state_t1s, getting the rewards
                out_state_t1s = self.model(state_t1s)

                # calculating the optimal rewards
                for i in self.args.batch_size:

                    # if the state is a terminal state, the optimal reward
                    # is the terminal reward
                    if is_terminals[i]:
                        y = torch.cat((
                            y,
                            torch.Tensor([reward_ts[i]]) # converting reward value to tensor
                        ))

                    # else, the optimal reward is given by:
                    # reward_j + gamma * max(Q(state_j1))
                    else:
                        y = torch.cat((
                            y,
                            reward_ts + self.args.gamma * torch.max(out_state_t1s[i])
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
                reduced_out_state_ts = torch.sum(out_state_ts * actions_ts, dim=1)

                # calculating loss
                loss = self.loss_func(reduced_out_state_ts, y)

                # computing gradients
                loss.backward()

                # stepping optimizer
                self.optimizer.step()

                # updating variables
                num_frames += 1
                state_t = state_t1
                prev_action_index = action_index

