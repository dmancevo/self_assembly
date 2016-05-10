#Here comes the physics engine (by Olga)

class World:
  
  def __init__(self):
    pass
  
  
  def scan(self,kilobot_id):
    """
    This method should be called by the kilobots to receive information
    about their neighbors.
    
    Returns list of tuples where each tuple has (d, (x,y), grad_val, stationary).
    (x,y) may be None and stationary is either True or False.
    """
    
    return []