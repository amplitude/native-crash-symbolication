import time

class Timer:

  '''
  Returns the system time started
  '''
  def start(self):
    self.start = time.time()
    self.last = self.start
    return self.start

  '''
  Returns the time in seconds since the last call to start or split
  '''
  def split(self):
    now = time.time()
    diff = now - self.last
    self.last = now
    return diff

  '''
  Returns the time in seconds since the last call to start and
  stops the timer
  '''
  def stop(self):
    now = time.time()
    diff = now - self.start
    self.last = now
    return diff

def start():
  timer = Timer()
  timer.start()
  return timer

