import enum
import pathlib
from typing import Any, Type

from pysvg import svg

from .args import SVGArgs


def filename(file: str, suffix: str | enum.Enum | None = None):
  if suffix:
    if isinstance(suffix, enum.Enum):
      suffix = suffix.name.lower()
    file = f'{pathlib.Path(file).stem}_{suffix}'
  return pathlib.Path(pathlib.Path(file).with_suffix('.svg').name)


class SVGFile[T: SVGArgs]():
  @property
  def filename(self):
    return filename(__file__)

  def __call__(self, args: T) -> tuple[pathlib.Path, svg]:
    ...


class VariantSVGFile[T: SVGArgs, V: enum.Enum](SVGFile[T]):
  def __init__(self, variant: V):
    self.variant = variant

  def __call__(self, args: T) -> tuple[pathlib.Path, svg]:
    ...


svg_list: list[SVGFile[Any]] = []


def register_svg_variants[T: SVGArgs, V: enum.Enum](enum: Type[enum.Enum]):
  def wrapped(f: Type[VariantSVGFile[T, V]]):
    for item in enum:
      register_svg(item)(f)
    return f
  return wrapped


def register_svg[T: SVGArgs](*args, **kwargs):
  def wrapped(f: Type[SVGFile[T]]):
    svg_list.append(f(*args, **kwargs))
    return f
  return wrapped


def generate_svgs(args: SVGArgs):
  args.output.mkdir(parents=True, exist_ok=True)
  data = []
  for svg in svg_list:
    if isinstance(args, svg.__call__.__annotations__.get('args', tuple())):
      data.append((svg.filename, svg(args)[1]))

  for (filename, svg_data) in data:
    (args.output / filename).write_text(format(svg_data, '.3f'))

  return data


def write_svgs(svgs: list[tuple[pathlib.Path, svg]]):
  data = [
      (str(filename), svg.attrs.width, svg.attrs.height)
      for (filename, svg) in svgs
  ]
  name_len = max(len(name) for (name, _, _) in data)
  length_len = max(len(f'{length:.2f}') for (_, length, _) in data)
  height_len = max(len(f'{height:.2f}') for (_, _, height) in data)
  for (name, length, height) in data:
    print(f'{name:<{name_len}} @ {length:>{length_len}.3f} x {height:>{height_len}.3f}')
