"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random, math


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x - 10, self.y - 10,
                               self.x + 10, self.y + 10)
            self.canvas.coords(self.__id2, self.x - 10, self.y + 10,
                               self.x + 10, self.y - 10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int],
                 size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown",
                                                 width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x - self.size / 2, self.x + self.size / 2
        y1, y2 = self.y - self.size / 2, self.y + self.size / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 coo_x: float,
                 coo_y: float,
                 speed: int):
        super().__init__(game)
        self.__id: int
        self.__size = size
        self.__color = color
        self.__speed = speed
        self.__coo_x = coo_x
        self.__coo_y = coo_y
        self.x = coo_x
        self.y = coo_y

    def create(self) -> None:
        self.id = self.canvas.create_oval(self.coo_x,
                                          self.coo_y,
                                          self.coo_x + self.size,
                                          self.coo_y + self.size,
                                          width=2,
                                          fill=self.color,
                                          outline=self.color)

    def render(self) -> None:
        self.canvas.coords(self.id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.id)

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
                (
                        self.x - self.size / 2 <= self.game.player.x <= self.x + self.size / 2)
                and
                (
                        self.y - self.size / 2 <= self.game.player.y <= self.y + self.size / 2)
        )

    def move_to(self, x, y) -> None:
        self.x = x
        self.y = y

    def hit_x(self):
        return not (0 <= self.x <= self.game.screen_width)

    def hit_y(self):
        return not (0 <= self.y <= self.game.screen_height)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, new):
        self.__id = new

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    @property
    def coo_x(self) -> float:
        """
        Get the coo of the enemy
        """
        return self.__coo_x

    @property
    def coo_y(self) -> float:
        """
        Get the coo of the enemy
        """
        return self.__coo_y

    @property
    def speed(self) -> int:
        """
        Get the coo of the enemy
        """
        return self.__speed


# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.


class RandomWalkEnemy(Enemy):
    """
    RandomWalkEnemy
    """

    def update(self) -> None:
        move_x = random.randint(-self.speed, self.speed)
        move_y = random.randint(-self.speed, self.speed)
        self.x += move_x
        self.y += move_y

        if self.hit_x():
            self.x -= move_x
        if self.hit_y():
            self.y -= move_y

        self.move_to(self.x, self.y)

        if self.hits_player():
            self.game.game_over_lose()


class ChasingEnemy(Enemy):
    """
    ChasingEnemy
    """

    def update(self) -> None:
        arc_tan = math.atan2(self.game.player.x - self.x,
                             self.game.player.y - self.y)
        move_x = math.sin(arc_tan) * self.speed
        move_y = math.cos(arc_tan) * self.speed
        self.x += move_x
        self.y += move_y

        if self.hit_x():
            self.x -= move_x
        if self.hit_y():
            self.y -= move_y

        self.move_to(self.x, self.y)

        if self.hits_player():
            self.game.game_over_lose()


class FencingEnemy(Enemy):
    """
    FencingEnemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 coo_x: float,
                 coo_y: float,
                 speed: int,
                 dis: float):
        super().__init__(game, size, color, coo_x, coo_y, speed)
        self.dis = dis

    def update(self) -> None:
        home_x = self.game.home.x
        home_y = self.game.home.y

        if (home_x-self.dis < 0 or
                home_y-self.dis < 0 or
                home_x+self.dis > self.game.screen_width or
                home_y+self.dis > self.game.screen_height):
            self.delete()

        if self.x == home_x - self.dis and self.y < home_y + self.dis:
            self.y += self.speed
        elif self.x < home_x + self.dis and self.y == home_y + self.dis:
            self.x += self.speed
        elif self.x == home_x + self.dis and self.y > home_y - self.dis:
            self.y -= self.speed
        elif self.x > home_x - self.dis and self.y == home_y - self.dis:
            self.x -= self.speed

        self.move_to(self.x, self.y)

        if self.hits_player():
            self.game.game_over_lose()


class LineYEnemy(Enemy):
    """
    LineYEnemy
    """
    count = 0

    def update(self) -> None:
        if self.y <= 0:
            self.count = 0
        elif self.y >= self.game.screen_height:
            self.count = 1

        if self.count == 0:
            self.y += self.speed
        else:
            self.y -= self.speed

        self.move_to(self.x, self.y)

        if self.hits_player():
            self.game.game_over_lose()


# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        distance_per = self.game.screen_width / (self.game.level + 1)
        distance_cur = 0

        for i in range(self.level):
            distance_cur += distance_per
            self.game.add_enemy(RandomWalkEnemy(self.game,
                                                10,
                                                "red",
                                                random.randint(0,
                                                               self.game.
                                                               screen_width),
                                                random.randint(0,
                                                               self.game.
                                                               screen_height),
                                                30))
            self.game.add_enemy(ChasingEnemy(self.game,
                                             15,
                                             "blue",
                                             random.randint(0,
                                                            self.game.
                                                            screen_width),
                                             random.randint(0,
                                                            self.game.
                                                            screen_height),
                                             3))
            self.game.add_enemy(LineYEnemy(self.game,
                                           5,
                                           "black",
                                           distance_cur,
                                           0,
                                           30))
            self.game.add_enemy(FencingEnemy(self.game,
                                             10,
                                             "purple",
                                             self.game.home.x - ((i+1)*30),
                                             self.game.home.y - ((i+1)*30),
                                             5,
                                             ((i+1)*30)))


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int,
                 level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height - 1,
                                          self.screen_width - 1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self,
                         (self.screen_width - 100, self.screen_height // 2),
                         20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>",
                         lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height // 2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Lose",
                                font=font,
                                fill="red")
