# menuTitle: Sidebear 3.0


from AppKit import NSColor, NSTextAlignmentCenter
import ezui
from mojo.UI import CurrentWindow, CurrentGlyphWindow, CurrentFontWindow, Message
from mojo.extensions import (
    getExtensionDefault,
    registerExtensionDefaults,
    setExtensionDefault,
)
from mojo.subscriber import Subscriber
from mojo.roboFont import CurrentFont, CurrentGlyph

# Import tools
import importlib
import tools

importlib.invalidate_caches()
importlib.reload(tools)


LIB_KEY = "com.ryanbugden.sidebear"
INCREMENT_PREF_KEY = f"{LIB_KEY}.increment"


def get_spacing_data(glyph, side):
    data = glyph.lib.get(LIB_KEY, {})
    if side in data:
        return data[side]
    if side == "left":
        return glyph.angledLeftMargin
    if side == "right":
        return glyph.angledRightMargin
    if side == "width":
        return glyph.width


def spacing_string_to_value(value):
    value = value.strip()
    if not value:
        return True, None
    try:
        return True, int(value)
    except ValueError:
        return True, value


def update_input_color(item):
    value = item.get()
    text_field = item.getNSTextField()
    if isinstance(value, str) and value:
        text_field.setTextColor_(NSColor.systemBlueColor())
    else:
        text_field.setTextColor_(NSColor.labelColor())


class SidebearController(Subscriber, ezui.WindowController):
    def build(self, mode="glyph"):
        registerExtensionDefaults({INCREMENT_PREF_KEY: 2})
        self.mode = mode
        self.glyph_span = []
        self.increment = getExtensionDefault(INCREMENT_PREF_KEY, 2)

        content = """
        * Box                                                   @modeBox
        > Selected Glyphs                                       @modeLabel

        * HorizontalStack                                       @inputHStack
        > [_ _]                                                 @leftInput
        > ({arrow.left.arrow.right})                            @swapSBButton
        > [_ _]                                                 @rightInput

        * HorizontalStack                                       @sidesHStack
        > ({arrow.uturn.backward})                              @equalsRSBButton
        > ({equal})                                             @centerGlyphButton
        > ({arrow.uturn.right})                                 @equalsLSBButton

        ---

        [_ _]                                                   @widthInput

        * HorizontalStack                                       @incrementHStack
        > ({arrow.right.and.line.vertical.and.arrow.left})      @closeSBButton
        > [_ _]                                                 @incrementInput
        > ({arrow.left.and.line.vertical.and.arrow.right})      @openSBButton

        Increment                                               @incrementLabel

        ---

        (Apply)                                                 @applyButton
        (Formulas)                                              @formulasButton
        """

        button_settings = dict(width="fill")
        input_settings = dict(
            width="fill",
            valueType="integer",
            valueIncrement=1,
            stringToValueConverter=spacing_string_to_value,
        )
        big_label_settings = dict(
            sizeStyle="small",
            width="fill",
            alignment="center",
        )
        label_settings = dict(
            sizeStyle="mini",
            width="fill",
            alignment="center",
        )
        hstack_settings = dict(
            width=270,
            distribution="fillEqually",
        )

        description_data = dict(
            leftInput=input_settings,
            rightInput=input_settings,
            widthInput=input_settings,
            incrementInput=dict(
                width="fill",
                valueType="integer",
                valueIncrement=1,
                value=self.increment,
            ),
            modeLabel=big_label_settings,
            incrementLabel=label_settings,
            inputHStack=hstack_settings,
            incrementHStack=hstack_settings,
            sidesHStack=hstack_settings,
            swapSBButton=button_settings,
            equalsRSBButton=button_settings,
            centerGlyphButton=button_settings,
            equalsLSBButton=button_settings,
            closeSBButton=button_settings,
            openSBButton=button_settings,
            applyButton=button_settings,
            formulasButton=button_settings,
        )

        self.w = ezui.EZPanel(
            content=content,
            title="Sidebear",
            descriptionData=description_data,
            defaultButton="applyButton",
            controller=self,
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)

        for item_name in self.w.getItems():
            if "Input" in item_name:
                self.w.getItem(item_name).getNSTextField().setAlignment_(
                    NSTextAlignmentCenter
                )
        self.left_input = self.w.getItem("leftInput")
        self.right_input = self.w.getItem("rightInput")
        self.width_input = self.w.getItem("widthInput")
        self.mode_box = self.w.getItem("modeBox")
        self.mode_label = self.mode_box.getItem("modeLabel")

    def started(self):
        self.w.open()
        self.update_mode_and_fields()

    def shared_spacing_value(self, font, glyph_names, side):
        values = [
            get_spacing_data(font[name], side) for name in glyph_names if name in font
        ]
        if not values:
            return ""
        return values[0] if all(value == values[0] for value in values) else ""

    def get_glyphs(self):
        font = CurrentFont()
        if not font:
            return []
        return [font[name] for name in self.glyph_span if name in font]

    # ---------------------------
    # UI
    # ---------------------------

    def update_mode_and_fields(self):
        # Update mode
        self.mode = "Current Glyph"
        self.glyph_span = []

        font = CurrentFont()
        glyph = CurrentGlyph()
        selected = font.selectedGlyphNames if font else []

        window = CurrentWindow()
        if window is CurrentGlyphWindow():
            if glyph:
                self.mode = "Current Glyph"
                self.mode_label.set(glyph.name)
                self.glyph_span = [glyph.name]
        elif window is CurrentFontWindow():
            if selected:
                self.mode = "Selected Glyphs"
                self.mode_label.set(selected[0] if len(selected) == 1 else self.mode)
                self.glyph_span = selected
        if len(selected) == 0:
            self.mode_label.set("Sidebear")

        # Update text fields
        if font and self.glyph_span:
            self.left_input.set(
                self.shared_spacing_value(font, self.glyph_span, "left")
            )
            self.right_input.set(
                self.shared_spacing_value(font, self.glyph_span, "right")
            )
            self.width_input.set(
                self.shared_spacing_value(font, self.glyph_span, "width")
            )
        for item in (self.left_input, self.right_input, self.width_input):
            update_input_color(item)

        # Enable or disable some buttons or things
        self.update_enables()

    def update_enables(self):
        values = (
            self.left_input.get(),
            self.right_input.get(),
            self.width_input.get(),
        )
        enabled = len(self.glyph_span) > 1 and any(
            value not in (None, "") for value in values
        )
        self.w.getItem("applyButton").enable(enabled)

    def leftInputCallback(self, sender):
        update_input_color(sender)
        self.update_enables()

    def rightInputCallback(self, sender):
        if sender.get() is not None and len(self.glyph_span) > 1:
            self.width_input.set(None)
        update_input_color(sender)
        self.update_enables()

    def widthInputCallback(self, sender):
        if sender.get() is not None and len(self.glyph_span) > 1:
            self.right_input.set(None)
        update_input_color(sender)
        self.update_enables()

    def swapSBButtonCallback(self, sender):
        for glyph in self.get_glyphs():
            tools.swap_sidebearings(glyph)

    def centerGlyphButtonCallback(self, sender):
        for glyph in self.get_glyphs():
            tools.center_sidebearings(glyph)

    def equalsRSBButtonCallback(self, sender):
        for glyph in self.get_glyphs():
            tools.set_left_equal_right(glyph)

    def equalsLSBButtonCallback(self, sender):
        for glyph in self.get_glyphs():
            tools.set_right_equal_left(glyph)

    def incrementInputCallback(self, sender):
        previous = self.increment
        try:
            self.increment = int(sender.get())
        except (TypeError, ValueError):
            self.increment = previous
            sender.set(previous)
        setExtensionDefault(INCREMENT_PREF_KEY, self.increment)

    def _validate_increment(self):
        if self.increment <= 0:
            Message("Sidebear’s expand/contract increment should be a positive number.")
            return False
        return True

    def closeSBButtonCallback(self, sender):
        if self._validate_increment():
            for glyph in self.get_glyphs():
                tools.adjust_spacing(glyph, -self.increment)

    def openSBButtonCallback(self, sender):
        if self._validate_increment():
            for glyph in self.get_glyphs():
                tools.adjust_spacing(glyph, self.increment)

    def applyButtonCallback(self, sender):
        font = CurrentFont()
        if not font or not self.glyph_span:
            return

        tools.apply_spacing(
            font=font,
            glyph_names=self.glyph_span,
            left_value=self.left_input.get(),
            right_value=self.right_input.get(),
            width_value=self.width_input.get(),
        )

    # ---------------------------
    # Subscriber
    # ---------------------------

    def roboFontDidSwitchCurrentGlyph(self, info):
        self.update_mode_and_fields()


SidebearController("glyph")
