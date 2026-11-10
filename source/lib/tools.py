def margin_is_valid(glyph):
    if glyph is None:
        return False
    try:
        return (
            glyph.angledLeftMargin is not None and glyph.angledRightMargin is not None
        )
    except (AttributeError, TypeError):
        return False


def width_is_valid(glyph):
    if glyph is None:
        return False
    try:
        return glyph.width is not None
    except (AttributeError, TypeError):
        return False


def swap_sidebearings(glyph):
    if not margin_is_valid(glyph):
        return

    with glyph.undo("Swap SB"):
        left = glyph.angledLeftMargin
        right = glyph.angledRightMargin
        glyph.angledLeftMargin = round(right)
        glyph.angledRightMargin = round(left)

    glyph.changed()


def center_sidebearings(glyph):
    if not margin_is_valid(glyph):
        return

    with glyph.undo("Center glyph"):
        average = (round(glyph.angledLeftMargin) + round(glyph.angledRightMargin)) // 2
        glyph.angledLeftMargin = average
        glyph.angledRightMargin = average

    glyph.changed()


def set_left_equal_right(glyph):
    if not margin_is_valid(glyph):
        return

    with glyph.undo("LSB = RSB"):
        glyph.angledLeftMargin = round(glyph.angledRightMargin)

    glyph.changed()


def set_right_equal_left(glyph):
    if not margin_is_valid(glyph):
        return

    with glyph.undo("RSB = LSB"):
        glyph.angledRightMargin = round(glyph.angledLeftMargin)

    glyph.changed()


def adjust_spacing(glyph, amount):
    """Add amount to both sidebearings, or to width if margins are unavailable."""
    if margin_is_valid(glyph):
        action = "Open sidebearings" if amount > 0 else "Close sidebearings"
        with glyph.undo(action):
            glyph.angledLeftMargin += amount
            glyph.angledRightMargin += amount
    elif width_is_valid(glyph):
        action = "Open glyph width" if amount > 0 else "Close glyph width"
        with glyph.undo(action):
            glyph.width += amount
    else:
        return

    glyph.changed()


def move_left_content(glyph, delta, glyph_names, planned_deltas):
    """
    Move contours, anchors and guidelines by delta.

    Components whose base glyph is also being changed are compensated for
    the transformed movement of that base glyph.
    """
    if not delta:
        moving_base = any(
            component.baseGlyph in glyph_names
            and planned_deltas.get(component.baseGlyph, 0)
            for component in glyph.components
        )
        if not moving_base:
            return

    for item in list(glyph.contours) + list(glyph.anchors) + list(glyph.guidelines):
        item.moveBy((delta, 0))

    for component in glyph.components:
        base_name = component.baseGlyph

        if base_name in glyph_names:
            base_delta = planned_deltas.get(base_name, 0)
            a, b, c, d, tx, ty = component.transformation
            x = delta - a * base_delta
            y = -b * base_delta
        else:
            x = delta
            y = 0

        if x or y:
            component.moveBy((x, y))


def plan_spacing(
    glyph,
    left_value,
    right_value,
    width_value,
    distribution=None,
):
    """Return (left-move delta, new width) without changing the glyph."""
    left = glyph.angledLeftMargin
    right = glyph.angledRightMargin

    if left is None or right is None:
        return None

    # Width only.
    if width_value is not None and left_value is None and right_value is None:
        content_width = glyph.width - left - right
        new_total_space = width_value - content_width

        if distribution == "centered":
            desired_left = new_total_space / 2

        elif distribution == "proportionate":
            current_total_space = left + right

            if current_total_space:
                desired_left = left * new_total_space / current_total_space
            else:
                desired_left = new_total_space / 2

        else:
            raise ValueError("Width-only spacing requires a distribution.")

        return desired_left - left, width_value

    delta = left_value - left if left_value is not None else 0

    if width_value is not None:
        new_width = width_value
    elif right_value is not None:
        new_width = glyph.width + delta + right_value - right
    else:
        new_width = None

    return delta, new_width


def apply_spacing(
    font,
    glyph_names,
    left_value=None,
    right_value=None,
    width_value=None,
    distribution=None,
    undo_name="Sidebear",
):
    glyph_names = [name for name in glyph_names if name in font]
    glyph_name_set = set(glyph_names)

    plans = {}
    skipped = []

    for glyph_name in glyph_names:
        plan = plan_spacing(
            glyph=font[glyph_name],
            left_value=left_value,
            right_value=right_value,
            width_value=width_value,
            distribution=distribution,
        )

        if plan is None:
            skipped.append(glyph_name)
        else:
            plans[glyph_name] = plan

    planned_deltas = {name: delta for name, (delta, _) in plans.items()}

    for glyph_name, (delta, new_width) in plans.items():
        glyph = font[glyph_name]

        with glyph.undo(undo_name):
            with glyph.holdChanges():
                move_left_content(
                    glyph,
                    delta,
                    glyph_name_set,
                    planned_deltas,
                )

                if new_width is not None:
                    glyph.width = new_width

    font.changed()
    return skipped
