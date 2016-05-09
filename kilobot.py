import random

class Kilobot:

  def __init__(self, ID, bitmap, pos=None, grad_val=float('inf'), radius=1):
    
    self.ID         = ID
    self.pos        = pos
    self.grad_val   = grad_val
    self.bitmap     = bitmap
    self.radius     = radius
    self.stationary = True
    
  
  def update_gradient_val(self):
    """
    Update gradient value to minimum among neighbors plus one.
    """
    
    grad_vals = [s[2] for s in world.scan(self.ID)]
    self.grad_val = min(grad_vals)+1
  
  def localize(self):
    pass
  
  def move(self):
    """
    Return desired movement direction as a tuple.
    """
    
    self.update_gradient()
    
    if self.stationary or random.uniform(0,1)>0.1:
      return (0,0)
    
    
  