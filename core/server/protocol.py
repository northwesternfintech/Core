# Signals worker is ready
READY = b"\x01"
# Signals heartbeat
HEARTBEAT = b"\x02"
# Signals for worker to die or that worker has died
DIE = b"\x03"