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
    self.world      = world
    self.dist_nn    = float('inf')
    self.rot        = False
    self.state      = 'wait_to_move'
    self.stationary = True
    self.rand_nonce = np.random.uniform(0,0.1)

    #Seed robots never move.
    if pos is not None:
      self.seed       = True
      self.state      = 'joined_shape'
    else:
      self.seed       = False
      
      
  def edge_follow(self, desired):
    """
    Edge following routine.
    """
    
    prev = self.dist_nn
    current = min([s[0] for s in self.world.scan(self.ID) if s[3]])
    
    if self.rot and (current-prev) > 4*self.radius and np.random.uniform(0,1)<0.8:
      return self.rot
    elif self.rot:
      self.rot = False
      return 'forward'
    
    move = 'stop'
      
    if current < desired:
      if prev < current:
        move = 'forward'
      else:
        move = 'counter-clock'
        self.rot = move
    else:
      if prev > current:
        move = 'forward'
      else:
        move = 'clock'
        self.rot = move
        
    self.dist_nn = current
    
    return move
    
  
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
    
    if grad_vals:
      self.grad_val = min(grad_vals)+1+self.rand_nonce
  
  def localize(self):
    """
    Update robot's position based on the information
    probed from its neighbors.
    """
    
    #Seed robots need no further localization.
    if self.seed:
      return
    
    #Stationary neighbor positions.
    neighbors = [(s[0],s[1]) for s in self.world.scan(self.ID) if s[3] and s[1] is not None]
    
    #Check if there are enough neighbors to localize.
    if not len(neighbors) > 2:
      return
    
    myPos = np.zeros(2)
    
    for _ in range(15):
      for pair in neighbors:
        
        #Measured distance (based on signal strengh)
        #and neighbor coordinates.
        d, pos = pair
        
        pos = np.array(pos)
        
        #Distance based on coordinates as opposed to signal strength.
        c = np.linalg.norm(pos-myPos)
        
        #Unit vector pointing from neighbor to self.
        if c == 0:
            v = 0
        else:
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
    
    if self.bitmap is None:
      return 'stop'
    
    #Yield distance
    Y = 3*self.radius
    
    prev_grad = self.grad_val
      
    #Update gradient and localize
    self.update_gradient()
    self.localize()

    if self.state == 'joined_shape':
      return 'stop'
    
    #Check if kilobot is not already in shape.
    if self.bitmap.in_shape(self.pos):
      self.state = 'joined_shape'
      self.stationary = True
      return 'stop'
    
    if self.state == 'wait_to_move':
      
      #Check if there are robots nearby already moving.
      if [1 for s in self.world.scan(self.ID) if not s[3] and s[0] < Y]:
        return 'stop'
      
      #Highest gradient value among neighbours.
      h = max([s[2] for s in self.world.scan(self.ID)])
      
      if self.grad_val > h:
        self.state = 'move_while_outside'
        self.stationary = False
      else:
        return 'stop'
        
    #Keep distance
    if self.state == 'move_while_outside' or \
    self.state == 'move_while_inside':
       moving = [(s[0],s[2]) for s in self.world.scan(self.ID) if not s[3]]
       
       for d, g in moving:
         if self.grad_val < prev_grad:
           if g < self.grad_val and d < Y:
             return 'stop'
         elif prev_grad < self.grad_val:
           if self.grad_val < g and d < Y:
             return 'stop'
       
      
    #Move while outside.
    if self.state == 'move_while_outside':
      
      if self.bitmap.in_shape(self.pos):
        self.state = 'move_while_inside'
        
      return self.edge_follow(2.3*self.radius)
    
    #Move while inside.
    elif self.state == 'move_while_inside':
      
      if not self.bitmap.in_shape(self.pos):
        self.state = 'joined_shape'
        self.stationary = True
        return 'stop'
      
      elif self.grad_val <= min([(s[0],s[2]) for s in self.world.scan(self.ID)],
      key=lambda x: x[0])[1]:
        self.state = 'joined_shape'
        self.stationary = True
        return 'stop'
        
      else:
        return self.edge_follow(2.3*self.radius)
          