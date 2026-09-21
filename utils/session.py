import time


class ConversationSession:

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.last_activity = 0

    def start(self):
        self.last_activity = time.time()

    def refresh(self):
        self.last_activity = time.time()

    def expired(self):
        return (time.time() - self.last_activity) > self.timeout