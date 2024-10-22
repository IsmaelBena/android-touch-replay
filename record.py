import subprocess
import re
import json
import keyboard
import time
import threading
import yaml



def record_raw_touch_events(adb_target="adb", output_file="raw_touch_log.txt"):
    with open(output_file, "w") as f:
        return subprocess.Popen([adb_target, "shell", "getevent", "-t", "/dev/input/event11"], stdout=f)

def get_actual_size(adb_target="adb"):
    cmd_output = subprocess.check_output([adb_target, "shell", "wm", "size"])
    cmd_output = cmd_output.decode("utf-8")
    for line in cmd_output.split("\n"):
        line = line.strip().split()
        if len(line) > 0:
            coords = line[-1].split("x")
            x = coords[0]
            y = coords[1]
            print(f"{line[0]}: ({x}, {y})")
            
    return int(x), int(y)

def parse_getevent_log(raw_logs="raw_touch_log.txt"):
    tracking_id_pattern = r"0003 0039 (.{8})"
    x_position_pattern = r"0003 0035 (.{8})"
    y_position_pattern = r"0003 0036 (.{8})"
    touch_down_pattern = r"0001 014a 00000001"
    touch_up_pattern = r"0001 014a 00000000"

    with open(raw_logs, "r", encoding="utf-8") as logs:

        touches = []
        current_touch = {
            'tracking_id': '',
            'x': [],
            'y': [],
            'start_time': '',
            'end_time': ''
        }
        
        for line in logs:
            line = line.strip()
            split_line = line.strip("[ ]").split()
            split_line[0] = split_line[0][0:-1]
            
            if re.search(tracking_id_pattern, line):
                tracking_id = re.search(tracking_id_pattern, line).group(1)
                if tracking_id == "ffffffff":
                    if current_touch:
                        current_touch["end_time"] = float(split_line[0])
                        print(f"end time: {split_line[0]}")
                        touches.append(current_touch)
                        current_touch = {
                            'prev_end': float(split_line[0]),
                            'tracking_id': '',
                            'x': [],
                            'y': [],
                            'start_time': '',
                            'end_time': ''
                        }
                else:
                    current_touch["tracking_id"] = tracking_id
            
            if re.search(x_position_pattern, line):
                print(f"{current_touch['tracking_id']} x")
                current_touch["x"].append(int(re.search(x_position_pattern, line).group(1), 16))
            
            if re.search(y_position_pattern, line):
                print(f"{current_touch['tracking_id']} y")
                current_touch["y"].append(int(re.search(y_position_pattern, line).group(1), 16))

            if re.search(touch_down_pattern, line):
                print(f"end time: {split_line[0]}")
                current_touch["start_time"] = float(split_line[0])
            
            if re.search(touch_up_pattern, line):
                print("up?")
                # current_touch["action"] = "up"

        return touches

def convert_to_input(touches, output_file="formatted_recording.json", adb_target="adb"):
    screen_x, screen_y = get_actual_size(adb_target)
    actions_to_take = []
    for action in touches:
        if "prev_end" in action:            
            actions_to_take.append({
                'wait_time': (action["start_time"] - action["prev_end"]),
                'start_x': int((action["x"][0] / 4095) * screen_x),
                'start_y': int((action["y"][0] / 4095) * screen_y),
                'end_x': int((action["x"][-1] / 4095) * screen_x),
                'end_y': int((action["y"][-1] / 4095) * screen_y),
                'duration': int((action["end_time"] - action["start_time"]) * 1000)
            })
        else:
            actions_to_take.append({
                'start_x': int((action["x"][0] / 4095) * screen_x),
                'start_y': int((action["y"][0] / 4095) * screen_y),
                'end_x': int((action["x"][-1] / 4095) * screen_x),
                'end_y': int((action["y"][-1] / 4095) * screen_y),
                'duration': int((action["end_time"] - action["start_time"]) * 1000)
            })
    with open(output_file, 'w') as f:
        json.dump(actions_to_take, f)
    print(actions_to_take)


def detect_end_process(process):
    print("press q to stop recording")
    while True:
        if keyboard.is_pressed('q'):
            print("\nstopping recording")
            process.terminate()
            break
        time.sleep(0.01)

def main():
        
    # with open('config.yaml', 'r') as file:
    #     config = yaml.safe_load(file)
    
    recording_process = record_raw_touch_events()
    
    end_recording_thread = threading.Thread(target=detect_end_process, args=(recording_process,))
    
    end_recording_thread.start()
    
    recording_process.wait()
    
    end_recording_thread.join()
    
    convert_to_input(parse_getevent_log())
    
    
if __name__ == "__main__":
        
    main()