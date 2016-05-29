#Here comes the physics engine (by Olga)
import numpy as np
from math import pi, sin, cos, sqrt
from kilobot2 import Kilobot
from bitmap import BitMap

class World:

    def __init__(self, bitmap, swarmSize, shape_width, robotRadius, sensorRadius, velocity, ang_vel=3, tick=100):
        """
        tick is miliseconds between updates
        """
        self.time = 0
        self.bitmap = bitmap
        self.swarmSize = swarmSize
        self.fullSwarmSize = self.swarmSize + 4
        self.radius = robotRadius
        self.sensor = sensorRadius
        self.tick = tick
        origin = bitmap.origin
        self.initialFormationWidth = shape_width
        self.initialFormationOffsetX = 0#origin[0]
        self.initialFormationOffsetY = 0#origin[1]

        self.robots = []
        #add 4 source robots
        source = self.computeSourceRobotsPositions()
        self.robots.append(Kilobot(0, bitmap, self, (source[:,0]), grad_val=0, radius=robotRadius))
        for i in xrange(1, 4):
            self.robots.append(Kilobot(i, bitmap, self, (source[:,i]),grad_val=1, radius=robotRadius))

        self.positions = np.hstack((source, self.makeInitialFormation()))

        #shift everything so that source is at (0,0)
        #self.positions = (self.positions.T - self.positions[:,0].T).T
        
        for i in xrange(4, self.fullSwarmSize):
            self.robots.append(Kilobot(i, bitmap, self, radius=robotRadius))

        self.colors = [0] * self.fullSwarmSize
        
        self.orientations = np.hstack((np.ones((4))*pi/2, np.random.rand(self.swarmSize) * 2 * pi)) #angle with X axes

        #noise = np.random.randn(self.fullSwarmSize) * velocity * 0.1 # sigma is 10% of velocity
        #self.velocities = np.fmax(velocity + noise, np.zeros((self.fullSwarmSize))) #to aviod negative velocities
        self.velocities = np.ones(self.fullSwarmSize) * velocity
        #noise = np.random.randn(self.fullSwarmSize) * ang_vel * 0.01 # sigma is 10% of velocity
        #self.angle_vel = np.fmax(ang_vel + noise, np.zeros((self.fullSwarmSize)))
        self.angle_vel = np.ones(self.fullSwarmSize) * ang_vel

        self.distances = np.array((self.fullSwarmSize, self.fullSwarmSize))
        self.updateDistances()

        self.inSensorRadius = np.zeros((self.fullSwarmSize, self.fullSwarmSize))
        self.updateInSensorRadius()

        self.estimatedPositions = []
        self.askInfo()


    def rotate(self, vec_len):
        pos = np.zeros((2, self.orientations.shape[0]))
        default_orient = np.array([[vec_len],[0]])
        for i in xrange(self.orientations.shape[0]):
            angle = self.orientations[i]
            R = np.array([[cos(angle), -sin(angle)],[sin(angle), cos(angle)]])
            pos[:,i] = np.dot(R, default_orient)[:,0]
        return pos


    def makeInitialFormation(self):
        swarmPos = np.zeros((2, self.swarmSize))
        shiftX = self.radius * 1.2
        shiftY = (3**0.5) * self.radius * 1.2
        x = 0
        y = -2 * shiftY
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
        source[1,0] = self.initialFormationOffsetY

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
        self.transmit = []
        self.in_shape = []
        self.inside = []
        self.colors = []
        for i in xrange(self.fullSwarmSize):
            self.estimatedPositions.append(self.robots[i].pos)
            self.gradients.append(self.robots[i].grad_val)
            self.stationarity.append(self.robots[i].stationary)
            self.transmit.append(self.robots[i].transmit)
            state = self.robots[i].state
            self.in_shape.append(state=='joined_shape')
            self.inside.append(state=='joined_shape' or state=='move_while_inside')
            if self.robots[i].seed:
                c = 'green'
            elif state=='joined_shape':
                c = 'red'
            elif state == 'move_while_outside':
                c = 'purple'
            elif state == 'move_while_inside':
                c = 'orange'
            else:
                c = 'blue'
            self.colors.append(c)


    def turn(self, robot_id, direct):
        self.orientations[robot_id] += direct*self.angle_vel[robot_id]/self.tick

    def move(self, robot_id):
        default_orient = np.array([[self.velocities[robot_id]],[0]])
        angle = self.orientations[robot_id]
        R = np.array([[cos(angle), -sin(angle)],[sin(angle), cos(angle)]])
        velocity = np.dot(R, default_orient)[:,0]
        new_pos = self.positions[:,robot_id] + velocity/self.tick
        
        if self.checkIfValidPos(robot_id, new_pos):
            #print self.checkIfValidPos(robot_id, new_pos)
            self.positions[:,robot_id] = new_pos

    def checkIfValidPos(self, robot_id, new_pos):
        indicesInRange = np.nonzero(self.inSensorRadius[robot_id,:])[0]
        for ind in indicesInRange:
            if ind != robot_id:
                #dist = self.distances[robot_id, ind] #not really
                dist = sqrt((new_pos[0] - self.positions[0][ind])**2 + 
                    (new_pos[1] - self.positions[1][ind])**2)
                if dist < 2*self.radius:
                    #print "can't move", dist, self.distances[robot_id, ind]
                    return False
        #print "moved"
        return True



    def updateWorld(self):
        """
        this method is called each iteration from the main simulation loop
        """
        self.time += 1./self.tick
        #print self.time
        #TODO: ask all robots to make a move

        for i in xrange(self.fullSwarmSize):
            move = self.robots[i].move()
            
            if move == "clock":
                self.turn(i, -1)
            elif move == "counter-clock":
                self.turn(i, 1)
                #print move
            elif move == "forward":
                
                self.move(i)
            

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
                if self.transmit[ind] and self.in_shape[ind]:
                    pos = self.estimatedPositions[ind]
                else:
                    pos = None
                neihbourData = (self.distances[kilobot_id, ind],
                                pos, 
                                self.gradients[ind],
                                self.stationarity[ind],
                                self.in_shape[ind],
                                (ind < 4),
                                self.inside[ind])
                scanData.append(neihbourData)
        return scanData
        
