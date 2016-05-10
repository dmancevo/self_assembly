import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import EllipseCollection
from world import World

robotRadius = 0.7
sensorRadius = 5
swarmSize = 500
tick = 100 # miliseconds
velocity = 1

fieldSizeX = 100
fieldSizeY = 100

#shape to assemble
shapeX = np.array([0, 20, 20, 10, 10, 0, 0])
shapeY = np.array([0, 0, 10, 10, 20, 20, 0])
shapeOffsetX = 40
shapeOffsetY = 40
scaleX = 1
scaleY = 1

World.initialize(swarmSize, robotRadius, sensorRadius, velocity, tick)

startPos = list(zip(World.positions[0,:],World.positions[1,:]))
startPosFace = list(zip(World.positions[0,:],World.positions[1,:] + 0.75*robotRadius))


fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, fieldSizeX), ax.set_xticks([])
ax.set_ylim(0, fieldSizeY), ax.set_yticks([])
plt.gca().set_aspect('equal', adjustable='box')

shape = ax.plot(shapeOffsetX + scaleX * shapeX, shapeOffsetY + scaleY * shapeY)


circles = ax.add_collection(EllipseCollection(widths=2*robotRadius, heights=2*robotRadius, angles=0,
                                    units='xy', facecolors='blue',
                                    offsets=startPos, transOffset=ax.transData))
points = ax.add_collection(EllipseCollection(widths=0.5*robotRadius, heights=0.5*robotRadius, angles=0,
                                    units='xy', facecolors='black',
                                    offsets=startPosFace, transOffset=ax.transData))

def init():
    circles.set_offsets([])
    points.set_offsets([])
    return circles


def update(frame):
    circles.set_offsets(list(zip(frame[0], frame[1])))
    points.set_offsets(list(zip(frame[0], frame[1] + 0.75*robotRadius)))
    return circles


def mainLoop():
    while True:
        World.updateWorld()
        yield World.positions[0,:],World.positions[1,:]
        

anim = animation.FuncAnimation(fig, update, mainLoop, init_func=init, interval=tick)
#anim.save('basic_animation.mp4', fps=int(1000/tick), extra_args=['-vcodec', 'libx264'])
plt.show()
