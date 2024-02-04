import threading
import time

def thread_function(name):
   print(f"Thread {name}: starting")
   time.sleep(2)
   print(f"Thread {name}: finishing")

if __name__ == "__main__":
   threads = list()
   for index in range(3):
       print(f"Main   : create and start thread {index}.")
       x = threading.Thread(target=thread_function, args=(index,))
       threads.append(x)
       x.start()

   for index, thread in enumerate(threads):
       thread.join()
