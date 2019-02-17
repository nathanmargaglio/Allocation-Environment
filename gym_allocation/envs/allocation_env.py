import os, subprocess, time, signal
import numpy as np
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

import logging
logger = logging.getLogger(__name__)

class AllocationEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': []}
    
    def __init__(self, total_plows=6, max_accum=12, max_fall=6, max_forecast_var=3.,
                 plow_coef=10., plow_exp=1., accum_coef=1., accum_exp=2.,
                 removal_rate_mean=2., removal_rate_var=1, seed=None):
        
        self.total_plows = total_plows
        self.max_accum = max_accum
        self.max_fall = max_fall
        self.max_forecast_var = max_forecast_var
        
        self.plow_coef = plow_coef
        self.plow_exp = plow_exp
        self.accum_coef = accum_coef
        self.accum_exp = accum_exp
        
        self.removal_rate_mean = removal_rate_mean
        self.removal_rate_var = removal_rate_var
        
        self.observation_space = spaces.Box(low=0., high=1, shape=(4, ))
        self.action_space = spaces.Discrete(total_plows)
        
        if seed is not None:
            np.random.seed(seed)
        
    def reset(self):
        self.iteration = 0
        self.current_plows = 0.
        self.current_accum = 0.

        self.forecast_mean = np.random.choice(3)
        self.forecast_var = np.random.rand()
        
        self.last_reward = None
        self.removal_rate = None
        self.actual_fall = 0.
        
        return self.get_observation()
    
    def step(self, action):
        # what it actually snowed
        self.actual_fall = np.random.normal(self.forecast_mean, self.forecast_var)
        # the snow accumulates...
        self.current_accum += self.actual_fall
        # but the plows remove some of it
        self.removal_rate = np.random.normal(self.removal_rate_mean, self.removal_rate_var)
        self.current_accum -= self.removal_rate * self.current_plows
        if self.current_accum < 0:
            self.current_accum = 0
        
        reward = 0
        reward -= self.accum_coef * (self.current_accum**self.accum_exp)
        reward -= self.plow_coef * (self.current_plows**self.plow_exp)
        self.last_reward = reward
        
        self.current_plows = action
        self.forecast_mean = np.random.normal(self.max_fall/2, self.max_fall/2)
        self.forecast_var = np.random.rand() * self.max_forecast_var
        
        self.iteration += 1
        if self.iteration > 9:
            done = True
        else:
            done = False

        info = {}
        return self.get_observation(), reward, done, info
    
    def get_observation(self):
        return np.array([
            self.current_plows/self.total_plows,
            self.current_accum/self.max_accum,
            self.forecast_mean/self.max_fall,
            self.forecast_var/self.max_forecast_var
        ])
    
    def render(self, mode="text", **kwargs):
        print("Iteration:", self.iteration)
        print("Current Plows:", self.current_plows)
        print("Current Accumulation:", self.current_accum)
        print("Realized Fall:", self.actual_fall)
        print("Forecasted Mean:", self.forecast_mean)
        print("Forecasted Variance:", self.forecast_var)
        print("Reward:", self.last_reward)