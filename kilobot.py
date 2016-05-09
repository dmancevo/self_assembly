
class Kilobot:

  def __init__(self, ID, bitmap, pos=None, grad_val=None):
    
    self.ID        = ID
    self.pos       = pos
    self.grad_val  = grad_val
    self.localized = False
    self.bitmap    = bitmap
    
  
  def update_gradient_val(self):
    pass
  
  def localize(self):
    pass
  
  def move(self):
    pass
  