import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import EllipseCollection
from world import World

robotRadius = 0.7
sensorRadius = 5
swarmSize = 100
tick = 50 # miliseconds
velocity = 1
ang_velocity = 4

fieldSizeX1 = -30
fieldSizeX2 = 70
fieldSizeY1 = -50
fieldSizeY2 = 50

#shape to assemble
shapeX = np.array([0, 20, 20, 10, 10, 0, 0])
shapeY = np.array([0, 0, 10, 10, 20, 20, 0])
shapeOffsetX = 0
shapeOffsetY = 0
scaleX = 1
scaleY = 1

world = World(swarmSize, robotRadius, sensorRadius, velocity, ang_velocity, tick)
fasePos = world.rotate(0.75*robotRadius)
'''
for i in xrange(100):
    world.updateWorld()
'''

startPos = list(zip(world.positions[0,:], world.positions[1,:]))
#startPosFace = list(zip(world.positions[0,:], world.positions[1,:] + 0.75*robotRadius))
startPosFace = list(zip(world.positions[0,:] + fasePos[0,:], world.positions[1,:] + fasePos[1,:]))

fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(fieldSizeX1, fieldSizeX2), ax.set_xticks([])
ax.set_ylim(fieldSizeY1, fieldSizeY2), ax.set_yticks([])
plt.gca().set_aspect('equal', adjustable='box')

shape = ax.plot(shapeOffsetX + scaleX * shapeX, shapeOffsetY + scaleY * shapeY)

Blues = plt.get_cmap('Blues')
grad = world.gradients
max_g = 40.
colors = map(lambda x: 0 if max_g==float('inf') else x/max_g , grad)

circles = ax.add_collection(EllipseCollection(widths=2*robotRadius, heights=2*robotRadius, angles=0,
                                    units='xy', edgecolors='black', linewidth=0.5,#facecolors=world.colors, 
                                    offsets=startPos, transOffset=ax.transData))
circles.set_array(np.array(grad))
points = ax.add_collection(EllipseCollection(widths=0.5*robotRadius, heights=0.5*robotRadius, angles=0,
                                    units='xy', facecolors='black',
                                    offsets=startPosFace, transOffset=ax.transData))

def init():
    circles.set_offsets([])
    points.set_offsets([])
    return circles


def update(frame):
    circles.set_offsets(list(zip(frame[0], frame[1])))
    
    grad = world.gradients
    max_g = 40.
    colors = map(lambda x: 0 if max_g==float('inf') else x/max_g , grad)
    circles.set_color(Blues(np.array(colors)))
    circles.set_edgecolor('black')

    #points.set_offsets(list(zip(frame[0], frame[1] + 0.75*robotRadius)))
    points.set_offsets(list(zip(frame[0] + frame[2], frame[1] + frame[3])))
    return circles


def mainLoop():
    while True:
        world.updateWorld()
        fasePos = world.rotate(0.75*robotRadius)
        yield world.positions[0,:], world.positions[1,:], fasePos[0,:], fasePos[1,:]
        

anim = animation.FuncAnimation(fig, update, mainLoop, init_func=init, interval=tick)
#anim.save('basic_animation.mp4', fps=int(1000/tick), extra_args=['-vcodec', 'libx264'])
plt.show()

