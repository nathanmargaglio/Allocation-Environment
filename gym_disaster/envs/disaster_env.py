import os, subprocess, time, signal
import numpy as np
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

import logging
logger = logging.getLogger(__name__)

class DisasterEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': []}
    
    def __init__(self, total_plows=3, max_accum=12, max_fall=4,
                 plow_coef=1., accum_coef=1., removal_rate=2.):
        self.total_plows = total_plows
        self.max_accum = max_accum
        self.max_fall = max_fall
        self.plow_coef = plow_coef
        self.accum_coef = accum_coef
        self.removal_rate = removal_rate
        
        self.observation_space = spaces.Box(low=0., high=1, shape=(4, ))
        self.action_space = spaces.Discrete(total_plows)
        
    def reset(self):
        self.iteration = 0
        self.current_plows = 0.
        self.current_accum = 0.

        self.forecast_mean = np.random.choice(3)
        self.forecast_var = np.random.rand()
        
        observation = np.array([
            self.current_plows/self.total_plows,
            self.current_accum/self.max_accum,
            self.forecast_mean/self.max_fall,
            self.forecast_var
        ])
        
        self.last_reward = None
        self.actual_fall = 0.
        return observation
    
    def step(self, action):
        # what it actually snowed
        self.actual_fall = np.random.normal(self.forecast_mean, self.forecast_var)
        # the snow accumulates...
        self.current_accum += self.actual_fall
        # but the plows remove some of it
        self.current_accum -= self.removal_rate * self.current_plows
        if self.current_accum < 0:
            self.current_accum = 0
        
        reward = -self.accum_coef * self.current_accum - self.plow_coef * self.current_plows
        self.last_reward = reward
        
        self.current_plows = action
        self.forecast_mean = np.random.choice(3)
        self.forecast_var = np.random.rand()
        
        observation = np.array([
            self.current_plows/self.total_plows,
            self.current_accum/self.max_accum,
            self.forecast_mean/self.max_fall,
            self.forecast_var
        ])
        
        self.iteration += 1
        if self.iteration > 9:
            done = True
        else:
            done = False

        info = {}
        return observation, reward, done, info
    
    def render(self, mode="text", **kwargs):
        print("Iteration:", self.iteration)
        print("Current Plows:", self.current_plows)
        print("Current Accumulation:", self.current_accum)
        print("Realized Fall:", self.actual_fall)
        print("Forecasted Mean:", self.forecast_mean)
        print("Forecasted Variance:", self.forecast_var)
        print("Reward:", self.last_reward)