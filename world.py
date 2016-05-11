#Here comes the physics engine (by Olga)
import numpy as np
from math import pi
from kilobot import Kilobot

class World:

    def __init__(self, swarmSize, robotRadius, sensorRadius, velocity, tick=100):
        """
        tick is miliseconds between updates
        """
        self.swarmSize = swarmSize
        self.fullSwarmSize = self.swarmSize + 4
        self.radius = robotRadius
        self.sensor = sensorRadius
        self.tick = tick
        self.avgVelocity = velocity

        self.initialFormationWidth = 35
        self.initialFormationOffsetX = -30
        self.initialFormationOffsetY = 0

        self.robots = []
        #add 4 source robots
        source = self.computeSourceRobotsPositions()
        self.robots.append(Kilobot(0, None, self, (source[:,0]), grad_val=0, radius=robotRadius))
        for i in xrange(1, 4):
            self.robots.append(Kilobot(i, None, self, (source[:,i]),grad_val=1, radius=robotRadius))

        self.positions = np.hstack((source, self.makeInitialFormation()))

        #shift everything so that source is at (0,0)
        self.positions = (self.positions.T - self.positions[:,0].T).T
        
        for i in xrange(4, self.fullSwarmSize):
            self.robots.append(Kilobot(i, None, self, radius=robotRadius))

        self.colors = ['green'] * 4 + ['blue'] * self.swarmSize
        
        self.orientations = np.random.rand(2, self.fullSwarmSize) * 2 * pi #angle with X axes

        noise = np.random.randn(self.fullSwarmSize) * velocity * 0.1 # sigma is 10% of velocity
        self.velocities = np.fmax(velocity + noise, np.zeros((self.fullSwarmSize))) #to aviod negative velocities
        
        self.distances = np.array((self.fullSwarmSize, self.fullSwarmSize))
        self.updateDistances()

        self.inSensorRadius = np.zeros((self.fullSwarmSize, self.fullSwarmSize))
        self.updateInSensorRadius()

        self.estimatedPositions = []
        self.askInfo()


    def makeInitialFormation(self):
        swarmPos = np.zeros((2, self.swarmSize))
        shiftX = self.radius * 1.2
        shiftY = (3**0.5) * self.radius * 1.2
        x = 0
        y = 0
        row = 1
        for i in xrange(self.swarmSize):
            swarmPos[0, i] = x
            swarmPos[1, i] = y
            
            if (i+1) % self.initialFormationWidth == 0:
                row += 1
                y -= shiftY
                x = shiftX if row%2==0 else 0
            else:
                x += 2 * shiftX

        #move
        swarmPos[0,:] += self.initialFormationOffsetX
        swarmPos[1,:] += self.initialFormationOffsetY

        return swarmPos


    def computeSourceRobotsPositions(self):
        source = np.zeros((2, 4))
        shiftX = self.radius * 1.2
        shiftY = (3**0.5) * self.radius * 1.2

        source[0,0] = self.initialFormationOffsetX
        source[1,0] = self.initialFormationOffsetY + 2 * shiftY

        source[0,1] = source[0,0] + 2 * shiftX
        source[1,1] = source[1,0]

        source[0,2] = source[0,0] + shiftX
        source[1,2] = source[1,0] + shiftY

        source[0,3] = source[0,0] + shiftX
        source[1,3] = source[1,0] - shiftY

        return source


    def updateDistances(self):
        z = np.array([[complex(self.positions[0,i], self.positions[1,i]) for i in range(self.positions.shape[1])]])
        self.distances = abs(z.T - z)


    def updateInSensorRadius(self):
        self.inSensorRadius = self.sensor - self.distances
        self.inSensorRadius = np.fmax(self.inSensorRadius, np.zeros((self.fullSwarmSize, self.fullSwarmSize)))
        self.inSensorRadius = np.array(self.inSensorRadius, dtype=bool)



    def askInfo(self):
        self.estimatedPositions = []
        self.gradients = []
        self.stationarity = []
        for i in xrange(self.fullSwarmSize):
            self.estimatedPositions.append(self.robots[i].pos)
            self.gradients.append(self.robots[i].grad_val)
            self.stationarity.append(self.robots[i].stationary)


    def updateWorld(self):
        """
        this method is called each iteration from the main simulation loop
        """
        #TODO: ask all robots to make a move
        for i in xrange(self.fullSwarmSize):
            self.robots[i].move()

        #TODO: update their positions
        
        #update distances
        self.updateDistances()

        #update in sensor radius matrix
        self.updateInSensorRadius()

        #ask robots for (x,y), grad_val, stationary
        self.askInfo()

        return self.positions

    def scan(self, kilobot_id):
        """
        This method should be called by the kilobots to receive information
        about their neighbors.

        Returns list of tuples where each tuple has (d, (x,y), grad_val, stationary).
        (x,y) may be None and stationary is either True or False.

        """
        indicesInRange = np.nonzero(self.inSensorRadius[kilobot_id,:])[0]
        scanData = []
        for ind in indicesInRange:
            if ind != kilobot_id:
                neihbourData = (self.distances[kilobot_id, ind], self.estimatedPositions[ind], self.gradients[ind], self.stationarity[ind])
                scanData.append(neihbourData)
        
        return scanData
        
