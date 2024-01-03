import math

BARRIER_INTRUSION = 336
BARRIER_INTRUSION_WIDTH = 41
GRID_INTRUSION = 138
GRID_INTRUSION_WIDTH = 550
OUTER_GUARD_RAIL_INTRUSION = 16  # TODO: THIS IS A GUESS
DOUBLE_SUBSTATION_INTRUSION = 33
DOUBLE_SUBSTATION_INTRUSION_WIDTH = 244
FIELD_MAJOR_AXIS = 1654
NINETY_DEG = 1.587  # IN RADIANS
ANGLE_IRON_HEIGHT = 20
CHARGE_OFFSET = 247
CHARGE_WIDTH = 244
CHARGE_LENGTH = 193
CHARGE_HEIGHT = 23
CHARGE_RAMP = 39

PRIMARY_INTENSITY = 0.7
SECONDARY_INTENSITY = 0.5
TERTIARY_INTENSITY = 0.3

BOTTOM_COMMUNITY_TAG_LOCATION = 102.743
TOP_COMMUNITY_TAG_LOCATION = 1551.3558
BOTTOM_LOADER_TAG_LOCATION = 36.195
TOP_LOADER_TAG_LOCATION = 1617.8784
TAG_ONE_AND_EIGHT = 107.1626
TAG_TWO_AND_SEVEN = 274.8026
TAG_THREE_AND_SIX = 442.4426
TAG_FOUR_AND_FIVE = 674.9796

OUTER_GRID_WIDTH = 191
INNER_GRID_WIDTH = 168
MIDDLE_GRID_ROW_HEIGHT = 56
APRIL_TAG_WIDTH = 20
APRIL_TAG_HEIGHT = 20
SINGLE_APRIL_TAG_HEIGHT = 46


class Square:
    def __init__(self, top, bottom, left, right, up, down, red, green, blue, image=None):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.red = red
        self.green = green
        self.blue = blue
        self.image = image
        self.textureId = 0

    @property
    def x(self):
        return (self.right + self.left) / 2

    @property
    def y(self):
        return (self.top + self.bottom) / 2

    def z(self):
        return (self.up + self.down) / 2

    @property
    def coords(self):
        return (self.x, self.y)

    def __neg__(self):
        return Square(
            (FIELD_MAJOR_AXIS - self.bottom),
            (FIELD_MAJOR_AXIS - self.top),
            self.left,
            self.right,
            self.up,
            self.down,
            self.red,
            self.green,
            self.blue
        )

    def __sub__(self, other):
        return Square(
            abs(other.bottom - self.top),
            abs(other.bottom - self.bottom),
            self.left,
            self.right,
            self.up,
            self.down,
            self.red,
            self.green,
            self.blue
        )


SQUARE1 = Square(
    OUTER_GUARD_RAIL_INTRUSION + GRID_INTRUSION_WIDTH,
    OUTER_GUARD_RAIL_INTRUSION,
    GRID_INTRUSION,
    FIELD_MAJOR_AXIS - GRID_INTRUSION,
    0,
    0,
    0.0,
    0.0,
    PRIMARY_INTENSITY)
SQUARE2 = Square(
    SQUARE1.top + BARRIER_INTRUSION_WIDTH,
    SQUARE1.top,
    BARRIER_INTRUSION,
    FIELD_MAJOR_AXIS - BARRIER_INTRUSION,
    0,
    0,
    0.0,
    0.0,
    PRIMARY_INTENSITY)
SQUARE3 = Square(
    SQUARE2.top + DOUBLE_SUBSTATION_INTRUSION_WIDTH,
    SQUARE2.top,
    DOUBLE_SUBSTATION_INTRUSION,
    FIELD_MAJOR_AXIS - DOUBLE_SUBSTATION_INTRUSION,
    0,
    0,
    0.0,
    0.0,
    PRIMARY_INTENSITY)
FLOOR = [SQUARE1, SQUARE2, SQUARE3]

WALLS = [
    Square(
        SQUARE1.bottom,
        SQUARE1.bottom,
        SQUARE1.left,
        SQUARE1.right,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        0.0,
        0.0
    ),
    Square(
        SQUARE3.top,
        SQUARE3.bottom,
        SQUARE3.right,
        SQUARE3.right,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        SECONDARY_INTENSITY,
        0.0
    ),
    Square(
        SQUARE3.top,
        SQUARE3.bottom,
        SQUARE3.left,
        SQUARE3.left,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        SECONDARY_INTENSITY,
        0.0
    ),
    Square(
        SQUARE3.top,
        SQUARE3.top,
        SQUARE3.right,
        SQUARE3.left,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        0.0,
        0.0
    ),
    Square(
        SQUARE3.bottom,
        SQUARE3.bottom,
        SQUARE3.left,
        SQUARE1.left,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        0.0,
        0.0
    ),
    Square(
        SQUARE3.bottom,
        SQUARE3.bottom,
        SQUARE3.right,
        SQUARE1.right,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        0.0,
        0.0
    ),
    Square(
        (SQUARE1.top + SQUARE3.bottom)/2,
        (SQUARE1.top + SQUARE3.bottom)/2,
        SQUARE1.left,
        SQUARE2.left,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        0.0,
        0.0
    ),
    Square(
        (SQUARE1.top + SQUARE3.bottom) / 2,
        (SQUARE1.top + SQUARE3.bottom) / 2,
        SQUARE1.right,
        SQUARE2.right,
        ANGLE_IRON_HEIGHT,
        0,
        PRIMARY_INTENSITY,
        0.0,
        0.0
    ),
]


def generate_charge(offset):
    return [
        Square(
            SQUARE1.bottom + CHARGE_OFFSET + CHARGE_WIDTH / 2,
            SQUARE1.bottom + CHARGE_OFFSET - CHARGE_WIDTH / 2,
            offset + CHARGE_LENGTH / 2,
            offset - CHARGE_LENGTH / 2,
            CHARGE_HEIGHT,
            CHARGE_HEIGHT,
            0.0,
            PRIMARY_INTENSITY,
            0.0
        ),
        # Square(
        #     SQUARE1.left + CHARGE_OFFSET - CHARGE_WIDTH / 2,
        #     SQUARE1.left + CHARGE_OFFSET + CHARGE_WIDTH / 2,
        #     offset + CHARGE_LENGTH / 2 + CHARGE_RAMP,
        #     offset + CHARGE_LENGTH / 2,
        #     CHARGE_HEIGHT,
        #     0,
        #     0.0,
        #     PRIMARY_INTENSITY,
        #     SECONDARY_INTENSITY
        # ),
        # Square(
        #     SQUARE1.left + CHARGE_OFFSET - CHARGE_WIDTH / 2,
        #     SQUARE1.left + CHARGE_OFFSET + CHARGE_WIDTH / 2,
        #     offset - CHARGE_LENGTH / 2 - CHARGE_RAMP,
        #     offset - CHARGE_LENGTH / 2,
        #     CHARGE_HEIGHT,
        #     0,
        #     0.0,
        #     PRIMARY_INTENSITY,
        #     SECONDARY_INTENSITY
        # ),
        # Square(
        #     SQUARE1.left + CHARGE_OFFSET - CHARGE_WIDTH / 2,
        #     SQUARE1.left + CHARGE_OFFSET + CHARGE_WIDTH / 2,
        #     offset + CHARGE_LENGTH / 2,
        #     offset + CHARGE_LENGTH / 2,
        #     CHARGE_HEIGHT,
        #     0,
        #     SECONDARY_INTENSITY,
        #     PRIMARY_INTENSITY,
        #     SECONDARY_INTENSITY
        # ),
        # Square(
        #     SQUARE1.left + CHARGE_OFFSET - CHARGE_WIDTH / 2,
        #     SQUARE1.left + CHARGE_OFFSET + CHARGE_WIDTH / 2,
        #     offset - CHARGE_LENGTH / 2,
        #     offset - CHARGE_LENGTH / 2,
        #     CHARGE_HEIGHT,
        #     0,
        #     SECONDARY_INTENSITY,
        #     PRIMARY_INTENSITY,
        #     SECONDARY_INTENSITY
        # ),
        # Square(
        #     SQUARE1.left + CHARGE_OFFSET - CHARGE_WIDTH / 2,
        #     SQUARE1.left + CHARGE_OFFSET - CHARGE_WIDTH / 2,
        #     offset + CHARGE_LENGTH / 2,
        #     offset - CHARGE_LENGTH / 2,
        #     CHARGE_HEIGHT,
        #     0,
        #     SECONDARY_INTENSITY,
        #     PRIMARY_INTENSITY,
        #     0.0
        # ),
        # Square(
        #     SQUARE1.left + CHARGE_OFFSET + CHARGE_WIDTH / 2,
        #     SQUARE1.left + CHARGE_OFFSET + CHARGE_WIDTH / 2,
        #     offset + CHARGE_LENGTH / 2,
        #     offset - CHARGE_LENGTH / 2,
        #     CHARGE_HEIGHT,
        #     0,
        #     SECONDARY_INTENSITY,
        #     PRIMARY_INTENSITY,
        #     0.0
        # ),

    ]


CHARGE_1 = generate_charge(SQUARE1.right - CHARGE_OFFSET)
CHARGE_2 = generate_charge(SQUARE1.left + CHARGE_OFFSET)

QRS = [
    Square(
        TAG_ONE_AND_EIGHT + APRIL_TAG_WIDTH / 2,
        TAG_ONE_AND_EIGHT - APRIL_TAG_WIDTH / 2,
        TOP_COMMUNITY_TAG_LOCATION,
        TOP_COMMUNITY_TAG_LOCATION,
        MIDDLE_GRID_ROW_HEIGHT - APRIL_TAG_HEIGHT,
        MIDDLE_GRID_ROW_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00001.png"
    ),
    Square(
        TAG_TWO_AND_SEVEN + APRIL_TAG_WIDTH / 2,
        TAG_TWO_AND_SEVEN - APRIL_TAG_WIDTH / 2,
        TOP_COMMUNITY_TAG_LOCATION,
        TOP_COMMUNITY_TAG_LOCATION,
        MIDDLE_GRID_ROW_HEIGHT - APRIL_TAG_HEIGHT,
        MIDDLE_GRID_ROW_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00002.png"
    ),
    Square(
        TAG_THREE_AND_SIX + APRIL_TAG_WIDTH / 2,
        TAG_THREE_AND_SIX - APRIL_TAG_WIDTH / 2,
        TOP_COMMUNITY_TAG_LOCATION,
        TOP_COMMUNITY_TAG_LOCATION,
        MIDDLE_GRID_ROW_HEIGHT - APRIL_TAG_HEIGHT,
        MIDDLE_GRID_ROW_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00003.png"
    ),
    Square(
        TAG_FOUR_AND_FIVE + APRIL_TAG_WIDTH / 2,
        TAG_FOUR_AND_FIVE - APRIL_TAG_WIDTH / 2,
        TOP_LOADER_TAG_LOCATION,
        TOP_LOADER_TAG_LOCATION,
        SINGLE_APRIL_TAG_HEIGHT,
        SINGLE_APRIL_TAG_HEIGHT + APRIL_TAG_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00004.png"
    ),
    Square(
        TAG_FOUR_AND_FIVE - APRIL_TAG_WIDTH / 2,
        TAG_FOUR_AND_FIVE + APRIL_TAG_WIDTH / 2,
        BOTTOM_LOADER_TAG_LOCATION,
        BOTTOM_LOADER_TAG_LOCATION,
        SINGLE_APRIL_TAG_HEIGHT,
        SINGLE_APRIL_TAG_HEIGHT + APRIL_TAG_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00005.png"
    ),
    Square(
        TAG_THREE_AND_SIX - APRIL_TAG_WIDTH / 2,
        TAG_THREE_AND_SIX + APRIL_TAG_WIDTH / 2,
        BOTTOM_COMMUNITY_TAG_LOCATION,
        BOTTOM_COMMUNITY_TAG_LOCATION,
        MIDDLE_GRID_ROW_HEIGHT - APRIL_TAG_HEIGHT,
        MIDDLE_GRID_ROW_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00006.png"
    ),
    Square(
        TAG_TWO_AND_SEVEN - APRIL_TAG_WIDTH / 2,
        TAG_TWO_AND_SEVEN + APRIL_TAG_WIDTH / 2,
        BOTTOM_COMMUNITY_TAG_LOCATION,
        BOTTOM_COMMUNITY_TAG_LOCATION,
        MIDDLE_GRID_ROW_HEIGHT - APRIL_TAG_HEIGHT,
        MIDDLE_GRID_ROW_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00007.png"
    ),
    Square(
        TAG_ONE_AND_EIGHT - APRIL_TAG_WIDTH / 2,
        TAG_ONE_AND_EIGHT + APRIL_TAG_WIDTH / 2,
        BOTTOM_COMMUNITY_TAG_LOCATION,
        BOTTOM_COMMUNITY_TAG_LOCATION,
        MIDDLE_GRID_ROW_HEIGHT - APRIL_TAG_HEIGHT,
        MIDDLE_GRID_ROW_HEIGHT,
        1,
        1,
        1,
        "tag16_05_00008.png"
    ),
    Square(
        20,
        20,
        1 - APRIL_TAG_WIDTH / 2,
        1 + APRIL_TAG_WIDTH / 2,
        67 - APRIL_TAG_HEIGHT,
        67,
        1,
        1,
        1,
        "tag16_05_00000.png"
    )
]

SQUARES = []
SQUARES.extend(FLOOR)
SQUARES.extend(WALLS)
SQUARES.extend(CHARGE_1)
SQUARES.extend(CHARGE_2)
SQUARES.extend(QRS)
