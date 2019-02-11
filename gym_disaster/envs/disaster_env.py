import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

import logging
logger = logging.getLogger(__name__)

class DisasterEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': []}

    def __init__(self):
        self.observation_space = spaces.Box(low=-1, high=1,
                                            shape=(self.env.getStateSize()))
        # Action space omits the Tackle/Catch actions, which are useful on defense
        self.action_space = spaces.Tuple((spaces.Discrete(3),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1)))

    def step(self, action):
        observation = None
        reward = None
        done = None
        info = {}
        return ob, reward, done, info

    def reset(self):
        observation = None
        return observation

# ACTION_LOOKUP = {
#     0 : hfo_py.DASH,
#     1 : hfo_py.TURN,
#     2 : hfo_py.KICK,
#     3 : hfo_py.TACKLE, # Used on defense to slide tackle the ball
#     4 : hfo_py.CATCH,  # Used only by goalie to catch the ball
# }
