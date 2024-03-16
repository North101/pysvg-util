import enum
import math
from typing import Callable

from pysvg import PresentationAttributes, g, path, transforms
from pysvg.attributes.presentation import DrawSegment

from . import types


def corner_radius_br(r: float, bite=False):
  return path.d.a(r, r, 0, False, not bite, r, r)


def corner_radius_tl(r: float, bite=False):
  return path.d.a(r, r, 0, False, not bite, r, -r)


def engrave_image(path: path.d, image: types.Image, engrave: PresentationAttributes):
  contain_scale = min(path.width / image.width, path.height / image.height)
  width = image.width * contain_scale * image.scale
  height = image.height * contain_scale * image.scale
  return g(
      attrs=g.attrs(transform=[
          transforms.translate(
              x=(path.width - width) / 2,
              y=(path.height - height) / 2,
          ),
          transforms.scale(contain_scale),
          transforms.scale(image.scale),
      ]) | engrave,
      children=[
          image.path.read_text().strip(),
      ],
  )


def seperated_by(items: list[DrawSegment], seperator: DrawSegment):
  if len(items) == 0:
    raise ValueError()

  result = [
      items[0],
  ]
  for item in items[1:]:
    result.append(seperator)
    result.append(item)
  return result


def m_center(segment: Callable[[float, float], DrawSegment], width: float = 0, height: float = 0):
  return path.d([
      path.placeholder(lambda w, h: path.d.m((width - w) / 2, (height - h) / 2)),
      segment(width, height),
      path.placeholder(lambda w, h: path.d.m((width - w) / 2, (height - h) / 2)),
  ])


def h_center(segment: Callable[[float], DrawSegment], width: float):
  return path.d([
      path.placeholder(lambda w, h: path.d.h((width - w) / 2)),
      segment(width),
      path.placeholder(lambda w, h: path.d.h((width - w) / 2)),
  ])


def hm_center(segment: Callable[[float], DrawSegment], width: float):
  return path.d([
      path.placeholder(lambda w, h: path.d.m((width - w) / 2, 0)),
      segment(width),
      path.placeholder(lambda w, h: path.d.m((width - w) / 2, 0)),
  ])


def v_center(segment: Callable[[float], DrawSegment], height: float):
  return path.d([
      path.placeholder(lambda w, h: path.d.v((height - h) / 2)),
      segment(height),
      path.placeholder(lambda w, h: path.d.v((height - h) / 2)),
  ])


def vm_center(segment: Callable[[float], DrawSegment], height: float):
  return path.d([
      path.placeholder(lambda w, h: path.d.m(0, (height - h) / 2)),
      segment(height),
      path.placeholder(lambda w, h: path.d.m(0, (height - h) / 2)),
  ])


def tab_kerf(out: bool, kerf: float):
  return -kerf if out else kerf


def h_tab(out: bool, thickness: float, tab: float, kerf: float):
  thickness = -thickness if out else thickness
  return path.d([
      path.d.v(thickness),
      path.d.h(tab - tab_kerf(out, kerf * 2)),
      -path.d.v(thickness),
  ])


def h_tabs(out: bool, thickness: float, tab: float, gap: float, max_width: float, kerf: float, padding: float = 0):
  max_width = max_width + (padding * 2)
  item = h_tab(out, thickness, tab, kerf)
  seperator = path.d.h(gap + tab_kerf(out, kerf * 2))
  return path.d([
      path.d.h(padding),
      path.d.h((gap / 2) + tab_kerf(out, kerf)),
      path.placeholder(lambda w, h: h_center(
          segment=lambda max_width: path.d(seperated_by(
              items=[item] * math.floor((max_width + gap) / (tab + gap)),
              seperator=seperator,
          )),
          width=max_width - w,
      )),
      path.d.h((gap / 2) + tab_kerf(out, kerf)),
      path.d.h(padding),
  ])


def h_slot(thickness: float, slot: float, kerf: float):
  kerf = kerf * 2
  return path.d([
      path.d.h(slot - kerf),
      path.d.v(thickness),
      -path.d.h(slot - kerf),
      -path.d.v(thickness),
      path.d.m(slot - kerf, 0),
  ])


def h_slots(thickness: float, slot: float, gap: float, max_width: float, kerf: float, padding: float = 0):
  max_width = max_width + (padding * 2)
  item = h_slot(thickness, slot, kerf)
  seperator = path.d.m(gap + (kerf * 2), 0)
  return path.d([
      path.d.m(padding, 0),
      path.d.m((gap / 2) + kerf, 0),
      path.placeholder(lambda w, h: hm_center(
          segment=lambda max_width: path.d(seperated_by(
              items=[item] * math.floor((max_width + gap) / (slot + gap)),
              seperator=seperator,
          )),
          width=max_width - w,
      )),
      path.d.m((gap / 2) + kerf, 0),
      path.d.m(padding, 0),
  ])


def h_pad(item: DrawSegment, pad: float):
  return path.d([
      path.d.h(pad),
      item,
      path.d.h(pad),
  ])


def v_tab(out: bool, thickness: float, tab: float, kerf: float):
  thickness = -thickness if out else thickness
  return path.d([
      -path.d.h(thickness),
      path.d.v(tab - tab_kerf(out, kerf * 2)),
      path.d.h(thickness),
  ])


def v_tabs(out: bool, thickness: float, tab: float, gap: float, max_height: float, kerf: float, padding: float = 0):
  max_height = max_height + (padding * 2)
  item = v_tab(out, thickness, tab, kerf)
  seperator = path.d.v(gap + tab_kerf(out, kerf * 2))
  return path.d([
      path.d.v(padding),
      path.d.v((gap / 2) + tab_kerf(out, kerf)),
      path.placeholder(lambda w, h: v_center(
          segment=lambda max_height: path.d(seperated_by(
              items=[item] * math.floor((max_height + gap) / (tab + gap)),
              seperator=seperator,
          )),
          height=max_height - h,
      )),
      path.d.v((gap / 2) + tab_kerf(out, kerf)),
      path.d.v(padding),
  ])


def v_slot(thickness: float, slot: float, kerf: float):
  kerf = kerf * 2
  return path.d([
      path.d.v(slot - kerf),
      path.d.h(thickness),
      -path.d.v(slot - kerf),
      -path.d.h(thickness),
      path.d.m(0, slot - kerf),
  ])


def v_slots(thickness: float, slot: float, gap: float, max_height: float, kerf: float, padding: float = 0):
  max_height = max_height + (padding * 2)
  item = v_slot(thickness, slot, kerf)
  seperator = path.d.m(0, gap + (kerf * 2))
  return path.d([
      path.d.m(0, padding),
      path.d.m(0, (gap / 2) + kerf),
      path.placeholder(lambda w, h: vm_center(
          segment=lambda max_height: path.d(seperated_by(
              items=[item] * math.floor((max_height + gap) / (slot + gap)),
              seperator=seperator,
          )),
          height=max_height - h,
      )),
      path.d.m(0, (gap / 2) + kerf),
      path.d.m(0, padding),
  ])


def v_pad(item: DrawSegment, pad: float):
  return path.d([
      path.d.v(pad),
      item,
      path.d.v(pad),
  ])


def box(horizontal: DrawSegment, vertical: DrawSegment):
  return path.d([
      horizontal,
      vertical,
      -horizontal,
      -vertical,
  ])


class Align(enum.Flag):
  TOP = enum.auto()
  LEFT = enum.auto()
  BOTTOM = enum.auto()
  RIGHT = enum.auto()
  CENTER_V = TOP & BOTTOM
  CENTER_H = LEFT & RIGHT
  CENTER = CENTER_V & CENTER_H


def m_align(item: DrawSegment, align: Align, width: float, height: float):
  if isinstance(item, path.d):
    item_width = item.width
    item_height = item.height
  else:
    item_width = item.rel_x
    item_height = item.rel_y

  if Align.CENTER_H in align:
    x = (item_width - width) / 2
  if Align.RIGHT in align:
    x = item_width - width
  else:
    x = 0

  if Align.CENTER_V in align:
    y = (item_height - height) / 2
  if Align.BOTTOM in align:
    y = item_height - height
  else:
    y = 0

  return path.d([
      path.d.m(x, y),
      item,
  ])


class Tab():
  tab: float
  thickness: float
  kerf: float

  def __init__(self, tab: float, thickness: float, kerf: float):
    self.tab = tab
    self.thickness = thickness
    self.kerf = kerf

  def h_tab(self, out: bool):
    return h_tab(
        out=out,
        thickness=self.thickness,
        tab=self.tab,
        kerf=self.kerf,
    )

  def h_tabs(self, out: bool, width: float, pad: bool, gap: float | None = None):
    return h_tabs(
        out=out,
        thickness=self.thickness,
        tab=self.tab,
        gap=gap if gap is not None else self.tab,
        max_width=width,
        padding=self.thickness if pad else 0,
        kerf=self.kerf,
    )

  def h_slot(self):
    return h_slot(
        thickness=self.thickness,
        slot=self.tab,
        kerf=self.kerf,
    )

  def h_slots(self, width: float, gap: float | None = None, padding: float = 0):
    return h_slots(
        thickness=self.thickness,
        slot=self.tab,
        gap=gap if gap is not None else self.tab,
        max_width=width,
        padding=padding,
        kerf=self.kerf,
    )

  def v_tab(self, out: bool):
    return v_tab(
        out=out,
        thickness=self.thickness,
        tab=self.tab,
        kerf=self.kerf,
    )

  def v_tabs(self, out: bool, height: float, pad: bool, gap: float | None = None):
    return v_tabs(
        out=out,
        thickness=self.thickness,
        tab=self.tab,
        gap=gap if gap is not None else self.tab,
        max_height=height,
        padding=self.thickness if pad else 0,
        kerf=self.kerf,
    )

  def v_slot(self):
    return v_slot(
        thickness=self.thickness,
        slot=self.tab,
        kerf=self.kerf,
    )

  def v_slots(self, height: float, gap: float | None = None, padding: float = 0):
    return v_slots(
        thickness=self.thickness,
        slot=self.tab,
        gap=gap if gap is not None else self.tab,
        max_height=height,
        padding=padding,
        kerf=self.kerf,
    )
