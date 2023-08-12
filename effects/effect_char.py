"""EffectCharacter class and supporting classes to initialize and manage the state of a single character from the input data."""

from dataclasses import dataclass, field


@dataclass
class Coord:
    """A coordinate with row and column values.

    Args:
        column (int): column value
        row (int): row value"""

    column: int
    row: int


@dataclass
class GraphicalEffect:
    """A class for storing terminal graphical modes and a color.

    Supported graphical modes:
    bold, dim, italic, underline, blink, inverse, hidden, strike

    Args:
        bold (bool): bold mode
        dim (bool): dim mode
        italic (bool): italic mode
        underline (bool): underline mode
        blink (bool): blink mode
        reverse (bool): reverse mode
        hidden (bool): hidden mode
        strike (bool): strike mode
        color (int): color code
    """

    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    reverse: bool = False
    hidden: bool = False
    strike: bool = False
    color: int = 0

    def disable_modes(self) -> None:
        """Disables all graphical modes."""
        self.bold = False
        self.dim = False
        self.italic = False
        self.underline = False
        self.blink = False
        self.reverse = False
        self.hidden = False
        self.strike = False


@dataclass
class AnimationUnit:
    """An AnimationUnit is a graphicaleffect with a symbol and duration. May be looping.

    Args:
        symbol (str): the symbol to show
        duration (int): the number of animation steps to use the AnimationUnit
        looping (bool): if True, the AnimationUnit will be recycled until the character reaches its final position
        graphicaleffect (GraphicalEffect): a GraphicalEffect object containing the graphical modes and color of the character
    """

    symbol: str
    duration: int
    looping: bool = False
    graphicaleffect: GraphicalEffect = field(default_factory=GraphicalEffect)

    def __post_init__(self):
        self.frames_played = 0


class EffectCharacter:
    """A single character from the input data. Contains the state of the character.

    An EffectCharacter object contains the symbol, animation units, graphical modes, waypoints, and coordinates for a single
    character from the input data. The EffectCharacter object is used by the Effect class to animate the character.

    Attributes:
        symbol (str): the character symbol.
        final_symbol (str): the symbol for the character in the input data.
        animation_units (list[AnimationUnit]): a list of AnimationUnit objects containing the animation units for the character.
        final_coord (Coord): the final coordinate of the character.
        current_coord (Coord): the current coordinate of the character. If different from the final coordinate, the character is moving.
        last_coord (Coord): the last coordinate of the character. Used to clear the last position of the character.
        target_coord (Coord): the target coordinate of the character. Used to determine the next coordinate to move to.
        waypoints (list[Coord]): a list of coordinates to move to. Used to determine the next target coordinate to move to.
        graphical_modes: (GraphicalEffects): a GraphicalEffects object containing the graphical modes of the character.
    """

    def __init__(self, symbol: str, input_column: int, input_row: int):
        """Initializes the EffectCharacter class.

        Args:
            symbol (str): the character symbol.
            input_column (int): the final column position of the character.
            input_row (int): the final row position of the character.
        """
        self.symbol: str = symbol
        "The current symbol for the character, determined by the animation units."
        self.input_symbol: str = symbol
        "The symbol for the character in the input data."
        self.alternate_symbol: str = symbol
        "An alternate symbol for the character to use when all AnimationUnits have been processed."
        self.use_alternate_symbol: bool = False
        "Set this flag if you want to use the alternate symbol"
        self.animation_units: list[AnimationUnit] = []
        self.input_coord: Coord = Coord(input_column, input_row)
        "The coordinate of the character in the input data."
        self.current_coord: Coord = Coord(input_column, input_row)
        "The current coordinate of the character. If different from the final coordinate, the character is moving."
        self.previous_coord: Coord = Coord(-1, -1)
        "The last coordinate of the character. Used to clear the last position of the character."
        self.target_coord: Coord = Coord(input_column, input_row)
        "The target coordinate of the character. Used to determine the next coordinate to move to."
        self.waypoints: list[Coord] = []
        "A list of coordinates to move to. Used to determine the next target coordinate to move to."
        self.graphical_effect: GraphicalEffect = GraphicalEffect()
        self.final_graphical_effect: GraphicalEffect = GraphicalEffect()
        # move_delta is the floating point distance to move each step
        self.move_delta: float = 0
        self.row_delta: float = 0
        self.column_delta: float = 0
        # tweened_column and tweened_row are the floating point values for the current column and row positions
        self.tweened_column: float = 0
        self.tweened_row: float = 0

    def move(self) -> None:
        """Moves the character one step closer to the target position."""
        self.previous_coord.column, self.previous_coord.row = self.current_coord.column, self.current_coord.row

        # if the character has reached the target coordinate, pop the next coordinate from the waypoints list
        # and reset the move_delta for recalculation
        if self.current_coord == self.target_coord and self.waypoints:
            self.target_coord = self.waypoints.pop(0)
            self.move_delta = 0

        column_distance = abs(self.current_coord.column - self.target_coord.column)
        row_distance = abs(self.current_coord.row - self.target_coord.row)
        # on first call, calculate the column and row movement distance to approximate an angled line
        if not self.move_delta:
            self.tweened_column = self.current_coord.column
            self.tweened_row = self.current_coord.row
            self.move_delta = min(column_distance, row_distance) / max(column_distance, row_distance, 1)
            if self.move_delta == 0:
                self.move_delta = 1

            if column_distance < row_distance:
                self.column_delta = self.move_delta
                self.row_delta = 1
            elif row_distance < column_distance:
                self.row_delta = self.move_delta
                self.column_delta = 1
            else:
                self.column_delta = self.row_delta = 1
        # adjust the column and row positions by the calculated delta, round down to int
        if self.current_coord.column < self.target_coord.column:
            self.tweened_column += self.column_delta
            self.current_coord.column = int(self.tweened_column)
        elif self.current_coord.column > self.target_coord.column:
            self.tweened_column -= self.column_delta
            self.current_coord.column = int(self.tweened_column)
        if self.current_coord.row < self.target_coord.row:
            self.tweened_row += self.row_delta
            self.current_coord.row = int(self.tweened_row)
        elif self.current_coord.row > self.target_coord.row:
            self.tweened_row -= self.row_delta
            self.current_coord.row = int(self.tweened_row)

    def step_animation(self) -> None:
        """Steps the animation by one unit. Removes the animation unit if the duration is 0 and not looping."""
        if self.animation_units:
            current_animation_unit = self.animation_units[0]
            # check if current animation unit has been played for the specified duration
            if current_animation_unit.frames_played < current_animation_unit.duration:
                current_animation_unit.frames_played += 1
            else:
                # if it has been played for the duration but is looping, reset duration and add to end of list
                if current_animation_unit.looping:
                    current_animation_unit.frames_played = 0
                    self.animation_units.append(current_animation_unit)
                self.animation_units.pop(0)

        if self.animation_units:
            # get the current animation unit again, will be different if the previous unit was popped
            current_animation_unit = self.animation_units[0]
            self.symbol = current_animation_unit.symbol
            self.graphical_effect = current_animation_unit.graphicaleffect
        else:
            # if there are no more animation units, use the alternate symbol
            if self.use_alternate_symbol:
                self.symbol = self.alternate_symbol
            else:
                # if there are no more animation units and no alternate symbol, use the final symbol
                self.symbol = self.input_symbol
            # set the final graphical effect to be applied to the symbol
            self.graphical_effect = self.final_graphical_effect

    def animation_completed(self) -> bool:
        """Returns True if the character has reached its final position and has no remaining animation units."""
        only_looping = True
        for animation_unit in self.animation_units:
            if not animation_unit.looping:
                only_looping = False
                break
        return self.previous_coord == self.input_coord and (not self.animation_units or only_looping)
