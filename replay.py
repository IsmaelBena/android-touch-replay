import subprocess
import json
import time
import yaml

def replay_touch_events(input_file="formatted_recording.json"):
    with open(input_file, "r") as f:
        actions = json.load(f)
        for action in actions:
            print(action)
            if "wait_time" in action:
                time.sleep(action["wait_time"])
            command = ["adb", "shell", "input", "swipe", str(action["start_x"]), str(action["start_y"]), str(action["end_x"]), str(action["end_y"]), str(action["duration"])]
            print(command)
            subprocess.run(command)

replay_touch_events()
