import urllib.request
import subprocess
import os

class Server:
    """Classe para gerenciar um servidor de jogos."""
    def __init__(self, name):
        self.name = name
        self.version = "1.8"
        self.path = name
        self.process = None
        self.running = False

    def __enter__(self):
        os.makedirs(self.path, exist_ok=True)
        os.chdir(self.path)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir("..")
        pass

    def download_server_jar(self):
        url = "https://launcher.mojang.com/v1/objects/a028f00e678ee5c6aef0e29656dca091b5df11c7/server.jar"
        filename = "server.jar"

        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded {filename} successfully!")

    def run_core(self):
        self.running = True
        self.process = subprocess.Popen(["java", "-jar", "server.jar", "nogui"], stdin=subprocess.PIPE, text=True)

    def stop_core(self):
        self.running = False
        if self.process:
            self.process.stdin.write("stop\n")
            self.process.stdin.flush()
            self.process.wait()
            print("Server stopped.")
            self.process = None

    def kill_core(self):
        self.running = False
        if self.process:
            self.process.kill()
            print("Server killed.")
            self.process = None
    
    def execute_command(self, command):
        if self.running and self.process:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def eula(self):
        with open("eula.txt", "w") as f:
            f.write("eula=true\n")
    
    def properties(self, properties_dict):
        with open("server.properties", "w") as f:
            for key, value in properties_dict.items():
                f.write(f"{key}={value}\n")

if __name__ == "__main__":
    with Server("MyServer") as server:
        # server.download_server_jar()
        # server.eula()
        # server.properties()
        server.run_core()
