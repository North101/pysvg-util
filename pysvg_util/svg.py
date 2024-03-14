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


def seperated(item: DrawSegment, seperator: DrawSegment, count: int):
  if count == 0:
    raise ValueError()
  for _ in range(count - 1):
    yield item
    yield seperator
  yield item


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


def h_tabs(out: bool, thickness: float, tab: float, gap: float, max_width: float, padding: float, kerf: float):
  max_width = max_width + (padding * 2)
  item = h_tab(out, thickness, tab, kerf)
  seperator = path.d.h(gap + tab_kerf(out, kerf * 2))
  return path.d([
      path.d.h(padding),
      path.d.h(gap + tab_kerf(out, kerf)),
      path.placeholder(lambda w, h: h_center(
          segment=lambda max_width: path.d(list(seperated(
              item=item,
              seperator=seperator,
              count=math.floor((max_width + gap) / (tab + gap)),
          ))),
          width=max_width - w,
      )),
      path.d.h(gap + tab_kerf(out, kerf)),
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


def h_slots(thickness: float, slot: float, gap: float, max_width: float, padding: float, kerf: float):
  max_width = max_width + (padding * 2)
  item = h_slot(thickness, slot, kerf)
  seperator = path.d.m(gap + (kerf * 2), 0)
  return path.d([
      path.d.m(padding, 0),
      path.d.m(gap + kerf, 0),
      path.placeholder(lambda w, h: hm_center(
          segment=lambda max_width: path.d(list(seperated(
              item=item,
              seperator=seperator,
              count=math.floor((max_width + gap) / (slot + gap)),
          ))),
          width=max_width - w,
      )),
      path.d.m(gap + kerf, 0),
      path.d.m(padding, 0),
  ])


def v_tab(out: bool, thickness: float, tab: float, kerf: float):
  thickness = -thickness if out else thickness
  return path.d([
      -path.d.h(thickness),
      path.d.v(tab - tab_kerf(out, kerf * 2)),
      path.d.h(thickness),
  ])


def v_tabs(out: bool, thickness: float, tab: float, gap: float, max_height: float, padding: float, kerf: float):
  max_height = max_height + (padding * 2)
  item = v_tab(out, thickness, tab, kerf)
  seperator = path.d.v(gap + tab_kerf(out, kerf * 2))
  return path.d([
      path.d.v(padding),
      path.d.v(gap + tab_kerf(out, kerf)),
      path.placeholder(lambda w, h: v_center(
          segment=lambda max_height: path.d(list(seperated(
              item=item,
              seperator=seperator,
              count=math.floor((max_height + gap) / (tab + gap)),
          ))),
          height=max_height - h,
      )),
      path.d.v(gap + tab_kerf(out, kerf)),
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


def v_slots(thickness: float, slot: float, gap: float, max_height: float, padding: float, kerf: float):
  max_height = max_height + (padding * 2)
  item = v_slot(thickness, slot, kerf)
  seperator = path.d.m(0, gap + (kerf * 2))
  return path.d([
      path.d.m(0, padding),
      path.d.m(0, gap + kerf),
      path.placeholder(lambda w, h: vm_center(
          segment=lambda max_height: path.d(list(seperated(
              item=item,
              seperator=seperator,
              count=math.floor((max_height + gap) / (slot + gap)),
          ))),
          height=max_height - h,
      )),
      path.d.m(0, gap + kerf),
      path.d.m(0, padding),
  ])


def h_pad(item: DrawSegment, pad: float):
  return path.d([
      path.d.h(pad),
      item,
      path.d.h(pad),
  ])


def v_pad(item: DrawSegment, pad: float):
  return path.d([
      path.d.v(pad),
      item,
      path.d.v(pad),
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
