from random import randint
from json import *
from turtle import *

from genFunc import function as func

class TurtleCompatible:
    @staticmethod
    def init_turtle():
        hideturtle()
        up()
        speed(0)

    @staticmethod
    def draw_square(size=5, turn="l"):
        if not isdown():
            down()
        begin_fill()
        for i in range(4):
            fd(size - 1)
            if turn in ("l", "left"):
                lt(90)
            elif turn in ("r", "right"):
                rt(90)
        end_fill()
        up()

    @staticmethod
    def terminate():
        done()


class Wall(TurtleCompatible):
    def __init__(self, allocation, wall_type=None, side=""):
        self.wall_type = wall_type
        self.allocation = [allocation]
        self.side = side

    def get_wall_type(self):
        return self.wall_type

    def get_allocation(self):
        return self.allocation

    def get_side(self):
        return self.side

    def get_opposite_side(self):
        """Give the opposite side (direction) of this wall"""
        directions = ("n", "e", "s", "w")
        for i in range(len(directions)):
            if self.side == directions[i]:
                return directions[i - 2]
        return directions[0]  # dummy

    def set_wall_type(self, wall_type):
        self.wall_type = wall_type

    def set_allocation(self, allocation):
        for side in range(2):
            if self.allocation[1] is None:
                self.allocation.append(allocation)

    def set_side(self, side):
        self.side = side

    def other_side(self):
        """Give the position of the tile behind this wall"""
        known_side = list(self.allocation[0].base_pos())
        if self.side == "n":
            known_side[1] += 1
        elif self.side == "s":
            known_side[1] -= 1
        elif self.side == "e":
            known_side[0] += 1
        elif self.side == "w":
            known_side[0] -= 1
        return tuple(known_side)

    def draw(self, size):
        color("#000000")
        x, y = xcor(), ycor()
        if self.wall_type == "em":
            fd(size + 1)
            rt(90)
            fd(1)
            self.draw_square(size)
            bk(size + 1)
            lt(90)
            self.draw_square(size)
            bk(1)
        elif self.wall_type == "wa":
            fd(1)
            self.draw_square(size)
            bk(1)
        elif self.wall_type == "do":
            color("#00FFFF")
            fd(1)
            self.draw_square(size)
            fd(size)
            self.draw_square(size)
            color("#000000")
            bk(1)
        goto(x, y)

    def goto_draw_pos(self, size):
        if self.side == "n":
            fd(size - 1)
            lt(90)
            fd(size - 1)
            self.draw(size)
            bk(size - 1)
            rt(90)
            bk(size - 1)
        elif self.side == "w":
            lt(90)
            fd(size - 1)
            lt(90)
            self.draw(size)
            rt(90)
            bk(size - 1)
            rt(90)
        elif self.side == "s":
            rt(90)
            self.draw(size)
            lt(90)
        else:
            fd(size - 1)
            self.draw(size)
            bk(size - 1)


class Tile(TurtleCompatible):
    def __init__(self, allocation=None, walls=None, relative_pos=(0, 0), content=None):
        self.walls = {}
        for direction in ("n", "s", "w", "e"):
            if direction not in walls.keys():
                self.walls[direction] = Wall(self, "em", direction)
            else:
                self.walls[direction] = Wall(self, walls[direction], direction)
        self.relative_pos = relative_pos
        self.content = content
        self.allocation = allocation

    def base_pos(self):
        return tuple([self.relative_pos[i] + self.allocation.get_base_pos()[i] for i in range(len(self.relative_pos))])

    def get_allocation(self):
        return self.allocation

    def get_walls(self):
        return self.walls

    def get_relative(self):
        return self.relative_pos

    def get_content(self):
        return self.content

    def set_allocation(self, allocation):
        self.allocation = allocation

    def set_wall(self, key: str, value: Wall):
        self.walls[key] = value

    def set_relative_pos(self, relative_pos=(0, 0)):
        self.relative_pos = relative_pos

    def set_content(self, content):
        self.content = content

    def draw(self, size):
        goto(self.base_pos()[0] * 5 * size, self.base_pos()[1] * 5 * size)
        color("#000000")
        # baliser la tuile
        if self.relative_pos == (0, 0):  # basepos = vert
            color("#00FF00")
        rt(90)
        fd(1)
        rt(90)
        fd(1)
        self.draw_square(size)
        for i in range(3):
            rt(90)
            fd(size + 1)
            self.draw_square(size)
        bk(1)
        lt(90)
        bk(size)
        # mettre les murs
        for wall in self.walls.values():
            wall.goto_draw_pos(size)
        # mettre le contenu
        goto(self.base_pos()[0] * 5 * size, self.base_pos()[1] * 5 * size)
        if self.get_content() is not None:
            color("#FFFF00")
            self.draw_square(size)
            color("#000000")

    def get_compiled(self):
        dic = {"relative_pos": self.relative_pos,
                "walls": {wall.get_side(): wall.get_wall_type() for wall in self.walls.values()}}
        if self.content is not None:
            dic["content"] = self.content
        return dic


class Room(TurtleCompatible):
    def __init__(self, composition: list, base_pos=(0, 0), weight=1):
        self.weight = weight
        self.base_pos = base_pos
        self.compo = composition  # exemple de composition : self.compo = (Tile(self, relative_pos=(0, 0)))
        for tile in self.compo:
            tile.set_allocation(self)

    def get_base_pos(self):
        return self.base_pos

    def get_composition(self):
        return self.compo

    def get_weight(self):
        return self.weight

    def set_base_pos(self, base_pos=(0, 0)):
        self.base_pos = base_pos

    def add_compo(self, tile: Tile):
        self.compo.append(tile)

    def del_compo(self, index):
        if index < len(self.compo):
            del (self.compo[index])

    def copy(self):
        tiles = []
        for tile in self.compo:
            walls = {}
            for side, wall in tile.get_walls().items():
                walls[side] = wall.get_wall_type()
            tiles.append(Tile(None, walls, relative_pos=tile.get_relative(), content=tile.get_content()))
        copy = Room(tiles, base_pos=self.base_pos, weight=self.weight)
        return copy

    def rotate(self, anticlokwise=False):
        polarity = int(anticlokwise)
        tiles = []
        for tile in self.compo:
            walls = {}
            for side, wall in tile.get_walls().items():
                directions = ("n", "w", "s", "e")
                rotated_side = directions[directions.index(side) - (1 - 2 * polarity) - 4 * polarity]
                walls[rotated_side] = wall.get_wall_type()
            relative_pos = (tile.get_relative()[1] * (1 - 2 * polarity),
                            tile.get_relative()[0] * (2 * polarity - 1))
            tiles.append(Tile(None, walls, relative_pos=relative_pos, content=tile.get_content()))
        rotation = Room(tiles, base_pos=self.base_pos, weight=self.weight)
        return rotation

    def mirror(self, y_axis=False):
        polarity = int(y_axis)
        tiles = []
        for tile in self.compo:
            walls = {}
            directions = ("n", "w", "s", "e")
            walls[directions[polarity]], walls[directions[polarity + 2]] = \
                tile.get_walls()[directions[polarity + 2]].get_wall_type(), \
                tile.get_walls()[directions[polarity]].get_wall_type()
            relative_pos = (tile.get_relative()[0] * (1 - 2 * polarity),
                            tile.get_relative()[1] * (2 * polarity - 1))
            walls[directions[polarity - 1]] = tile.get_walls()[directions[polarity - 1]].get_wall_type()
            walls[directions[polarity + 1]] = tile.get_walls()[directions[polarity + 1]].get_wall_type()
            tiles.append(Tile(None, walls, relative_pos=relative_pos, content=tile.get_content()))
        mirror = Room(tiles, base_pos=self.base_pos, weight=self.weight)
        return mirror

    def add_all_instances(self, maze):
        room = self.copy()
        for i in range(4):
            rotated_room = room
            if i == 1:
                rotated_room = room.rotate()
            elif i == 2:
                rotated_room = room.rotate(True)
            elif i == 3:
                rotated_room = room.rotate()
                rotated_room = rotated_room.rotate()
            for j in range(4):
                mirrored_room = rotated_room
                if j == 1:
                    mirrored_room = rotated_room.mirror()
                elif j == 2:
                    mirrored_room = rotated_room.mirror(True)
                elif j == 3:
                    mirrored_room = rotated_room.mirror()
                    mirrored_room = mirrored_room.mirror(True)
                maze.add_room(mirrored_room)

    def __repr__(self):
        str_room = "["
        for tile in self.compo:
            str_room += 'Tile(walls={"s": "%s", "n": "%s", "w": "%s", "e": "%s"}, relative_pos=%s' \
                        % (tile.get_walls()["s"].get_wall_type(), tile.get_walls()["n"].get_wall_type(),
                           tile.get_walls()["w"].get_wall_type(), tile.get_walls()["e"].get_wall_type(),
                           tile.get_relative())
            if tile.get_content() is not None:
                str_room += ", content=" + tile.get_content()
            if tile == self.compo[-1]:
                str_room += ")],\n"
            else:
                str_room += "),\n"
        str_room += "base_pos=%s, weight=%s)" % (self.base_pos, self.weight)
        return str_room

    def draw(self, size):
        for tile in self.compo:
            tile.draw(size)

    def get_compiled(self):
        return {"composition": [tile.get_compiled() for tile in self.compo],
                "base_pos": self.base_pos, "weight": self.weight}


class Maze(TurtleCompatible):
    def __init__(self, source, roots, length=100, draw_size=0, metadata=None):
        if type(metadata) == dict:
            self.metadata = metadata
        else:
            self.metadata = {}
        self.roots = roots
        self.draw_size = draw_size
        if type(source) == Maze:
            self.rooms = [self.roots[0]]
            if draw_size > 0:
                self.init_turtle()
                self.rooms[0].draw(draw_size)
            # preparing create() :
            self.source = source.get_rooms()
            self.door_queue = self.update_door_queue()
            self.length = length
            self.create()
        elif type(source) == str:
            if "palette" in source:
                self.rooms = []
                rooms, self.metadata = self.open(source)
                self.metadata["palette_rooms"] = rooms
                for room in self.metadata["palette_rooms"]:
                    room.add_all_instances(self)
                if draw_size > 0:
                    self.init_turtle()
                    self.draw()
            else:
                self.rooms, self.metadata = self.open(source)
                if draw_size > 0:
                    self.init_turtle()
                    self.draw()
            self.door_queue = self.update_door_queue()
        elif type(source) == list:
            self.rooms = []
            self.metadata["palette_rooms"] = source
            for room in source:
                room.add_all_instances(self)
            if draw_size > 0:
                self.init_turtle()
                self.draw()
            self.door_queue = self.update_door_queue()

    def get_rooms(self):
        return self.rooms

    def add_room(self, room: Room):
        self.rooms.append(room)

    def del_room(self, index):
        if index < len(self.rooms):
            del (self.rooms[index])

    def update_door_queue(self):
        """Get all the doors to close. They are encoded like this : (empty_position:tuple, direction:str, directory:tuple)"""
        door_queue = []
        for i in range(len(self.rooms)):
            for j in range(len(self.rooms[i].get_composition())):
                for wall in self.rooms[i].get_composition()[j].get_walls().values():
                    if self.is_empty(wall.other_side()) and wall.get_wall_type() == "do":
                        door_queue.append((wall.other_side(), wall.get_opposite_side(), (i, j, wall.get_side())))
        return door_queue

    def is_empty(self, base_pos=(0, 0)):
        for room in self.rooms:
            for tile in room.get_composition():
                if tile.base_pos() == base_pos:
                    return False
        return True

    def do_in_tile(self, location=(0, 0), method=None):
        if method is None:
            if len(self.rooms) >= location[0] and len(self.rooms[location[0]].get_composition()) >= location[1]:
                return True
            else:
                return False
        elif method == "base_pos":
            if self.do_in_tile(location):
                return self.rooms[location[0]].get_composition()[location[1]].base_pos()
            else:  # dummy
                return False  # dummy
        else:  # dummy
            return False  # dummy

    def do_in_wall(self, location=(0, 0, "n"), method=None):
        assert location[2] in ("n", "s", "e", "w")
        if method is None:
            if len(self.rooms) >= location[0] and len(self.rooms[location[0]].get_composition()) >= location[1] \
                    and self.rooms[location[0]].get_composition()[location[1]].get_walls()[location[2]] is not None:
                return True
            else:
                return False
        else:
            if self.do_in_wall(location):
                wall = self.rooms[location[0]].get_composition()[location[1]].get_walls()[location[2]]
                if method == "other_side":
                    return wall.other_side()
                elif method[0:3] == "get":
                    if method[4:] == "wall_type":
                        return wall.get_wall_type()
                    else:  # dummy
                        return False  # dummy
                else:  # dummy
                    return False  # dummy
            else:  # dummy
                return False  # dummy

    def get_tile(self, base_pos=(0, 0)):
        for i in range(len(self.rooms)):
            current_room = self.rooms[i]
            for j in range(len(current_room.get_composition())):
                if self.do_in_tile((i, j), "base_pos") == base_pos:
                    return i, j
        return False  # dummy

    def select_rooms(self, weight, selection_mode = ""):
        selectedr = []
        if selection_mode == "genFunc.func":
            target, interval = func(self.length, weight)
            selectedr = [room for room in self.source if target - interval >= room.get_weight() >= target + interval]
        if selection_mode == "randomPonderatedWeight":
            total_weight = 0
            for room in self.source:
                total_weight += room.get_weight()

        else:
            selectedr = self.source
        if len(selectedr) == 0:
            selectedr = self.source
            print("not enough room ... taking to source")
        return selectedr

    def create(self):
        weight = 0
        tries = 0
        while weight < self.length and tries < 1000:  # proper maze construction
            rooms_len = len(self.rooms)
            possible_rooms = self.select_rooms(weight = weight, selection_mode="genFunc.func")
            selected_room = possible_rooms[randint(0, len(possible_rooms) - 1)].copy()
            self.insert(self.door_queue[randint(0, len(self.door_queue) - 1)], selected_room)
            if len(self.rooms) != rooms_len:
                weight += selected_room.get_weight()
                if self.draw_size > 0:
                    self.rooms[-1].draw(self.draw_size)
            tries += 1
        # from now on : insertion of the end room
        rooms_len = len(self.rooms)
        if len(self.door_queue) == 0:
            print("door queue empty. creating new doors ...")
            self.del_room(-1)
            self.door_queue = self.update_door_queue()
        for door in self.door_queue:
            if rooms_len == len(self.rooms):
                self.insert(door, self.roots[1].copy())
        if self.draw_size > 0:
            self.rooms[-1].draw(self.draw_size)
        if weight >= self.length:
            print("maze successfully constructed")
            self.post_creation_fill(0)
        else:
            print("Maze creation aborded. Tries limit reached. Weight :", weight)

    def preinsert(self, selected_door, selected_room: Room):
        print("Starting pre-insertion ... insertion prints doesn't count")
        old_rooms = self.rooms.copy()
        self.insert(selected_door, selected_room)
        print("Pre-insertion finished")
        if len(self.rooms) != old_rooms:
            del(self.rooms[-1])
            return True
        else:
            return False

    def insert(self, selected_door, selected_room: Room):
        validation = True
        for tile in selected_room.get_composition():
            if tile.get_walls()[selected_door[1]].get_wall_type() == "do":
                selected_room.set_base_pos((selected_door[0][0] - tile.get_relative()[0],
                                            selected_door[0][1] - tile.get_relative()[1]))
        for tile in selected_room.get_composition():
            if self.is_empty(tile.base_pos()):
                for side, vector in {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}.items():
                    adjacent_base_pos = (tile.base_pos()[0] + vector[0], tile.base_pos()[1] + vector[1])
                    if not self.is_empty(adjacent_base_pos):
                        location = list(self.get_tile(adjacent_base_pos))
                        location.append(tile.get_walls()[side].get_opposite_side())
                        if tile.get_walls()[side].get_wall_type() != self.do_in_wall(tuple(location), "get_wall_type"):
                            print("ERROR : wall type is not matching", location)
                            validation = False
            else:
                print("ERROR : occupied place", tile.base_pos())
                validation = False
        if validation:
            print("Room successfully added in index", len(self.rooms))
            self.add_room(selected_room)
            self.door_queue = self.update_door_queue()

    def post_creation_fill(self, weight_limit):
        print("starting post-creation fill ... a draw will be necessary afterward")
        while len(self.door_queue) != 0:
            door = self.door_queue[0]
            possible_rooms = [room for room in self.source if room.get_weight() <= weight_limit and self.preinsert(door, room)]
            if len(possible_rooms) == 0:
                location = door[2]
                self.rooms[location[0]].get_composition()[location[1]].get_walls()[location[2]].set_wall_type("wa")
                self.door_queue = self.update_door_queue()
                print("door transformed into wall. %s doors remaining" % len(self.door_queue))
            else:
                self.insert(door, possible_rooms[randint(0, len(possible_rooms) - 1)])
                print("door completed with a room. %s doors remaining" % len(self.door_queue))
        print("post-creation fill finished")

    def draw(self, size=0):
        for room in self.rooms:
            if size < 1 and self.draw_size > size:
                room.draw(self.draw_size)
            elif self.draw_size < 1 and size > self.draw_size:
                self.init_turtle()
                room.draw(size)

    @staticmethod
    def open(file_name: str):
        if file_name[-5:] == ".json":
            file_name = file_name[:-4]
        with open(file_name+".json", "r") as f:
            data = load(f)
        rooms = []
        for room in data["rooms"]:
            tiles = []
            for tile in room["composition"]:
                tile["relative_pos"] = tuple(tile["relative_pos"])
                tiles.append(Tile(**tile))
            room["composition"] = tiles
            room["base_pos"] = tuple(room["base_pos"])
            rooms.append(Room(**room))
        return rooms, data

    def save(self, file_name: str):
        if file_name == "":
            file_name = input("Save as (.json will be apply if not present) : ")
        print("saving as", file_name)
        if file_name[-5:] == ".json":
            file_name = file_name[:-4]
        data = self.metadata
        if "palette" in file_name:
            data["rooms"] = [room.get_compiled() for room in self.metadata["palette_rooms"]]
            del(self.metadata["palette_rooms"])
        else:
            data["rooms"] = [room.get_compiled() for room in self.rooms]
        with open(file_name+".json", "w") as f:
            dump(data, f)
        print("file saved")


class DFS:
    def __init__(self, maze: Maze, start_index=0):
        self.maze = maze
        self.index = start_index
        self.explored = []
        self.to_explore = [self.index]
        self.items = []

    def get_outside(self):
        external_rooms = []
        for tile in self.maze.get_rooms()[self.index].get_composition():
            for wall in tile.get_walls().values():
                if wall.get_wall_type() == "do" and not self.maze.is_empty(wall.other_side()):
                    if self.maze.get_tile(wall.other_side())[0] != self.index:
                        external_rooms.append(self.maze.get_tile(wall.other_side())[0])
        return external_rooms

    def explore(self):
        for tile in self.maze.get_rooms()[self.index].get_composition():
            if tile.get_content() is not None:
                self.items.append(tile.get_content())
        del (self.to_explore[-1])
        for room in self.get_outside():
            if not (room in self.to_explore or room in self.explored):
                self.to_explore.append(room)
        self.explored.append(self.index)
        print("To explore :", self.to_explore, ". Explored :", self.explored)

    def map(self, goal="end", draw = None):
        if draw is not None:
            self.maze.init_turtle()
        if goal is None:
            while len(self.explored) != len(self.maze.get_rooms()):
                pass  # to do
        else:
            while goal not in self.items:
                self.explore()
                if len(self.explored) != len(self.maze.get_rooms()):
                    self.index = self.to_explore[-1]
                print("Place :", self.index, ". Inventory :", self.items)
                if draw is not None:
                    self.maze.get_rooms()[self.explored[-1]].draw(draw)
        if draw is not None:
            self.maze.terminate()
