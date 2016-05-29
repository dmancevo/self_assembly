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
      self.accurate_pos = True
      self.transmit     = True
      self.seed         = True
      self.state        = 'joined_shape'
    else:
      self.accurate_pos = False
      self.transmit     = False
      self.seed         = False
      
      
  def edge_follow(self, desired):
    """
    Edge following routine.
    """
    G = 3.5*self.radius
    prev = self.dist_nn
    current = min([s[0] for s in self.world.scan(self.ID) if s[3] and s[0]<G])
    
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
      min_grad = min(grad_vals)
      if min_grad == float('inf'):
        self.grad_val = float('inf')
      else:
        self.grad_val = int(min_grad) + 1 + self.rand_nonce
  
  def localize(self):
    """
    Update robot's position based on the information
    probed from its neighbors.
    """
    MAX_ITER = 30
    eps1 = 0.01
    eps2 = 0.001
    
    #Localized robots need no further localization.
    if self.state == 'joined_shape' and self.transmit:
      return
    
    #Stationary neighbor positions.
    neighbors = [(s[0],s[1]) for s in self.world.scan(self.ID) if s[3] and s[1] is not None]
    
    #Check if there are enough neighbors to localize.
    if not len(neighbors) > 2:
      self.accurate_pos = False
      self.transmit     = False
      return

    #if position is None, assume 0, otherwise it is probably better to use latest approximation
    if self.pos is None:
      myPos = np.zeros(2)
    else:
      myPos = np.array(self.pos)
    
    it = 0

    while True:
      dist_diff = []
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

        #difference between true dictance and new
        dist_diff.append(np.linalg.norm(pos-myPos) - d)
        it += 1
      
      max_dist = max(dist_diff)

      if abs(max_dist) < eps1 or it > MAX_ITER:
        self.pos = tuple(myPos)
        self.accurate_pos = abs(max_dist) < eps1
        self.transmit = abs(max_dist) < eps2
        return

  
  def move(self):
    """
    Return desired movement direction as a tuple.
    """
    
    if self.bitmap is None:
      return 'stop'
    
    #Yield distance
    Y = 6*self.radius

    G = 3*self.radius
    
    prev_grad = self.grad_val
      
    #Update gradient and localize
    self.update_gradient()
    self.localize()
    
    if self.state == 'joined_shape':
      return 'stop'
    
    
    if self.state == 'wait_to_move':
      #in the paper they assume al robots start outside, and the was some strange bug here
      '''
      #Check if kilobot is not already in shape.
      if self.accurate_pos and self.bitmap.in_shape(self.pos):
        print self.ID, self.pos, self.bitmap.in_shape(self.pos)
        self.state = 'joined_shape'
        self.stationary = True
        return 'stop'
      '''
      
      #Check if there are robots nearby already moving.
      if [1 for s in self.world.scan(self.ID) if not s[3] and s[0] < Y]:
        return 'stop'
      
      
      #Highest gradient value among neighbours.
      ngbs = [s[2] for s in self.world.scan(self.ID) if s[0] < G and (not s[4] or s[5])]

      if len(ngbs) == 0:
        h = float('inf')
      else:
        h = max(ngbs)
      
      if self.grad_val > h:
        self.state = 'move_while_outside'
        self.stationary = False
      else:
        return 'stop'
        
    #Keep distance
    '''
    if self.state == 'move_while_outside' or \
    self.state == 'move_while_inside':
       moving = [(s[0],s[2],s[6]) for s in self.world.scan(self.ID) if not s[3]]
       
       for d, g, inside in moving:
        g = int(g)
        if self.state=='move_while_outside' and g < int(self.grad_val) and d < Y:
          print 'keeping distance'
          return 'stop'
        elif self.state=='move_while_inside' and g > int(self.grad_val) and d < Y:
          print 'keeping distance'
          return 'stop'
    '''
      
    #Move while outside.
    if self.state == 'move_while_outside':
      
      if self.accurate_pos and self.bitmap.in_shape(self.pos):
        self.state = 'move_while_inside'
        
      return self.edge_follow(2.3*self.radius)
    
    #Move while inside.
    elif self.state == 'move_while_inside':
      
      if self.accurate_pos and not self.bitmap.in_shape(self.pos):
        self.state = 'joined_shape'
        self.stationary = True
        return 'stop'
      
      elif int(self.grad_val) <= int(min([(s[0],s[2]) for s in self.world.scan(self.ID) if s[0] < G and s[3]],
      key=lambda x: x[0])[1]):
        self.state = 'joined_shape'
        self.stationary = True
        return 'stop'
        
      else:
        return self.edge_follow(2.3*self.radius)
          