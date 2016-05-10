#Here comes the physics engine (by Olga)
import numpy as np
from math import pi
from kilobot import Kilobot

class World:
  
    @classmethod
    def initialize(cls, swarmSize, robotRadius, sensorRadius, velocity, tick=100):
        """
        tick is miliseconds between updates
        """
        cls.swarmSize = swarmSize
        cls.radius = robotRadius
        cls.sensor = sensorRadius
        cls.tick = tick
        cls.avgVelocity = velocity

        cls.positions = cls.makeInitialFormation(50, 10, 10)
        cls.orientations = np.random.rand(2, swarmSize) * 2 * pi #angle with X axes
        cls.robots = []
        for i in xrange(swarmSize):
            cls.robots.append(Kilobot(i, None, radius=robotRadius))

        noise = np.random.randn(swarmSize) * velocity * 0.1 # sigma is 10% of velocity
        cls.velocities = np.fmax(velocity + noise, np.zeros((swarmSize))) #to aviod negative velocities
        
        cls.distances = np.array((swarmSize, swarmSize))
        cls.updateDistances()

        cls.inSensorRadius = np.zeros((swarmSize, swarmSize))
        cls.updateInSensorRadius()


    @classmethod
    def makeInitialFormation(cls, firstDim, offsetX, offsetY):
        swarmPos = np.zeros((2, cls.swarmSize))
        shiftX = cls.radius * 1.2
        shiftY = (3**0.5) * cls.radius * 1.2
        x = 0
        y = 0
        row = 1
        for i in xrange(cls.swarmSize):
            swarmPos[0, i] = x
            swarmPos[1, i] = y
            
            if (i+1) % firstDim == 0:
                row += 1
                y += shiftY
                x = shiftX if row%2==0 else 0
            else:
                x += 2 * shiftX

        #move
        swarmPos[0,:] += offsetX
        swarmPos[1,:] += offsetY

        return swarmPos


    @classmethod
    def updateDistances(cls):
        z = np.array([[complex(cls.positions[0,i], cls.positions[1,i]) for i in range(cls.positions.shape[1])]])
        cls.distances = abs(z.T - z)


    @classmethod
    def updateInSensorRadius(cls):
        #TODO: replace, very slow
        cls.inSensorRadius = np.zeros((cls.swarmSize, cls.swarmSize))
        for i in range(cls.distances.shape[0]):
            for j in range(i, cls.distances.shape[1]):
                if cls.distances[i,j] <= cls.sensor:
                    cls.inSensorRadius[i,j] = 1
                    cls.inSensorRadius[j,i] = 1


    @classmethod
    def updateEstimatedPositions():
        #
        pass

    @classmethod
    def updateWorld(cls):
        """
        this method is called each iteration from the main simulation loop
        """
        #TODO: ask all robots to make a move

        #TODO: update their positions
        
        #update distances
        cls.updateDistances()

        #update in sensor radius matrix
        #cls.updateInSensorRadius()

        return cls.positions

    @classmethod
    def scan(cls, kilobot_id):
        """
        This method should be called by the kilobots to receive information
        about their neighbors.

        Returns list of tuples where each tuple has (d, (x,y), grad_val, stationary).
        (x,y) may be None and stationary is either True or False.

        """

        return []
        