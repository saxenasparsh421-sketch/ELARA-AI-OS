class Kernel:

    def __init__(self):

        self.services = {}

        print("=" * 50)
        print("        JARVIS OS Kernel")
        print("=" * 50)

    def register(self, name, service):

        self.services[name] = service

        print(f"[OK] {name} registered")

    def get(self, name):

        return self.services.get(name)

    def start(self):

        print("\nStarting Services...\n")

        for name, service in self.services.items():

            if hasattr(service, "start"):
                service.start()

        print("\nAll services are online.\n")