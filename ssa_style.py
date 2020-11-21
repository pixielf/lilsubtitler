import dataclasses
import enum
import warnings


class BorderStyle(enum.Enum):
    OUTLINE = 1         # outline + drop shadow
    OPAQUE_BOX = 3


class Alignment(enum.IntEnum):
    LEFT = 0b0001
    CENTER = 0b0010
    RIGHT = 0b0011

    BOTTOM = 0b0000
    MIDDLE = 0b1000
    TOP = 0b0100

    @classmethod
    def validate(cls, value: int):
        """ Determine if the value is a possible alignment. Returns True when valid; raises ValueError otherwise. """
        for x in (cls.LEFT, cls.CENTER, cls.RIGHT):
            for y in (cls.BOTTOM, cls.MIDDLE, cls.TOP):
                if x | y == value:
                    return True

        # no valid (x, y) combination gets to this value
        raise ValueError(f'{value} is not a valid alignment.')


@dataclasses.dataclass
class Style:
    name: str = 'Default'
    font_name: str = 'Arial'
    font_size: int = 14

    # colors are given here as 0xRRGGBB -- these are later converted to the BBGGRR that SSA expects
    primary_colour: int = 0xFFFFFF
    secondary_colour: int = 0xFFFFFF
    outline_colour: int = 0xFFFFFF
    back_colour: int = 0x000000

    # font styles given here as booleans -- these are later converted to the integer values that SSA expects
    # (-1 for True, 0 for False :: -int(val))
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False

    border_style: BorderStyle = BorderStyle.OUTLINE

    # If BorderStyle.OUTLINE, then this specifies the width of the outline around the text, in pixels.
    # It may be one of 0, 1, 2, 3, or 4.
    outline: int = 1

    # If BorderStyle.OUTLINE, then this specifies the depth of the drop shadow behind the text, in pixels.
    # It may be one of 0, 1, 2, 3, or 4. Drop shadow is always used in addition to an outline:
    # SSA will force an outline of 1 pixel if no outline width is given.
    shadow: int = 1

    alignment: int = Alignment.BOTTOM | Alignment.CENTER

    # These define the margins (left, right, vertical) in pixels.
    margin_l: int = 10  # distance from left edge of screen
    margin_r: int = 10  # distance from right edge of screen
    margin_v: int = 10  # distance from bottom edge (for bottom title) or top edge (for top title)
    # ------------------- and ignored for mid title (where text is vertically centered)

    # The transparency of the text. Currently unused in SSA.
    alpha_level: int = 0

    # Specifies the font character set or encoding and on multilingual Windows installations of SSA, it provides
    # access to characters used in more than one language. It is usually zero for English (Western, ANSI) Windows.
    encoding: int = 0

    @staticmethod
    def _validate_colour(c):
        """ Validate/parse the input color. """
        if isinstance(c, str):
            # Try to interpret as a hex color (#)RRGGBB
            try:
                original = c
                c = int(c.lstrip('#'), 16)
                warnings.warn(f'color {original!r} given, interpreted as {c}')
            except ValueError:
                raise TypeError('color {c!r} given, not interpretable as hex color')

        if not isinstance(c, int):
            # Try to interpret as an int (perhaps float?)
            try:
                original = c
                c = int(c)
                warnings.warn(f'color {original!r} given, interpreted as {c}')
            except ValueError:
                raise TypeError('color {c!r} given, not interpretable as color')

        # For integer values, check if it's in the correct range.
        if not 0 <= c <= 0xFFFFFF:
            original = c
            c = c & 0xFFFFFF
            warnings.warn(f'color {original} == #{original:06X} given, outside [0, 0xFFFFFF]. Using {c} instead.')

        return c

    def __post_init__(self):
        """ Check that all of the values are valid. """
        if not isinstance(self.name, str):
            raise TypeError(f'Style.name must be a str, not {self.name!r}')

        if not isinstance(self.font_name, str):
            raise TypeError(f'Style.font_name must be a str, not {self.name!r}')

        if not isinstance(self.font_size, int):
            try:
                s = self.font_size
                self.font_size = int(self.font_size)
                warnings.warn(f'Passed {s!r} as Style.font_size. Converted to {self.font_size!r}')
            except ValueError:
                raise TypeError(f'Style.font_size must be interpretable as int, not {self.font_size}')

        for colour in (self.primary_colour, self.secondary_colour, self.outline_colour, self.back_colour):
            self._validate_colour(colour)

        if not isinstance(self.bold, bool):
            s = self.bold
            self.bold = bool(s)
            warnings.warn(f'Passed {s!r} as Style.bold. Converted to {self.bold!r}')

        if not isinstance(self.italic, bool):
            s = self.italic
            self.italic = bool(s)
            warnings.warn(f'Passed {s!r} as Style.italic. Converted to {self.italic!r}')

        if not isinstance(self.underline, bool):
            s = self.underline
            self.underline = bool(s)
            warnings.warn(f'Passed {s!r} as Style.underline. Converted to {self.underline!r}')

        if not isinstance(self.strikethrough, bool):
            s = self.strikethrough
            self.strikethrough = bool(s)
            warnings.warn(f'Passed {s!r} as Style.strikethrough. Converted to {self.strikethrough!r}')

        # If self.border_style isn't already an BorderStyle, it is converted to one, raising ValueError
        # if the border_style value is invalid.
        self.border_style = BorderStyle(self.border_style)

        # outline and shadow must be one of 0, 1, 2, 3, 4
        if self.outline not in range(5):
            raise ValueError(f'Style.outline must be one of 0, 1, 2, 3, 4, not {self.outline!r}')

        if self.shadow not in range(5):
            raise ValueError(f'Style.shadow must be one of 0, 1, 2, 3, 4, not {self.shadow!r}')

        Alignment.validate(self.alignment)

    @classmethod
    def header(cls):
        return '[V4 Styles]\nFormat: ' + ', '.join([
            'Name', 'Fontname', 'Fontsize',
            'PrimaryColour', 'SecondaryColour',
            'OutlineColour', 'BackColour',
            'Bold', 'Italic', 'Underline', 'Strikethrough',
            'BorderStyle', 'Outline', 'Shadow', 'Alignment',
            'MarginL', 'MarginR', 'MarginV', 'AlphaLevel', 'Encoding'
        ])

    @classmethod
    def load(cls, style: str):
        """ Create a style from the SSA output, `style`.

        TODO: Implement this. Note that the colours will need to be "unparsed" back to RRGGBB. This can be done
        by passing them through the cls.reformat_colour method (as the function is its own inverse).
        """
        raise NotImplementedError()

    def __str__(self):
        return 'Style: ' + ', '.join(map(str, [
            self.name, self.font_name, self.font_size,
            self.reformat_colour(self.primary_colour), self.reformat_colour(self.secondary_colour),
            self.reformat_colour(self.outline_colour), self.reformat_colour(self.back_colour),
            -int(self.bold), -int(self.italic), -int(self.underline), -int(self.strikethrough),
            self.border_style.value, self.outline, self.shadow, self.alignment,
            self.margin_l, self.margin_r, self.margin_v, self.alpha_level, self.encoding
        ]))

    @staticmethod
    def reformat_colour(rrggbb: int) -> int:
        """ Convert a colour in the form 0xRRGGBB to SSA's required BBGGRR (base-10) """
        # strip out original components
        r = (rrggbb & 0xFF0000) >> 16
        g = (rrggbb & 0x00FF00) >> 8
        b = (rrggbb & 0x0000FF)

        # and stitch back together in the other order
        return (b << 16) + (g << 8) + r
