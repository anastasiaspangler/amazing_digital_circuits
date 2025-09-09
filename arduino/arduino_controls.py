# Read key=value lines from Arduino. Print all button events. Print pot only on change.
import serial, re
from datetime import datetime

def serial_reader():
    PORT = "/dev/cu.usbmodem311201"   # your port
    BAUD = 115200
    ser = serial.Serial(PORT, BAUD, timeout=1)

    last = {}
    POT_THRESH = 4
    kv_re = re.compile(r"\s*([A-Za-z0-9_]+)\s*=\s*([^\s]+)\s*$")

    def now_str():
      return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    while True:
      raw = ser.readline()
      if not raw:
        continue
      line = raw.decode('ascii', errors='ignore').strip()
      if not line:
        continue

      m = kv_re.match(line)
      if not m:
        continue
      k, v = m.group(1), m.group(2)

      # Always print button presses
      if k.startswith("button"):
        print(f"[ARDUINO] {now_str()} {k} pressed")
        continue

      # Pot: print only on change (with threshold)
      try:
        v_use = int(v)
      except ValueError:
        v_use = v

      prev = last.get(k)
      should = (prev is None) or (
          isinstance(v_use, int) and isinstance(prev, int) and abs(v_use - prev) >= POT_THRESH
      ) or (v_use != prev)

      if should:
        print(f"[ARDUINO] {now_str()} dial={v_use}")
        last[k] = v_use
