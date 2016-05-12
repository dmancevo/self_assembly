from PIL import Image
import numpy as np

class BitMap:
  
  def __init__(self, image):
    
    self.im = Image.open("shapes/{im}".format(im=image)).convert('L')
    self.arr = np.array(self.im.getdata(), np.uint8).reshape(self.im.size)
    
  def in_shape(self, pos):
    """
    Determine if the point at position pos
    is inside the figure or not.
    
    Returns boolean (True or False)
    """
    
    pos = (int(np.round(pos[0])),int(np.round(pos[1])))
    
    return self.arr[pos] != 255
  
if __name__ == '__main__':
  
  bitmap = BitMap("shape1.png")
  print bitmap.in_shape((345,203))
  
  print bitmap.arr.shape