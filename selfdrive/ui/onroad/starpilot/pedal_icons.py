import pyray as rl
from openpilot.selfdrive.ui.ui_state import ui_state

_RADIUS = 36


def _alpha(opacity: float) -> int:
  return int(255 * max(0.0, min(1.0, opacity)))


def _draw_brake_icon(cx: float, cy: float, opacity: float):
  a = _alpha(opacity)
  white = rl.Color(255, 255, 255, a)
  groove = rl.Color(201, 34, 49, a)

  # Brake pedal stem
  rl.draw_rectangle_rounded(
    rl.Rectangle(cx - 3, cy - 21, 6, 14),
    0.6, 8, white
  )

  # Rounded brake pedal pad
  rl.draw_rectangle_rounded(
    rl.Rectangle(cx - 21, cy - 9, 42, 25),
    0.4, 8, white
  )

  # Vertical grip grooves
  for offset in [-13, -5, 3, 11]:
    rl.draw_rectangle_rounded(
      rl.Rectangle(cx + offset, cy - 4, 3, 15),
      0.6, 8, groove
    )


def _draw_gas_icon(cx: float, cy: float, opacity: float):
  a = _alpha(opacity)
  white = rl.Color(255, 255, 255, a)
  groove = rl.Color(22, 127, 64, a)

  # Rotate accelerator pedal by 10 degrees
  rl.rl_push_matrix()

  try:
    rl.rl_translatef(cx, cy, 0.0)
    rl.rl_rotatef(10.0, 0.0, 0.0, 1.0)

    # Rounded accelerator pedal pad
    rl.draw_rectangle_rounded(
      rl.Rectangle(-11, -23, 22, 46),
      0.45, 8, white
    )

    # Horizontal grip grooves
    for offset in [-15, -6, 3, 12]:
      rl.draw_rectangle_rounded(
        rl.Rectangle(-6, offset, 12, 3),
        0.6, 8, groove
      )

  finally:
    rl.rl_pop_matrix()


def render_pedal_icons(start_x: float, start_y: float, font):
  params = ui_state.ui_params
  if not params.get_bool("PedalsOnUI"):
    return

  car_state = ui_state.sm["carState"] if ui_state.sm.valid.get("carState", False) else None
  if not car_state:
    return

  standstill = getattr(car_state, "standstill", False)
  starpilot_car_state = ui_state.sm["starpilotCarState"] if ui_state.sm.valid.get("starpilotCarState", False) else None

  brake_lights = (
    getattr(car_state, "brakeLights", False) or
    getattr(car_state, "brakeLightsDEPRECATED", False) or
    getattr(car_state, "regenBraking", False) or
    getattr(starpilot_car_state, "brakeLights", False)
  )

  acceleration_ego = getattr(car_state, "aEgo", 0.0)

  dynamic_pedals = params.get_bool("DynamicPedalsOnUI")
  static_pedals = params.get_bool("StaticPedalsOnUI")

  brake_opacity = 1.0
  gas_opacity = 1.0

  if dynamic_pedals:
    brake_opacity = 1.0 if standstill else min(1.0, max(0.25, abs(acceleration_ego))) if acceleration_ego < -0.25 else 0.25
    gas_opacity = min(1.0, max(0.25, acceleration_ego)) if acceleration_ego > 0.0 else 0.25

  elif static_pedals:
    brake_opacity = 1.0 if (standstill or brake_lights or acceleration_ego < -0.25) else 0.25
    gas_opacity = 1.0 if acceleration_ego > 0.25 else 0.25

  cx = start_x + 48
  cy = start_y + 48

  # Brake circle
  rl.draw_circle(
    int(cx), int(cy), _RADIUS,
    rl.Color(201, 34, 49, _alpha(brake_opacity))
  )

  rl.draw_circle_lines(
    int(cx), int(cy), _RADIUS,
    rl.Color(255, 255, 255, _alpha(brake_opacity))
  )

  _draw_brake_icon(cx, cy, brake_opacity)

  # Accelerator circle
  gx = cx + 96

  rl.draw_circle(
    int(gx), int(cy), _RADIUS,
    rl.Color(22, 127, 64, _alpha(gas_opacity))
  )

  rl.draw_circle_lines(
    int(gx), int(cy), _RADIUS,
    rl.Color(255, 255, 255, _alpha(gas_opacity))
  )

  _draw_gas_icon(gx, cy, gas_opacity)
