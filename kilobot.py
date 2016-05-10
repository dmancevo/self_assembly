import random
import numpy as np
#from world import World

class Kilobot:

  def __init__(self, ID, bitmap, world, pos=None, grad_val=float('inf'), radius=1):
    
    self.ID         = ID
    self.pos        = pos
    self.grad_val   = grad_val
    self.bitmap     = bitmap
    self.radius     = radius
    self.stationary = True
    self.world      = world

    #Seed robots never move.
    if pos != None:
      self.final_form = True
      self.seed       = True
    else:
      self.final_form = False
      self.seed       = False
    
  
  def update_gradient(self):
    """
    Update gradient value to minimum among neighbors plus one.
    """
    
    #Seed robots need no further update.
    if self.seed:
      return
    
    #Gradient distance
    G = 3*self.radius
    
    #Only consider neighbors closer than G
    grad_vals = [s[2] for s in self.world.scan(self.ID) if s[0]<G]
    
    self.grad_val = min(grad_vals)+1
  
  def localize(self):
    """
    Update robot's position based on the information
    probed from its neighbors.
    """
    
    #Seed robots need no further localization.
    if self.seed:
      return
    
    #Stationary neighbor positions.
    neighbors = [(s[0],s[1]) for s in self.world.scan(self.ID) if s[3]]
    
    #Check if there are enough neighbors to localize.
    if not len(neighbors) > 2:
      return
    
    myPos = np.zeros(2)
    for pair in neighbors:
      
      #Measured distance (based on signal strengh)
      #and neighbor coordinates.
      d, pos = pair
      
      pos = np.array(pos)
      
      #Distance based on coordinates as opposed to signal strength.
      c = np.linalg.norm(pos-myPos)
      
      #Unit vector pointing from neighbor to self.
      v = (myPos - pos)/c
      
      #Compute new position.
      n = pos + d*v
      
      #Move 1/4 of the way from old calculated position towards new one.
      myPos -= (myPos-n)/4.0
      
    self.pos = tuple(myPos)
  
  def move(self):
    """
    Return desired movement direction as a tuple.
    """
    
    self.update_gradient()
    
    if self.self.final_form:
      return (0,0)
      
    #Check if there are robots nearby already moving.
    if [1 for s in self.world.scan(self.ID) if not s[3]]:
      return (0,0)
    
    
  