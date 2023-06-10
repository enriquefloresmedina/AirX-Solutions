
BUFFER = []

def addToBuffer(data):
    global BUFFER
    BUFFER.append(data)

def getBuffer():
    global BUFFER
    return BUFFER

def eraseBuffer():
    global BUFFER
    BUFFER = []