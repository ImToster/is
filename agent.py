import socket
import argparse
from msg import parse_msg
from calculate_position import (
    calculate_agent_position,
    calculate_object_position
)


class Agent:
    def __init__(self, host, port, team_name):
        self.host = host
        self.port = port
        self.team_name = team_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.host, self.port)
        self.play_on = False

    def send_cmd(self, cmd):
        self.sock.sendto(cmd.encode('ascii'), self.server_address)

    def get_visible_objects(self, see_cmd_parameters):
        visible_objects = []
        for parameter in see_cmd_parameters[1:]:
            obj = {
                "name": parameter["cmd"]["p"]
            }
            obj_parameters = parameter["p"]
            if len(obj_parameters) == 1:
                obj["direction"] = int(obj_parameters[0])
            else:
                obj["distance"] = float(obj_parameters[0])
                obj["direction"] = int(obj_parameters[1])
                if len(obj_parameters) > 2:
                    obj["dist_change"] = float(obj_parameters[2])
                    obj["dir_change"] = float(obj_parameters[3])
                    if len(obj_parameters) > 4:
                        obj["body_facing_dir"] = int(obj_parameters[4])
                        obj["head_facing_dir"] = int(obj_parameters[5])
            visible_objects.append(obj)
        return visible_objects

    def analyze_env(self, cmd, p):
        if cmd == "hear":
            self.play_on = True
            print("Referee: play_on! Started turning.")
        elif cmd == "see":
            visible_objects = self.get_visible_objects(p)
            visible_flags = [
                visible_object for visible_object in visible_objects
                if visible_object["name"][0] == "f"
            ]
            visible_enemies = []
            for visible_object in visible_objects:
                if visible_object["name"][0] == "p":
                    if len(visible_object["name"]) > 1:
                        team = visible_object["name"][1]
                        if team != self.team_name:
                            visible_enemies.append(visible_object)
                    else:
                        visible_enemies.append(visible_object)

            agent_pos = calculate_agent_position(visible_flags)
            if agent_pos:
                print(
                    f"Agent position: x={agent_pos[0]:.2f}, y={agent_pos[1]:.2f}"
                )
                for visible_enemy in visible_enemies:
                    enemy_pos = calculate_object_position(
                        agent_pos, visible_enemy, visible_flags)
                    if enemy_pos:
                        print(
                            f"Enemy position: x={enemy_pos[0]:.2f}, y={enemy_pos[1]:.2f}"
                        )

    def run(self, start_x, start_y, turn_speed):
        print(
            f"Connecting to {self.host}:{self.port} as team {self.team_name}...")
        self.send_cmd(f"(init {self.team_name} (version 15))")

        try:
            data, self.server_address = self.sock.recvfrom(4096)
            init_response = data.decode('ascii')
            print(f"Init rx: {init_response}")
        except socket.timeout:
            print("Failed to connect to server.")
            return

        print(f"Moving to start position: ({start_x}, {start_y})")
        self.send_cmd(f"(move {start_x} {start_y})")

        print("Entering main loop. Waiting for play_on...")
        while True:
            try:
                if self.play_on:
                    self.send_cmd(f"(turn {turn_speed})")
                msg, addr = self.sock.recvfrom(8192)
                msg = msg.decode('ascii')
                data = parse_msg(msg)
                self.analyze_env(data["cmd"], data["p"])
            except socket.timeout:
                pass
            except KeyboardInterrupt:
                print("Agent stopped by user.")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RoboCup 2D Agent for Lab 1")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=6000, help="Server port")
    parser.add_argument("--team", default="Team1", help="Team name")
    parser.add_argument("--x", type=float, default=-
                        10.0, help="Initial X coordinate")
    parser.add_argument("--y", type=float, default=0,
                        help="Initial Y coordinate")
    parser.add_argument("--turn", type=float, default=45.0, help="Turn speed")

    args = parser.parse_args()

    agent = Agent(args.host, args.port, args.team)
    agent.run(args.x, args.y, args.turn)
