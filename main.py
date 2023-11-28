import pygame
import random
import threading
import time
import sys
import traceback
from intersection import Intersection
from crossing import Crossing
from traffic_lights import TrafficLights
from vehicle import Vehicle
from sarsa import SARSA


class Main:
    def __init__(self):

        try:
            pygame.init()
            pygame.font.init()
        except pygame.error as e:
            print(f"Error initializing Pygame: {e}")

        self.width, self.height = 1000, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        # Intersection parameters and colors
        # width of the road
        self.road_width = 150
        # width of the traffic light
        self.traffic_light_width = self.road_width // 2
        # center of the intersection
        self.intersection_center = (self.width // 2, self.height // 2)
        # distance from the center of the intersection to the center of the traffic light
        self.intersection_trl_width = self.road_width // 5

        self.colors = {
            "intersection": {
                "BLACK": (0, 0, 0),
                "GREEN": (26, 93, 26),
                "RED": (255, 0, 0),
                "YELLOW": (255, 255, 0),
                "GRAY": (128, 128, 128),
                "WHITE": (255, 255, 255),
                "BROWN": (185, 148, 112)
            },
            "traffic_lights": {
                "YELLOW_TR": (255, 255, 0),
                "GREEN_TR": (78, 228, 78),
                "RED_TR": (255, 0, 0)
            },
            "vehicle_direction": {
                "straight": (255, 163, 60),
                "left": (135, 196, 255),
                "right": (255, 75, 145)
            }
        }

        self.vehicle_parameters = {
            "radius": 12,
            "width": 12,
            "gap": 12,
            "speed": 0.25,
            "incoming_direction": ["north", "east", "south", "west"],
            "vehicle_count": {"north": 0, "south": 0, "east": 0, "west": 0},
            "processed_vehicles": {"north": 0, "south": 0, "east": 0, "west": 0},
            "dti_info": {"north": {}, "south": {}, "east": {}, "west": {}}
        }

        self.traffic_light_parameters = {
            "directions": ["north", "east", "south", "west"],
            "timings": {
                "RED": 20,
                "GREEN": 20,
                "YELLOW": 10
            }
        }

        self.thresholds = {
            "west": self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 30,
            "east": self.intersection_center[
                        0] - self.road_width // 2 + self.road_width + self.intersection_trl_width + 30,
            "north": self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width - 30,
            "south": self.intersection_center[1] + self.road_width - 15
        }

        self.starting_traffic_light = random.choice(self.traffic_light_parameters["directions"])

        self.vehicle_spawn_coords = {
            "west": [0, self.intersection_center[1] + self.road_width // 4],
            "east": [2 * self.intersection_center[0], self.intersection_center[1] - self.road_width // 4],
            "north": [self.intersection_center[0] - self.road_width // 4, 0],
            "south": [self.intersection_center[0] + self.road_width // 4, 2 * self.intersection_center[1]]
        }

        self.vehicle_turning_points = {
            "left": {
                "west": self.intersection_center[0] + self.road_width // 4,
                "north": self.intersection_center[1] + self.road_width // 4,
                "east": self.intersection_center[0] - self.road_width // 4,
                "south": self.intersection_center[1] - self.road_width // 4
            },
            "right": {
                "west": self.intersection_center[0] - self.road_width // 4,
                "north": self.intersection_center[1] - self.road_width // 4,
                "east": self.intersection_center[0] + self.road_width // 4,
                "south": self.intersection_center[1] + self.road_width // 4
            }
        }

        # threading parameters
        self.vehicle_list = []
        self.vehicle_list_lock = threading.Lock()

        # font object
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 36)

        self.sarsa_agent = None
        self.initialize_sarsa()

    def calculate_reward(self, old_dti, new_dti):
        # Reward for reducing the DTI in the most congested lane
        max_reduction = max(old_dti.values()) - max(new_dti.values())
        return max_reduction

    def apply_action(self, action, traffic_lights):
        directions = ["north", "east", "south", "west"]
        chosen_direction = directions[action]
        # Logic to change the traffic light to the chosen direction
        traffic_lights.change_light(chosen_direction)  # Assuming this method exists in TrafficLights

    def calculate_state(self, max_dti, old_dti):
        # Discretize the DTI values
        dti = self.calculate_dti()
        state = 0
        dti_levels = 10  # Example: 10 levels of DTI
        for direction, value in dti.items():
            state += int(value // (max_dti / dti_levels)) * dti_levels
        return state

    def initialize_sarsa(self):
        # Define the number of states and actions
        number_of_states = 100  # Example value, adjust based on your discretization
        number_of_actions = 4  # 4 directions for traffic lights
        self.sarsa_agent = SARSA(alpha=0.1, gamma=0.9, epsilon=0.1,
                                 number_of_states=number_of_states,
                                 number_of_actions=number_of_actions)

    def vehicle_generator(self, stop_event, vehicle_list_lock):
        while not stop_event.is_set():
            vehicle = Vehicle(self.screen, self.vehicle_parameters["radius"], self.vehicle_parameters["width"],
                              self.vehicle_parameters["speed"],
                              self.vehicle_parameters["processed_vehicles"], self.vehicle_parameters["dti_info"])
            vehicle.generate_vehicle(self.vehicle_spawn_coords, self.vehicle_parameters["incoming_direction"],
                                     self.colors["vehicle_direction"], self.vehicle_parameters["vehicle_count"])
            with vehicle_list_lock:
                self.vehicle_list.append(vehicle)
            time.sleep(0.5)

    def display_data(self, vehicle_count, processed_vehicles):
        x, y = 20, 20
        line_spacing = 25
        color = (0, 0, 0)
        for k, v in vehicle_count.items():
            content = f"{k.capitalize()} lane: {v}"
            text = self.font.render(content, True, color)
            self.screen.blit(text, (x, y))
            y += line_spacing

        x_1, y_1 = 20, y + line_spacing
        text_2 = self.font.render(f"Processed Vehicles: {str(sum(processed_vehicles.values()))}", True, color)
        self.screen.blit(text_2, (x_1, y_1))

    def calculate_dti(self):
        ans = {}
        for main_key in self.vehicle_parameters["dti_info"].keys():
            total = 0
            for k, v in self.vehicle_parameters["dti_info"][main_key].items():
                total += v
            ans[main_key] = round(total, 2)

        return ans

    def run(self):

        # Set up the display
        screen = pygame.display.set_mode((self.width, self.height))

        # Create Intersection, Crossing, and Traffic Lights
        intersection = Intersection(screen, self.intersection_center, self.road_width, self.colors["intersection"],
                                    self.width, self.height, self.font)
        crossing = Crossing(screen, self.intersection_center, self.road_width, self.intersection_trl_width,
                            self.colors["intersection"])
        current_light_state = "GREEN"
        traffic_lights = TrafficLights(screen, self.starting_traffic_light, current_light_state,
                                       self.traffic_light_parameters["directions"], self.colors["traffic_lights"],
                                       self.traffic_light_width,
                                       self.intersection_center, self.road_width, self.intersection_trl_width,
                                       self.traffic_light_parameters["timings"])

        # Vehicle management
        vehicle_list_lock = threading.Lock()
        stop_event = threading.Event()

        # Start the vehicle generator thread
        vehicle_gen_thread = threading.Thread(target=self.vehicle_generator,
                                              args=(stop_event, vehicle_list_lock))
        try:
            vehicle_gen_thread.start()
        except RuntimeError as e:
            print(f"Error starting thread: {e}")

        max_dti = 1000.0  # Set this to a reasonable upper estimate based on your simulation data.

        # Initialize the current state and action
        old_dti = self.calculate_dti()
        current_state = self.calculate_state(max_dti, old_dti)  # Pass max_dti as a parameter
        current_action = self.sarsa_agent.choose_action(current_state)

        # Main loop
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # In the main loop

                current_time = pygame.time.get_ticks()
                current_traffic_light, current_light_state = traffic_lights.update(current_time)

                if traffic_lights.green_light_start_time is None or \
                        current_time - traffic_lights.green_light_start_time >= 20000:  # 120 seconds in milliseconds
                    current_state = self.calculate_state(max_dti, old_dti)
                    current_action = self.sarsa_agent.choose_action(current_state)
                    self.apply_action(current_action, traffic_lights)
                    # Update the DTI and SARSA state after the action
                    new_dti = self.calculate_dti()
                    new_state = self.calculate_state(max_dti, new_dti)
                    reward = self.calculate_reward(old_dti, new_dti)
                    next_action = self.sarsa_agent.choose_action(new_state)
                    self.sarsa_agent.update(current_state, current_action, reward, new_state, next_action)
                    current_state = new_state
                    old_dti = new_dti
                    current_action = next_action

                # Draw the intersection, traffic lights, and crossing
                intersection.draw()
                traffic_lights.draw()
                crossing.draw()

                # Process and draw vehicles
                with vehicle_list_lock:
                    for vehicle in self.vehicle_list:  # Note the use of self here
                        vehicle.move(current_traffic_light, current_light_state, self.thresholds,
                                     self.vehicle_turning_points)
                        vehicle.draw()
                        if vehicle.kill_vehicle(self.width, self.height):
                            self.vehicle_list.remove(vehicle)

                        has_crossed, crossed_direction = vehicle.crossed_threshold()
                        if has_crossed:
                            self.vehicle_parameters["vehicle_count"][crossed_direction] -= 1

                self.display_data(self.vehicle_parameters["vehicle_count"],
                                  self.vehicle_parameters["processed_vehicles"])
                # print(self.vehicle_parameters["dti_info"])
                print(self.calculate_dti())
                pygame.display.flip()
        except Exception as e:
            print(f"Error during main loop: {e}", end='\r')
            traceback.print_exc()
            sys.exit(1)

        # Clean up and exit
        stop_event.set()
        vehicle_gen_thread.join()
        try:
            pygame.quit()
            sys.exit()
        except pygame.error as e:
            print(f"Error quitting Pygame: {e}")


if __name__ == "__main__":
    main = Main()
    main.run()
