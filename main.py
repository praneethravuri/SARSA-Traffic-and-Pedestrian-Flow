import pygame
import random
import threading
import time


class Intersection:
    def __init__(self, screen, center, road_width, intersection_colors, width, height, font):
        self.screen = screen
        self.center = center
        self.road_width = road_width
        self.intersection_colors = intersection_colors
        self.width = width
        self.height = height
        self.font = font

    def draw(self):
        # Fill background with green
        self.screen.fill(self.intersection_colors["GREEN"])

        # Drawing the vertical road
        pygame.draw.rect(self.screen, self.intersection_colors["BLACK"],
                         (self.center[0] - self.road_width // 2, 0, self.road_width, self.height))

        # Drawing the horizontal road
        pygame.draw.rect(self.screen, self.intersection_colors["BLACK"],
                         (0, self.center[1] - self.road_width // 2, self.width, self.road_width))

        # Drawing lanes for each road and naming them
        # West lane
        pygame.draw.line(self.screen, self.intersection_colors["YELLOW"], (0, self.center[1]),
                         (self.center[0] - self.road_width // 2, self.center[1]), 2)
        text = self.font.render('West', True, self.intersection_colors["WHITE"])
        self.screen.blit(text, (self.center[0] // 2, self.center[1] - 10))

        # East lane
        pygame.draw.line(self.screen, self.intersection_colors["YELLOW"],
                         (self.center[0] + self.road_width // 2, self.center[1]),
                         (self.width, self.center[1]), 2)
        text = self.font.render('East', True, self.intersection_colors["WHITE"])
        self.screen.blit(text, (self.center[0] // 2 + self.center[0], self.center[1] - 10))

        # North lane
        pygame.draw.line(self.screen, self.intersection_colors["YELLOW"], (self.center[0], 0),
                         (self.center[0], self.center[1] - self.road_width // 2), 2)
        text = self.font.render('North', True, self.intersection_colors["WHITE"])
        self.screen.blit(text, (self.center[0] - 30, self.center[1] // 2))

        # South lane
        pygame.draw.line(self.screen, self.intersection_colors["YELLOW"],
                         (self.center[0], self.center[1] + self.road_width // 2),
                         (self.center[0], self.height), 2)
        text = self.font.render('South', True, self.intersection_colors["WHITE"])
        self.screen.blit(text, (self.center[0] - 30, self.center[1] // 2 + self.center[1]))


class Crossing:

    def __init__(self, screen, intersection_center, road_width, intersection_trl_width, intersection_colors):
        self.screen = screen
        self.intersection_center = intersection_center
        self.intersection_colors = intersection_colors
        self.road_width = road_width
        self.intersection_trl_width = intersection_trl_width

    def draw(self):
        # Crossing parameters for the west lane
        west_crossing_x = self.intersection_center[0] - self.road_width // 2 - 25 - 5
        west_crossing_y = self.intersection_center[1] - self.road_width // 2
        pygame.draw.rect(self.screen, self.intersection_colors["GRAY"],
                         (west_crossing_x, west_crossing_y, self.intersection_trl_width, self.road_width))

        # Crossing for the east lane
        east_crossing_x = self.intersection_center[0] + self.road_width // 2
        east_crossing_y = west_crossing_y
        pygame.draw.rect(self.screen, self.intersection_colors["GRAY"],
                         (east_crossing_x, east_crossing_y, self.intersection_trl_width, self.road_width))

        # Crossing for the north lane
        north_crossing_x = self.intersection_center[0] - self.road_width // 2
        north_crossing_y = self.intersection_center[1] - self.road_width // 2 - 25
        pygame.draw.rect(self.screen, self.intersection_colors["GRAY"],
                         (north_crossing_x, north_crossing_y, self.road_width, 25))

        # Crossing for the south lane
        south_crossing_x = north_crossing_x
        south_crossing_y = self.intersection_center[1] + self.road_width // 2
        pygame.draw.rect(self.screen, self.intersection_colors["GRAY"],
                         (south_crossing_x, south_crossing_y, self.road_width, 25))


class TrafficLights:
    def __init__(self, screen, current_traffic_light, current_light_state, traffic_lights_directions, trl_colors,
                 traffic_light_width, intersection_center, road_width, intersection_trl_width,
                 traffic_light_change_times):
        self.screen = screen
        self.current_traffic_light_index = traffic_lights_directions.index(current_traffic_light)
        self.current_light_state = current_light_state
        self.traffic_lights_directions = traffic_lights_directions
        self.trl_colors = trl_colors
        self.traffic_light_width = traffic_light_width
        self.intersection_center = intersection_center
        self.road_width = road_width
        self.intersection_trl_width = intersection_trl_width
        self.traffic_light_change_times = traffic_light_change_times
        self.last_change_time = pygame.time.get_ticks()

    def draw(self):
        # Initialize all traffic lights to red
        north_color = self.trl_colors["RED_TR"]
        south_color = self.trl_colors["RED_TR"]
        east_color = self.trl_colors["RED_TR"]
        west_color = self.trl_colors["RED_TR"]

        light_color = None

        # Determine the color based on current state
        if self.current_light_state == "GREEN":
            light_color = self.trl_colors["GREEN_TR"]
        elif self.current_light_state == "YELLOW":
            light_color = self.trl_colors["YELLOW_TR"]
        elif self.current_light_state == "RED":
            light_color = self.trl_colors["RED_TR"]

        # Set the color of the current traffic light
        if self.current_traffic_light == "north":
            north_color = light_color
        elif self.current_traffic_light == "south":
            south_color = light_color
        elif self.current_traffic_light == "east":
            east_color = light_color
        elif self.current_traffic_light == "west":
            west_color = light_color

        # Drawing traffic lights with the updated colors
        # North traffic light
        north_traffic_light_width = self.traffic_light_width * 2
        north_traffic_light_pos = (self.intersection_center[0] - north_traffic_light_width // 2,
                                   self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width)
        pygame.draw.rect(self.screen, north_color, (*north_traffic_light_pos, north_traffic_light_width, 5))

        # South traffic light
        south_traffic_light_width = self.traffic_light_width * 2
        south_traffic_light_pos = (self.intersection_center[0] - south_traffic_light_width // 2,
                                   self.intersection_center[1] + self.road_width // 2 - 5 + self.intersection_trl_width)
        pygame.draw.rect(self.screen, south_color, (*south_traffic_light_pos, south_traffic_light_width, 5))

        # East traffic light
        east_traffic_light_height = self.traffic_light_width * 2
        east_traffic_light_pos = (self.intersection_center[0] + self.road_width // 2 + self.intersection_trl_width,
                                  self.intersection_center[1] - east_traffic_light_height // 2)
        pygame.draw.rect(self.screen, east_color, (*east_traffic_light_pos, 5, east_traffic_light_height))

        # West traffic light
        west_traffic_light_height = self.traffic_light_width * 2
        west_traffic_light_pos = (self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 5,
                                  self.intersection_center[1] - west_traffic_light_height // 2)
        pygame.draw.rect(self.screen, west_color, (*west_traffic_light_pos, 5, west_traffic_light_height))

    def update(self, current_time):
        # Logic to change the state of the traffic lights
        if self.current_light_state == "GREEN" and current_time - self.last_change_time >= \
                self.traffic_light_change_times[
                    "GREEN"] * 1000:
            self.current_light_state = "YELLOW"
            self.last_change_time = current_time
        elif self.current_light_state == "YELLOW" and current_time - self.last_change_time >= \
                self.traffic_light_change_times["YELLOW"] * 1000:
            self.current_light_state = "RED"
            self.last_change_time = current_time
            self.current_traffic_light_index = (self.current_traffic_light_index + 1) % len(
                self.traffic_lights_directions)
        elif self.current_light_state == "RED" and current_time - self.last_change_time >= \
                self.traffic_light_change_times[
                    "RED"] * 1000:
            self.current_light_state = "GREEN"
            self.last_change_time = current_time

        self.current_traffic_light = self.traffic_lights_directions[self.current_traffic_light_index]

        return self.current_traffic_light, self.current_light_state


class Vehicle:
    def __init__(self, screen, radius, width, speed):
        self.screen = screen
        self.radius = radius
        self.width = width
        self.speed = speed
        self.x = None
        self.y = None
        self.direction = None
        self.color = None
        self.moving = True
        self.out_going_direction = None

    def generate_vehicle(self, vehicle_spawn_coords, vehicle_incoming_direction, vehicle_direction_color):
        self.direction = random.choice(vehicle_incoming_direction)
        self.x, self.y = vehicle_spawn_coords[self.direction]
        self.out_going_direction = random.choice(["straight", "left", "right"])
        self.color = vehicle_direction_color[self.out_going_direction]

    def move(self, current_traffic_light, current_light_state, thresholds, vehicle_turning_points):
        threshold = thresholds[self.direction]
        # print(f"Threshold value: {threshold}")
        # print(f"Outgoing direction: {self.out_going_direction}")
        if self.out_going_direction == "left":
            current_turning_point = vehicle_turning_points["left"][self.direction]
        else:
            current_turning_point = vehicle_turning_points["right"][self.direction]

        # For vehicle coming from the west
        if self.direction == "west":
            if (current_traffic_light == "west" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x > threshold):
                if self.out_going_direction == "straight":
                    self.x += self.speed
                elif self.out_going_direction == "left":
                    if self.x < current_turning_point:
                        self.x += self.speed
                    else:
                        self.y -= self.speed
                else:
                    if self.x < current_turning_point:
                        self.x += self.speed
                    else:
                        self.y += self.speed
            else:
                if self.x < threshold:
                    self.x += self.speed

        # For vehicle coming from the east
        elif self.direction == "east":
            if (current_traffic_light == "east" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x < threshold):
                if self.out_going_direction == "straight":
                    self.x -= self.speed
                elif self.out_going_direction == "left":
                    if self.x > current_turning_point:
                        self.x -= self.speed
                    else:
                        self.y += self.speed

                else:
                    if self.x > current_turning_point:
                        self.x -= self.speed
                    else:
                        self.y -= self.speed
            else:
                if self.x > threshold:
                    self.x -= self.speed

        # For vehicle coming from the north
        elif self.direction == "north":
            if (current_traffic_light == "north" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y > threshold):
                if self.out_going_direction == "straight":
                    self.y += self.speed
                elif self.out_going_direction == "left":
                    if self.y < current_turning_point:
                        self.y += self.speed
                    else:
                        self.x += self.speed
                else:
                    if self.y < current_turning_point:
                        self.y += self.speed
                    else:
                        self.x -= self.speed
            else:
                if self.y < threshold:
                    self.y += self.speed

        # For vehicle coming from the south
        elif self.direction == "south":
            if (current_traffic_light == "south" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y < threshold):
                if self.out_going_direction == "straight":
                    self.y -= self.speed
                elif self.out_going_direction == "left":
                    if self.y > current_turning_point:
                        self.y -= self.speed
                    else:
                        self.x -= self.speed
                else:
                    if self.y > current_turning_point:
                        self.y -= self.speed
                    else:
                        self.x += self.speed
            else:
                if self.y > threshold:
                    self.y -= self.speed

        # Debug information
        # print(f"Direction: {self.direction}")
        # print(f"X: {self.x} | Y: {self.y}")

        return self.x, self.y

    def draw(self):
        # print(f"Color: {self.color}")
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius, self.width)

    def kill_vehicle(self, width, height):
        # Check if the vehicle is out of bounds
        out_of_bounds = self.x < 0 or self.x > width or self.y < 0 or self.y > height
        return out_of_bounds


class SARSA:
    def __init__(self):

        pygame.init()
        pygame.font.init()

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

        self.intersection_colors = {
            "BLACK": (0, 0, 0),
            "GREEN": (26, 93, 26),
            "RED": (255, 0, 0),
            "YELLOW": (255, 255, 0),
            "GRAY": (128, 128, 128),
            "WHITE": (255, 255, 255)
        }

        # crossing thresholds
        self.thresholds = {
            "west": self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 30,
            "east": self.intersection_center[
                        0] - self.road_width // 2 + self.road_width + self.intersection_trl_width + 30,
            "north": self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width - 30,
            "south": self.intersection_center[1] + self.road_width - 15
        }

        # traffic light parameters and colors
        self.trl_colors = {
            "YELLOW_TR": (255, 255, 0),
            "GREEN_TR": (78, 228, 78),
            "RED_TR": (255, 0, 0)
        }

        self.traffic_lights_directions = ["north", "east", "south", "west"]
        # creating the starting point for the traffic light rotation
        self.starting_traffic_light = random.choice(self.traffic_lights_directions)
        self.traffic_light_change_times = {
            "RED": 5,
            "GREEN": 5,
            "YELLOW": 2
        }

        # vehicle parameters
        self.vehicle_radius = 15
        self.vehicle_width = 15
        # vehicle speed
        self.vehicle_speed = 0.25
        # direction of a vehicle after the traffic light turns green
        self.vehicle_direction_color = {
            "straight": (255, 163, 60),
            "left": (135, 196, 255),
            "right": (255, 75, 145)
        }
        # the direction from which a vehicle is generated
        self.vehicle_incoming_direction = ["north", "east", "south", "west"]
        # vehicle spawn coordinates
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

        self.vehicle_list = []
        self.font = pygame.font.SysFont(name=None, size=36)

    def vehicle_generator(self, screen, stop_event, vehicle_list_lock):
        while not stop_event.is_set():
            vehicle = Vehicle(self.screen, self.vehicle_radius, self.vehicle_width, self.vehicle_speed)
            vehicle.generate_vehicle(self.vehicle_spawn_coords, self.vehicle_incoming_direction,
                                     self.vehicle_direction_color)
            with vehicle_list_lock:
                self.vehicle_list.append(vehicle)
            time.sleep(0.5)

    def run(self):

        # Set up the display
        screen = pygame.display.set_mode((self.width, self.height))

        # Create Intersection, Crossing, and Traffic Lights
        intersection = Intersection(screen, self.intersection_center, self.road_width, self.intersection_colors,
                                    self.width, self.height, self.font)
        crossing = Crossing(screen, self.intersection_center, self.road_width, self.intersection_trl_width,
                            self.intersection_colors)
        current_light_state = "GREEN"
        traffic_lights = TrafficLights(screen, self.starting_traffic_light, current_light_state,
                                       self.traffic_lights_directions, self.trl_colors, self.traffic_light_width,
                                       self.intersection_center, self.road_width, self.intersection_trl_width,
                                       self.traffic_light_change_times)

        # Vehicle management
        vehicle_list_lock = threading.Lock()
        stop_event = threading.Event()

        # Start the vehicle generator thread
        vehicle_gen_thread = threading.Thread(target=self.vehicle_generator,
                                              args=(screen, stop_event, vehicle_list_lock))
        vehicle_gen_thread.start()

        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            current_time = pygame.time.get_ticks()
            current_traffic_light, current_light_state = traffic_lights.update(current_time)

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

            pygame.display.flip()

        # Clean up and exit
        stop_event.set()
        vehicle_gen_thread.join()
        pygame.quit()


if __name__ == "__main__":
    sarsa = SARSA()
    sarsa.run()
