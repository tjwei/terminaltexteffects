"""Characters are dispersed and form into spinning rings.

Classes:
    Rings: Characters are dispersed and form into spinning rings.
    RingsConfig: Configuration for the Rings effect.
    RingsIterator: Iterates over the effect. Does not normally need to be called directly.
"""

import random
import typing
from dataclasses import dataclass

import terminaltexteffects.utils.argvalidators as argvalidators
from terminaltexteffects.engine import motion
from terminaltexteffects.engine.base_character import EffectCharacter, EventHandler
from terminaltexteffects.engine.base_effect import BaseEffect, BaseEffectIterator
from terminaltexteffects.utils import easing, geometry
from terminaltexteffects.utils.argsdataclass import ArgField, ArgsDataClass, argclass
from terminaltexteffects.utils.geometry import Coord
from terminaltexteffects.utils.graphics import Color, Gradient


def get_effect_and_args() -> tuple[type[typing.Any], type[ArgsDataClass]]:
    return Rings, RingsConfig


@argclass(
    name="rings",
    help="Characters are dispersed and form into spinning rings.",
    description="rings | Characters are dispersed and form into spinning rings.",
    epilog="""Example: terminaltexteffects rings --ring-colors ab48ff e7b2b2 fffebd --final-gradient-stops ab48ff e7b2b2 fffebd --final-gradient-steps 12 --ring-gap 0.1 --spin-duration 200 --spin-speed 0.25-1.0 --disperse-duration 200 --spin-disperse-cycles 3""",
)
@dataclass
class RingsConfig(ArgsDataClass):
    """Configurations for the RingsEffect.

    Attributes:
        ring_colors (tuple[Color, ...]): Tuple of colors for the rings.
        final_gradient_stops (tuple[Color, ...]): Tuple of colors for the final color gradient. If only one color is provided, the characters will be displayed in that color.
        final_gradient_steps (tuple[int, ...] | int): Number of gradient steps to use. More steps will create a smoother and longer gradient animation.
        final_gradient_direction (Gradient.Direction): Direction of the final gradient.
        ring_gap (float): Distance between rings as a percent of the smallest canvas dimension. Valid values are 0 < n <= 1.
        spin_duration (int): Number of frames for each cycle of the spin phase. Valid values are n >= 0.
        spin_speed (tuple[float, float]): Range of speeds for the rotation of the rings. The speed is randomly selected from this range for each ring. Valid values are n > 0.
        disperse_duration (int): Number of frames spent in the dispersed state between spinning cycles. Valid values are n >= 0.
        spin_disperse_cycles (int): Number of times the animation will cycle between spinning rings and dispersed characters. Valid values are n > 0.
    """

    ring_colors: tuple[Color, ...] = ArgField(
        cmd_name=["--ring-colors"],
        type_parser=argvalidators.ColorArg.type_parser,
        nargs="+",
        default=(Color("ab48ff"), Color("e7b2b2"), Color("fffebd")),
        metavar=argvalidators.ColorArg.METAVAR,
        help="Space separated, unquoted, list of colors for the rings.",
    )  # type: ignore[assignment]

    "tuple[Color] : Tuple of colors for the rings."

    final_gradient_stops: tuple[Color, ...] = ArgField(
        cmd_name=["--final-gradient-stops"],
        type_parser=argvalidators.ColorArg.type_parser,
        nargs="+",
        default=(Color("ab48ff"), Color("e7b2b2"), Color("fffebd")),
        metavar=argvalidators.ColorArg.METAVAR,
        help="Space separated, unquoted, list of colors for the character gradient (applied from bottom to top). If only one color is provided, the characters will be displayed in that color.",
    )  # type: ignore[assignment]

    "tuple[Color] : Tuple of colors for the final color gradient. If only one color is provided, the characters will be displayed in that color."

    final_gradient_steps: tuple[int, ...] | int = ArgField(
        cmd_name=["--final-gradient-steps"],
        type_parser=argvalidators.PositiveInt.type_parser,
        nargs="+",
        default=12,
        metavar=argvalidators.PositiveInt.METAVAR,
        help="Space separated, unquoted, list of the number of gradient steps to use. More steps will create a smoother and longer gradient animation.",
    )  # type: ignore[assignment]

    "tuple[int, ...] | int : Number of gradient steps to use. More steps will create a smoother and longer gradient animation."

    final_gradient_direction: Gradient.Direction = ArgField(
        cmd_name="--final-gradient-direction",
        type_parser=argvalidators.GradientDirection.type_parser,
        default=Gradient.Direction.VERTICAL,
        metavar=argvalidators.GradientDirection.METAVAR,
        help="Direction of the final gradient.",
    )  # type: ignore[assignment]

    "Gradient.Direction : Direction of the final gradient."

    ring_gap: float = ArgField(
        cmd_name=["--ring-gap"],
        type_parser=argvalidators.PositiveFloat.type_parser,
        default=0.1,
        help="Distance between rings as a percent of the smallest canvas dimension.",
    )  # type: ignore[assignment]

    "float : Distance between rings as a percent of the smallest canvas dimension."
    spin_duration: int = ArgField(
        cmd_name=["--spin-duration"],
        type_parser=argvalidators.PositiveInt.type_parser,
        default=200,
        help="Number of frames for each cycle of the spin phase.",
    )  # type: ignore[assignment]

    "int : Number of frames for each cycle of the spin phase."

    spin_speed: tuple[float, float] = ArgField(
        cmd_name=["--spin-speed"],
        type_parser=argvalidators.PositiveFloatRange.type_parser,
        default=(0.25, 1.0),
        metavar=argvalidators.PositiveFloatRange.METAVAR,
        help="Range of speeds for the rotation of the rings. The speed is randomly selected from this range for each ring.",
    )  # type: ignore[assignment]

    "tuple[float, float] : Range of speeds for the rotation of the rings. The speed is randomly selected from this range for each ring."

    disperse_duration: int = ArgField(
        cmd_name=["--disperse-duration"],
        type_parser=argvalidators.PositiveInt.type_parser,
        default=200,
        help="Number of frames spent in the dispersed state between spinning cycles.",
    )  # type: ignore[assignment]

    "int : Number of frames spent in the dispersed state between spinning cycles."

    spin_disperse_cycles: int = ArgField(
        cmd_name=["--spin-disperse-cycles"],
        type_parser=argvalidators.PositiveInt.type_parser,
        default=3,
        help="Number of times the animation will cycles between spinning rings and dispersed characters.",
    )  # type: ignore[assignment]

    "int : Number of times the animation will cycles between spinning rings and dispersed characters."

    @classmethod
    def get_effect_class(cls):
        return Rings


class RingsIterator(BaseEffectIterator[RingsConfig]):
    class Ring:
        def __init__(
            self,
            config: RingsConfig,
            radius: int,
            origin: Coord,
            ring_coords: list[Coord],
            ring_gap: int,
            ring_color: Color,
            character_color_map: dict[EffectCharacter, Color],
        ):
            self.config = config
            self._built = False
            self.radius = radius
            self.origin: Coord = origin
            self.counter_clockwise_coords = ring_coords
            self.clockwise_coords = ring_coords[::-1]
            self.ring_gap = ring_gap
            self.ring_color = ring_color
            self.characters: list[EffectCharacter] = []
            self.character_last_ring_path: dict[EffectCharacter, motion.Path] = {}
            self.rotations = 0
            self.rotation_speed = random.uniform(self.config.spin_speed[0], self.config.spin_speed[1])
            self.character_color_map = character_color_map

        def add_character(self, character: EffectCharacter, clockwise: int) -> None:
            # make gradient scene
            gradient_scn = character.animation.new_scene(id="gradient")
            char_gradient = Gradient(self.character_color_map[character], self.ring_color, steps=8)
            gradient_scn.apply_gradient_to_symbols(char_gradient, character.input_symbol, 5)

            # make rotation waypoints
            ring_paths: list[motion.Path] = []
            character_starting_index = len(self.characters)
            if clockwise:
                coords = self.clockwise_coords
            else:
                coords = self.counter_clockwise_coords
            for coord in coords[character_starting_index:] + coords[:character_starting_index]:
                ring_path = character.motion.new_path(id=str(len(ring_paths)), speed=self.rotation_speed)
                ring_path.new_waypoint(coord, id=str(len(ring_path.waypoints)))
                ring_paths.append(ring_path)
            self.character_last_ring_path[character] = ring_paths[0]
            # make disperse scene
            disperse_scn = character.animation.new_scene(is_looping=False, id="disperse")
            disperse_gradient = Gradient(self.ring_color, self.character_color_map[character], steps=8)
            disperse_scn.apply_gradient_to_symbols(disperse_gradient, character.input_symbol, 16)
            character.motion.chain_paths(ring_paths, loop=True)
            self.characters.append(character)

        def make_disperse_waypoints(self, character: EffectCharacter, origin: Coord) -> motion.Path:
            disperse_coords = geometry.find_coords_in_rect(origin, self.ring_gap)
            character.motion.paths.pop("disperse", None)
            disperse_path = character.motion.new_path(speed=0.1, loop=True, id="disperse")
            for _ in range(5):
                disperse_path.new_waypoint(disperse_coords[random.randrange(0, len(disperse_coords))])
            return disperse_path

        def disperse(self) -> None:
            for character in self.characters:
                if character.motion.active_path is not None:
                    self.character_last_ring_path[character] = character.motion.active_path
                else:
                    self.character_last_ring_path[character] = character.motion.paths["0"]
                character.motion.activate_path(self.make_disperse_waypoints(character, character.motion.current_coord))
                character.animation.activate_scene(character.animation.query_scene("disperse"))

        def spin(self) -> None:
            for character in self.characters:
                condense_path = character.motion.new_path(speed=0.1)
                condense_path.new_waypoint(self.character_last_ring_path[character].waypoints[0].coord)
                character.event_handler.register_event(
                    EventHandler.Event.PATH_COMPLETE,
                    condense_path,
                    EventHandler.Action.ACTIVATE_PATH,
                    self.character_last_ring_path[character],
                )
                character.motion.activate_path(condense_path)
                character.animation.activate_scene(character.animation.query_scene("gradient"))

    def __init__(self, effect: "Rings") -> None:
        super().__init__(effect)
        self.pending_chars: list[EffectCharacter] = []
        self.ring_chars: list[EffectCharacter] = []
        self.non_ring_chars: list[EffectCharacter] = []
        self.rings: dict[int, RingsIterator.Ring] = {}
        self.ring_gap = int(
            max(round(min(self.terminal.output_area.top, self.terminal.output_area.right) * self.config.ring_gap), 1)
        )
        self.character_final_color_map: dict[EffectCharacter, Color] = {}
        self.build()

    def build(self) -> None:
        self.ring_gap = int(
            max(round(min(self.terminal.output_area.top, self.terminal.output_area.right) * self.config.ring_gap), 1)
        )
        final_gradient = Gradient(*self.config.final_gradient_stops, steps=self.config.final_gradient_steps)
        final_gradient_mapping = final_gradient.build_coordinate_color_mapping(
            self.terminal.output_area.top, self.terminal.output_area.right, self.config.final_gradient_direction
        )
        for character in self.terminal.get_characters():
            self.character_final_color_map[character] = final_gradient_mapping[character.input_coord]
            start_scn = character.animation.new_scene()
            start_scn.add_frame(character.input_symbol, 1, color=self.character_final_color_map[character])
            home_path = character.motion.new_path(speed=0.8, ease=easing.out_quad, id="home")
            home_path.new_waypoint(character.input_coord)
            character.animation.activate_scene(start_scn)
            self.terminal.set_character_visibility(character, True)
            self.pending_chars.append(character)

        random.shuffle(self.pending_chars)
        # make rings
        for radius in range(1, max(self.terminal.output_area.right, self.terminal.output_area.top), self.ring_gap):
            ring_coords = geometry.find_coords_on_circle(
                self.terminal.output_area.center, radius, 7 * radius, unique=True
            )
            # check if any part of the ring is in the canvas, if not, stop creating rings
            if (
                len([coord for coord in ring_coords if self.terminal.output_area.coord_is_in_output_area(coord)])
                / len(ring_coords)
                < 0.25
            ):
                break

            self.rings[radius] = RingsIterator.Ring(
                self.config,
                radius,
                self.terminal.output_area.center,
                ring_coords,
                self.ring_gap,
                self.config.ring_colors[len(self.rings) % len(self.config.ring_colors)],
                self.character_final_color_map,
            )
        # assign characters to rings
        ring_count = 0
        for ring in self.rings.values():
            for _ in ring.counter_clockwise_coords:
                if self.pending_chars:
                    next_character = self.pending_chars.pop(0)
                    # set rings to rotate in opposite directions
                    ring.add_character(next_character, clockwise=ring_count % 2)
                    self.ring_chars.append(next_character)
            ring_count += 1

        # make external waypoints for characters not in rings
        for character in self.terminal.get_characters():
            if character not in self.ring_chars:
                external_path = character.motion.new_path(id="external", speed=0.8, ease=easing.out_sine)
                external_path.new_waypoint(self.terminal.output_area.random_coord(outside_scope=True))

                self.non_ring_chars.append(character)
                character.event_handler.register_event(
                    EventHandler.Event.PATH_COMPLETE,
                    external_path,
                    EventHandler.Action.CALLBACK,
                    EventHandler.Callback(self.terminal.set_character_visibility, False),
                )
        self._rings_list = list(self.rings.values())
        self._phase = "start"
        self._initial_disperse_complete = False
        self._spin_time_remaining = self.config.spin_duration
        self._disperse_time_remaining = self.config.disperse_duration
        self._cycles_remaining = self.config.spin_disperse_cycles
        self._initial_phase_time_remaining = 100

    def __next__(self) -> str:
        if self._phase != "complete":
            if self._phase == "start":
                if not self._initial_phase_time_remaining:
                    self._phase = "disperse"
                else:
                    self._initial_phase_time_remaining -= 1

            elif self._phase == "disperse":
                if not self._initial_disperse_complete:
                    self._initial_disperse_complete = True
                    for ring in self._rings_list:
                        for character in ring.characters:
                            disperse_path = ring.make_disperse_waypoints(
                                character, character.motion.paths["0"].waypoints[0].coord
                            )
                            initial_path = character.motion.new_path(speed=0.3, ease=easing.out_cubic)
                            initial_path.new_waypoint(disperse_path.waypoints[0].coord)
                            character.event_handler.register_event(
                                EventHandler.Event.PATH_COMPLETE,
                                initial_path,
                                EventHandler.Action.ACTIVATE_PATH,
                                disperse_path,
                            )
                            character.animation.activate_scene(character.animation.query_scene("disperse"))
                            character.motion.activate_path(initial_path)
                            self.active_characters.append(character)

                    for character in self.non_ring_chars:
                        character.motion.activate_path(character.motion.query_path("external"))
                        self.active_characters.append(character)

                else:
                    if not self._disperse_time_remaining:
                        self._phase = "spin"
                        self._cycles_remaining -= 1
                        self._spin_time_remaining = self.config.spin_duration
                        for ring in self._rings_list:
                            ring.spin()
                    else:
                        self._disperse_time_remaining -= 1

            elif self._phase == "spin":
                if not self._spin_time_remaining:
                    if not self._cycles_remaining:
                        self._phase = "final"
                        for character in self.terminal.get_characters():
                            self.terminal.set_character_visibility(character, True)
                            character.motion.activate_path(character.motion.query_path("home"))
                            self.active_characters.append(character)
                            if "external" in character.motion.paths:
                                continue
                            character.animation.activate_scene(character.animation.query_scene("disperse"))
                    else:
                        self._disperse_time_remaining = self.config.disperse_duration
                        for ring in self._rings_list:
                            ring.disperse()
                        self._phase = "disperse"

                else:
                    self._spin_time_remaining -= 1

            elif self._phase == "final":
                if not self.active_characters:
                    self._phase = "complete"

            self.update()
            return self.frame
        else:
            raise StopIteration


class Rings(BaseEffect[RingsConfig]):
    """Characters are dispersed and form into spinning rings.

    Attributes:
        effect_config (RingsConfig): Configuration for the effect.
        terminal_config (TerminalConfig): Configuration for the terminal.
    """

    _config_cls = RingsConfig
    _iterator_cls = RingsIterator

    def __init__(self, input_data: str) -> None:
        """Initialize the effect with the provided input data.

        Args:
            input_data (str): The input data to use for the effect."""
        super().__init__(input_data)
