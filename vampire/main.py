import random
import matplotlib.pyplot as plt
import csv
import sys


MAP_SIZE_X = 15
MAP_SIZE_Y = 15
map_objects = []
file_path = "E:\\Book1.csv"


class Human:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.age = random.randint(10, 50)

    def move(self):
        dx, dy = random.choice([(0, random.randint(1, 4)), (0, -random.randint(1, 4)), (random.randint(1, 4), 0),
                                (-random.randint(1, 4), 0)])
        new_x = self.x + dx
        new_y = self.y + dy
        old = self.x + self.y
        self.x = max(0, min(new_x, MAP_SIZE_X - 1))
        self.y = max(0, min(new_y, MAP_SIZE_Y - 1))
        self.health -= abs((self.x + self.y) - old)

    def human_human_interaction(self, human):
        global map_objects
        probability_of_attack_human = 0.4
        if self in map_objects and human in map_objects:
            if random.random() < probability_of_attack_human:
                print("One human attacked on other")
                map_objects.remove(self)
                if self.health < 80:
                    self.health += 20
                else:
                    self.health = 100
                map_objects.append(self)
                map_objects.remove(human)
                human.health -= 20
                if human.health > 0:
                    map_objects.append(human)
                else:
                    print("Human got killed")
            else:
                print("2 humans are helping each other")
                map_objects.remove(self)
                map_objects.remove(human)
                if self.health <= 90:
                    self.health += 10
                else:
                    self.health = 100
                if human.health <= 90:
                    human.health += 10
                else:
                    human.health = 100
                map_objects.append(self)
                map_objects.append(human)


class Vampire:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health

    def move(self):
        dx, dy = random.choice([(0, random.randint(1, 8)), (0, -random.randint(1, 8)), (random.randint(1, 8), 0),
                                (-random.randint(1, 8), 0)])
        new_x = self.x + dx
        new_y = self.y + dy
        self.x = max(0, min(new_x, MAP_SIZE_X - 1))
        self.y = max(0, min(new_y, MAP_SIZE_Y - 1))

    def biting(self, human):
        global map_objects
        probability_of_attack = 0.7  # 70% chance of attack
        if self in map_objects and human in map_objects:
            if random.random() < probability_of_attack:
                print("A human is beaten by vampire and converted into vampire")
                map_objects.remove(human)
                new_vampire = Vampire(human.x, human.y, health=human.health)
                map_objects.append(new_vampire)
            else:
                map_objects.remove(self)
                print("Vampire got killed by the human")

    def vampire_vampire_interaction(self, vampire):
        global map_objects
        if self in map_objects and vampire in map_objects:
            map_objects.remove(vampire)
            map_objects.remove(self)
            if vampire.health <= 20 and self.health > 20:
                self.health -= 20
                map_objects.append(self)
                print("One vampire got killed and other one losed health")
            elif vampire.health > 20 and self.health <= 20:
                vampire.health -= 20
                map_objects.append(vampire)
                print("One vampire got killed and other one losed health")
            elif vampire.health > 20 and self.health > 20:
                vampire.health -= 20
                map_objects.append(vampire)
                self.health -= 20
                map_objects.append(self)
                print("Both vampires loosed health")
            else:
                print("Both vampires got killed by each other")


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Water:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Garlic:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def initialize_map(num_humans, num_vampires, num_food, num_water, num_garlic):
    map_objects1 = []
    for _ in range(num_humans):
        x = random.randint(0, MAP_SIZE_X - 1)
        y = random.randint(0, MAP_SIZE_Y - 1)
        human = Human(x, y)
        map_objects1.append(human)

    for _ in range(num_vampires):
        x = random.randint(0, MAP_SIZE_X - 1)
        y = random.randint(0, MAP_SIZE_Y - 1)
        vampire = Vampire(x, y, health=random.randint(50, 100))
        map_objects1.append(vampire)

    for _ in range(num_food):
        x = random.randint(0, MAP_SIZE_X - 1)
        y = random.randint(0, MAP_SIZE_Y - 1)
        food = Food(x, y)
        map_objects1.append(food)

    for _ in range(num_water):
        x = random.randint(0, MAP_SIZE_X - 1)
        y = random.randint(0, MAP_SIZE_Y - 1)
        water = Water(x, y)
        map_objects1.append(water)

    for _ in range(num_garlic):
        x = random.randint(0, MAP_SIZE_X - 1)
        y = random.randint(0, MAP_SIZE_Y - 1)
        garlic = Garlic(x, y)
        map_objects1.append(garlic)

    return map_objects1


# Implement the parameter sweep function
def visualize_map(map_objects1, timestep, fig, ax, plt , simulation_no):
    # Clear the previous plot
    # plt.clf()
    x_human, y_human = [], []
    x_vampire, y_vampire = [], []
    x_food, y_food = [], []
    x_water, y_water = [], []
    x_garlic, y_garlic = [], []

    for obj in map_objects1:
        if isinstance(obj, Human):
            x_human.append(obj.x)
            y_human.append(obj.y)
        elif isinstance(obj, Vampire):
            x_vampire.append(obj.x)
            y_vampire.append(obj.y)
        elif isinstance(obj, Food):
            x_food.append(obj.x)
            y_food.append(obj.y)
        elif isinstance(obj, Water):
            x_water.append(obj.x)
            y_water.append(obj.y)
        elif isinstance(obj, Garlic):
            x_garlic.append(obj.x)
            y_garlic.append(obj.y)

    ax.clear()
    ax.scatter(x_human, y_human, color='green', marker='o', label='Humans')
    ax.scatter(x_vampire, y_vampire, color='red', marker='X', label='Vampires')
    ax.scatter(x_food, y_food, color='yellow', marker='s', label='Food')
    ax.scatter(x_water, y_water, color='pink', marker='s', label='Water')
    ax.scatter(x_garlic, y_garlic, color='orange', marker='s', label='Garlic')

    plt.pause(0.25)  # Pause to see the update
    fig.canvas.flush_events()  # Flush the events

    if timestep == 4:
        plt.savefig(f"C:/Users/Abdullah Mazhar/Downloads/images/timestep_{timestep + 1}"
                    f"_simulation_{simulation_no}.png")


def interaction(map_object):
    for obj in map_object:
        if isinstance(obj, Human):
            for obj1 in map_object:
                if (((obj.x == obj1.x and abs(obj.y - obj1.y) < 4) or (
                        obj.y == obj1.y and abs(obj.x - obj1.x) < 4)) and obj1 != obj):
                    if isinstance(obj1, Human):
                        obj.human_human_interaction(obj1)
                    elif isinstance(obj1, Vampire):
                        obj1.biting(obj)
                    elif isinstance(obj1, Food):
                        if obj in map_object and obj1 in map_object:
                            print("A human has just eaten food")
                            map_object.remove(obj1)
                            map_object.remove(obj)
                            if obj.health <= 70:
                                obj.health += 30
                            else:
                                obj.health = 100
                            map_object.append(obj)
                    elif isinstance(obj1, Garlic):
                        if obj in map_object and obj1 in map_object:
                            print("A human has just eaten garlic")
                            map_object.remove(obj1)
                            map_object.remove(obj)
                            obj.health = 100
                            map_object.append(obj)
                    elif isinstance(obj1, Water):
                        if obj in map_object and obj1 in map_object:
                            print("A human just drank water")
                            map_object.remove(obj1)
                            map_object.remove(obj)
                            if obj.health <= 50:
                                obj.health += 50
                            else:
                                obj.health = 100
                            map_object.append(obj)

        elif isinstance(obj, Vampire):
            for obj1 in map_object:
                if (((obj.x == obj1.x and abs(obj.y - obj1.y) < 4) or (
                        obj.y == obj1.y and abs(obj.x - obj1.x) < 4)) and obj1 != obj):
                    if isinstance(obj1, Human):
                        obj.biting(obj1)
                    elif isinstance(obj1, Vampire):
                        obj.vampire_vampire_interaction(obj1)


def main(arg1, arg2):
    arg1 = int(arg1)
    arg2 = int(arg2)
    global map_objects
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_title(f"Timestep")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(0, MAP_SIZE_X - 1)
    ax.set_ylim(0, MAP_SIZE_Y - 1)
    num_timesteps = 5
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([f"before simulation {((arg1-1)*31) + (arg1 + (arg2 - (9 + arg1)))}", arg1, arg2])
    map_objects = initialize_map(
        arg1, arg2, 5, 5, 5
    )

    for timestep in range(num_timesteps):
        for obj in map_objects:
            if isinstance(obj, Human) or isinstance(obj, Vampire):
                obj.move()

        interaction(map_objects)
        human_count = 0
        vampire_count = 0
        for obj in map_objects:
            if isinstance(obj, Human):
                human_count += 1
            elif isinstance(obj, Vampire):
                vampire_count += 1
        visualize_map(map_objects, timestep, fig, ax, plt, ((arg1-1)*31) + (arg1 + (arg2 - (9 + arg1))))
        print(f"After {timestep} Timesteps {human_count} humans left, and {vampire_count} vampires left")
        result = f"After {timestep} Timesteps {human_count} humans left, and {vampire_count} vampires left"
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([f"After simulation {((arg1-1)*31) + (arg1 + (arg2 - (9 + arg1)))}", human_count, vampire_count])


if __name__ == "__main__":
    num_args = len(sys.argv) - 1
    arg11 = 0
    arg22 = 0
    if num_args >= 2:
        arg11 = sys.argv[1]
        arg22 = sys.argv[2]
        print("num_args", num_args)
        print("args1", arg11)
        print("args2", arg22)
        main(arg11, arg22)
