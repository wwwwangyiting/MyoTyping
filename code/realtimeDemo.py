from collections import deque
from threading import Lock
from keras.models import load_model
import myo
import numpy as np
import time
import signalSegmentation as fg
import inputConvert as T9Tran

data_array = []
flag1 = True

load_time_start=time.perf_counter()
model = load_model('..\model\CLT_Model.h5')
load_time_end=time.perf_counter()
print("model load time:",load_time_end-load_time_start)


class EmgCollector(myo.DeviceListener):
  """
  Collects EMG data in a queue with *n* maximum number of elements.
  """

  def __init__(self, n):
    self.n = n
    self.lock = Lock()
    self.emg_data_queue = deque(maxlen=n)
    self.data_queue = deque(maxlen=n)
    self.flag = 400

  def get_emg_data(self):
    with self.lock:
      return list(self.emg_data_queue)

  # myo.DeviceListener

  def on_connected(self, event):
    print("Myo Connected")
    print("Current time", time.perf_counter())
    event.device.stream_emg(True)

  def on_emg(self, event):
    with self.lock:
      self.emg_data_queue.append((event.timestamp, event.emg)) #add new signal into the right end of the queue

      if len(list(self.emg_data_queue)) >= self.flag:
        emg_data = self.emg_data_queue
        emg_data = np.array([x[1] for x in emg_data])
        for data in emg_data:
          self.data_queue.append(data)
        #print(len(self.data_queue))
        self.emg_data_queue.clear()

class Fenge(object):

  def __init__(self, listener):
    self.n = listener.n
    self.listener = listener
    self.win_len = 30
    self.ch_len = 8
    self.on_set = 700
    self.off_set = 650
    self.min_signal_len = 70
    self.flag1 = True
    self.m_se = 2
    self.win_overloap = 30
    self.hang=0
    self.inputs=""
    self.biao=0
    self.inputTrue=-1
    # self.t9=[]

  def fenge(self):
    result = []
    if len(self.listener.data_queue)>=400 and self.flag1==True:
      input = -1
      self.flag1 = False
      data = np.array(self.listener.data_queue)
      num,input = fg.extractActiveSegment(data, self.win_len, self.ch_len, self.on_set, self.off_set,
                                     self.min_signal_len, result,model,self.m_se,self.win_overloap,input)

      # print(input)
      # print("flag:",self.listener.flag)
      #convert to character
      if input>-1:
        if input == 0:
          if self.hang == 0:
            self.hang = 1
          else:
            self.hang = 0
        # number mode---------------------------------------------
        elif input<6:
          if input==5:
            if self.hang==0:
              inputTrue=1
            else:
              inputTrue=0
          else:
            inputTrue = input + 4 * self.hang + 1
          self.inputs += str(inputTrue)
          T9Tran.runNumber(self.inputs)
        # letter mode--------------------------------------------
        # elif input!=5:
        #   if input==6:
        #     self.inputs=self.inputs[:-1]
        #     self.biao=self.biao+1
        #   elif input<5:
        #     self.inputTrue = input + 4*self.hang + 1
        #   T9Tran.runLetter(inputTrue,biao)

      for i in range (num):
        self.listener.data_queue.popleft()
      self.flag1 = True
      self.listener.flag =num

  def main(self):
    while True:
      self.fenge()
      # plt.pause(1.0 / 30)

def main():
  myo.init()
  # myo.init('E:\BaiduNetdiskDownload\Myo Windows\myo-sdk-win-0.9.0\myo-sdk-win-0.9.0\\bin\\myo64.dll')
  hub = myo.Hub()
  listener = EmgCollector(400)
  with hub.run_in_background(listener.on_event):
    Fenge(listener).main()

if __name__ == '__main__':
  main()