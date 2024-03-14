import pathlib
from os import PathLike
from typing import NamedTuple


class FileExists(pathlib.Path):
  def __init__(self, *args: PathLike | str):
    super().__init__(*args)
    if not self.is_file():
      raise ValueError()


class SVGFileExists(FileExists):
  def __init__(self, *args: PathLike | str):
    super().__init__(*args)
    if self.suffix != '.svg':
      raise ValueError()


class PositiveFloat(float):
  def __new__(cls, __x: str | float):
    value = super().__new__(cls, __x)
    if value < 0.0:
      raise ValueError()

    return value


class Percentage(float):
  def __new__(cls, __x: str | float, min=0.0, max=1.0):
    value = super().__new__(cls, __x)
    if not (min <= value <= max):
      raise ValueError()

    return value


class Dimension(NamedTuple):
  length: PositiveFloat
  width: PositiveFloat
  height: PositiveFloat


class Size(NamedTuple):
  width: PositiveFloat
  height: PositiveFloat


class Image(NamedTuple):
  path: SVGFileExists
  width: PositiveFloat
  height: PositiveFloat
  scale: PositiveFloat
