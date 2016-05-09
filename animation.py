"""
some animation
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import EllipseCollection

RADIUS = 0.7
swarmSize = 500
fieldSizeX = 100
fieldSizeY = 100
tick = 100 # miliseconds

def makeInitialFormation(swarmSize, radius, firstDim, offsetX, offsetY):
    swarmPos = np.zeros((2, swarmSize))
    shiftX = radius
    shiftY = (3**0.5) * radius
    print(shiftX, shiftY)
    x = 0
    y = 0
    row = 1
    for i in xrange(swarmSize):
        swarmPos[0, i] = x
        swarmPos[1, i] = y
        
        if (i+1) % firstDim == 0:
            print i
            row += 1
            y += shiftY
            x = shiftX if row%2==0 else 0
        else:
            x += 2 * shiftX

    #move
    swarmPos[0,:] += offsetX
    swarmPos[1,:] += offsetY

    return swarmPos

#starting positions
startPos = makeInitialFormation(swarmSize, RADIUS*1.2, 30, 10, 5)
currentX = startPos[0,:]
currentY = startPos[1,:]
startPos = list(zip(currentX,currentY))
startPosFace = list(zip(currentX,currentY + 0.75*RADIUS))

#shape to assemble
shapeX = np.array([0, 20, 20, 10, 10, 0, 0])
shapeY = np.array([0, 0, 10, 10, 20, 20, 0])
shapeOffsetX = 40
shapeOffsetY = 40
scaleX = 1
scaleY = 1

fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, fieldSizeX), ax.set_xticks([])
ax.set_ylim(0, fieldSizeY), ax.set_yticks([])
plt.gca().set_aspect('equal', adjustable='box')

shape = ax.plot(shapeOffsetX + scaleX * shapeX, shapeOffsetY + scaleY * shapeY)


circles = ax.add_collection(EllipseCollection(widths=2*RADIUS, heights=2*RADIUS, angles=0,
                                    units='xy', facecolors='blue',
                                    offsets=startPos, transOffset=ax.transData))
points = ax.add_collection(EllipseCollection(widths=0.5*RADIUS, heights=0.5*RADIUS, angles=0,
                                    units='xy', facecolors='black',
                                    offsets=startPosFace, transOffset=ax.transData))

def init():
    circles.set_offsets([])
    points.set_offsets([])
    return circles

def update(frame):
    updatePositions()
    circles.set_offsets(list(zip(frame[0], frame[1])))
    points.set_offsets(list(zip(frame[0], frame[1] + 0.75*RADIUS)))
    return circles

def updatePositions():
    for i in range(swarmSize):
        currentX[i] += np.random.randn(1) * 0.05
        currentY[i] += np.random.randn(1) * 0.05
    return currentX, currentY


def data_gen():
    while True:
        yield updatePositions()

#anim = animation.FuncAnimation(fig, update, data_gen, init_func=init, interval=tick)
#anim.save('basic_animation.mp4', fps=int(1000/tick), extra_args=['-vcodec', 'libx264'])
plt.show()