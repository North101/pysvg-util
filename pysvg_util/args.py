import pathlib

import typed_argparse as tap
from pysvg import PresentationAttributes


class SVGArgs(tap.TypedArgs):
  output: pathlib.Path = tap.arg(
      default=pathlib.Path('output'),
      help='output path',
  )

  cut = PresentationAttributes(
      fill='none',
      stroke='black',
      stroke_width=0.001,
  )

  engrave = PresentationAttributes(
      fill='black',
      stroke='none',
      stroke_width=0.001,
  )
