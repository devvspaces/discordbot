import threading
import time

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

li = dict()

def get_driver(a):
  driver = li.get(f'driver{a}', None)

  if driver is None:
    print('Created a new driver')
    driver = {
      'name': f'{a} I am a BOT'
    }
    li[f'driver{a}'] = driver

  return driver


def get_title(a, event):
  print(get_driver(a))
  time.sleep(6)
  if event.isSet():
    print(f'Finished {a} early')
    return
  time.sleep(6)
  print(f'Finished {a}')

thread_name = ''

events = dict()

for a in [1,2,3,1,2]:
  e = threading.Event()
  t1 = threading.Thread(target=get_title, args=(a, e,))
  t1.start()
  # if a == 3:
  #   thread_name = t1.name

  # Add event to events
  events[f'event{a}'] = e

time.sleep(5)

for a,b in events.items():
  if a == 'event3':
    b.set()

# for thread in threading.enumerate(): 
#   if thread.name == thread_name:
#     print(thread)