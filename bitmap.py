import numpy as np
import scipy.misc

class BitMap:
  
  def __init__(self, file_name):
    
    self.arr = np.transpose(scipy.misc.imread(file_name, mode="L"))
    self.shape = np.transpose(np.nonzero(self.arr-255))
    self._origin()


  def in_shape(self, pos):
    """
    Determine if the point at position pos
    is inside the figure or not.
    
    Returns boolean (True or False)
    """
    
    if pos is None:
      return False
    
    pos = (int(np.round(pos[0])),int(np.round(pos[1])))
    return self.arr[pos] != 255
    
  def _origin(self):
    """
    Return origin position.
    """
    ind = np.random.choice(range(len(self.shape)))
    self.origin = self.shape[ind]
    
  
if __name__ == '__main__':
  
  bitmap = BitMap("shape1.png")
  #print bitmap.in_shape((345,203))
  
  print bitmap.arr.shape
  
  #origin = bitmap.origin()
  #print origin