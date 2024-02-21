# menuTitle : Sidebear

'''
Installs an Inspector panel that enables one to 
quickly manipulating the current glyph’s sidebearings.

Ryan Bugden
v1.1.6: 2023.05.31
v1.1.5: 2022.03.01
v1.1.1: 2020.03.16
v1.1.0: 2020.03.03
v1.0.5: 2020.01.24
v1.0.4: 2019.05.07
v1.0.3: 2019.04.09
v1:     2019.03.28

Special thanks to:
Just van Rossum, Gustavo Ferreira, Frederik Berlaen, Colin Ford
'''

import os
import vanilla
import mojo.UI
from mojo.events import addObserver
from mojo.UI import inDarkMode
from mojo.extensions import setExtensionDefault, getExtensionDefault, registerExtensionDefaults

OTHER_SB = ','
MATH_SYMBOLS = ["+", "-", "*", "/"]

class Sidebear(object):

    def __init__(self, resources_path):
        
        self.pref_key = 'com.ryanbugden.sidebear.increment'

        self.resources_path = resources_path
        
        initialDefaults = {
            self.pref_key:   2,
            }
        registerExtensionDefaults(initialDefaults)

        try:
            self.g = CurrentGlyph()
        except:
            self.g = None
    
        window_width = 255
        window_margin = 20
        gutter = 25
        vert_gutter = 10
        rule_gutter = vert_gutter - 2
        text_box_height = 22
        image_button_height = text_box_height + 2
        row_1_y = -14
        row_2_y = row_1_y + vert_gutter + text_box_height - 5
        row_3_y = row_2_y + vert_gutter + text_box_height
        row_4_y = row_3_y + text_box_height + rule_gutter
        row_5_y = row_4_y + rule_gutter
        third_width = (window_width - (window_margin * 2) - (gutter * 2)) / 3
        self.window_height = window_margin*2 + row_5_y + text_box_height + 8
            
        # The group of elements
        self.w = vanilla.Group((0, 0, -0, -0))
    
        # Current glyph
        self.w.curr_glyph_note = vanilla.TextBox(
            (window_margin + third_width/2, window_margin + row_1_y, third_width*2 + gutter*2, text_box_height), 
            "None",
            sizeStyle = "regular", 
            alignment = "center")

        # Left width span rule
        self.w.left_w_span = vanilla.HorizontalLine((window_margin + 2, window_margin + row_1_y + (text_box_height/2), third_width, 1))
        
        # Left width vert rule
        self.w.left_w_vert = vanilla.VerticalLine((window_margin + 1, window_margin + row_1_y, 1, text_box_height))
        
        # Right width span rule
        self.w.right_w_span = vanilla.HorizontalLine((window_margin + third_width*2 + gutter*2, window_margin + row_1_y + (text_box_height/2), third_width - 1, 1))
        
        # Right width vert rule
        self.w.right_w_vert = vanilla.VerticalLine((window_margin + third_width*3 + gutter*2 - 1, window_margin + row_1_y, 1, text_box_height))
        
        # Left side-bearing
        self.w.LSB = vanilla.EditText(
            (window_margin, window_margin + row_2_y, third_width, text_box_height), 
            text = "", 
            sizeStyle = "small", 
            callback = self.editLSBCallback,
            continuous = False
            )
        self.w.LSB.getNSTextField().setFocusRingType_(1)
        self.w.LSB.getNSTextField().setAlignment_(2)
            
        # Left swap bridge rule
        self.w.left_sw_rule = vanilla.HorizontalLine((window_margin + third_width, window_margin + row_2_y + text_box_height/2, gutter, 1))
            
        # Swap SB button
        self.w.swap_SB = vanilla.ImageButton(
            (window_margin + third_width + gutter, window_margin + row_2_y, third_width, image_button_height), 
            callback = self.swapSBButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Right swap bridge rule
        self.w.right_sw_rule = vanilla.HorizontalLine((window_margin + third_width*2 + gutter, window_margin + row_2_y + text_box_height/2, gutter, 1))
        
        # Right side-bearing
        self.w.RSB = vanilla.EditText(
            (window_margin + third_width*2 + gutter*2, window_margin + row_2_y, third_width, text_box_height), 
            text = "", 
            sizeStyle = "small", 
            callback = self.editRSBCallback,
            continuous = False
            )
        self.w.RSB.getNSTextField().setFocusRingType_(1)
        self.w.RSB.getNSTextField().setAlignment_(2)
    
        # Center Glyph button
        self.w.center_glyph = vanilla.ImageButton(
            (window_margin + third_width + gutter, window_margin + row_3_y, third_width, image_button_height), 
            callback = self.centerGlyphButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Left vert bridge rule
        self.w.left_vert_rule = vanilla.VerticalLine((window_margin + third_width/2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
        
        # Right vert bridge rule
        self.w.right_vert_rule = vanilla.VerticalLine((window_margin + third_width*2.5 + gutter*2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
            
        # Equals RSB button
        self.w.equals_RSB = vanilla.ImageButton(
            (window_margin, window_margin + row_3_y, third_width, image_button_height), 
            callback = self.equalsRSBButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Equals LSB button
        self.w.equals_LSB = vanilla.ImageButton(
            (window_margin + third_width*2 + gutter*2, window_margin + row_3_y, third_width, image_button_height), 
            callback = self.equalsLSBButtonCallback, 
            sizeStyle = 'regular'
            )
        
        # Rule
        self.w.rule = vanilla.HorizontalLine((window_margin, window_margin + row_4_y, third_width*3 + gutter*2, 1))
    
        # Increment input
        self.increment = getExtensionDefault(self.pref_key, 2)
        self.w.inc_text_box = vanilla.EditText(
            (window_margin + gutter + third_width, window_margin + row_5_y, third_width, text_box_height), 
            text = "%s" % self.increment, 
            sizeStyle = "small", 
            callback = self.incrementCallback
            )
        self.w.inc_text_box.getNSTextField().setFocusRingType_(1)
        self.w.inc_text_box.getNSTextField().setAlignment_(2)
            
        # Left expand/contract bridge rule
        self.w.left_ec_rule = vanilla.HorizontalLine((window_margin + third_width, window_margin + row_5_y + text_box_height/2, gutter, 1))
            
        # Right expand/contract bridge rule
        self.w.right_ec_rule = vanilla.HorizontalLine((window_margin + third_width*2 + gutter, window_margin + row_5_y + text_box_height/2, gutter, 1))
        
        # Close SBs
        self.w.close_SB = vanilla.ImageButton(
            (window_margin, window_margin + row_5_y, third_width, image_button_height), 
            callback = self.closeSBButtonCallback, 
            sizeStyle = 'regular'
            )
        
        # Open SBs
        self.w.open_SB = vanilla.ImageButton(
            (window_margin + third_width*2 + gutter*2, window_margin + row_5_y, third_width, image_button_height), 
            callback = self.openSBButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Increment
        self.w.incr_caption = vanilla.TextBox(
            (window_margin + third_width, window_margin + row_5_y + 23, third_width + gutter*2, text_box_height), 
            "Increment",
            sizeStyle = "mini", 
            alignment = "center")

        for button in [self.w.open_SB, self.w.close_SB, self.w.equals_LSB, self.w.equals_RSB, self.w.center_glyph, self.w.swap_SB]:
            ns_button = button.getNSButton()
            ns_button.setBezelStyle_(8)
        self.set_button_images()
            
        addObserver(self, "glyphChanged", "currentGlyphChanged")
        addObserver(self, "glyphChanged", "viewDidChangeGlyph")
        addObserver(self, "glyphChanged", "glyphWindowDidOpen")
        addObserver(self, "glyphDraw", "draw")
        addObserver(self, "appearanceChanged", "appearanceChanged")

        self.updateUI_BothSB()


# =========================== CUSTOM FUNCTIONS =========================== #


    def LSB_math_value(self, value):
        LSBs = {}
        for g in self.f:
            LSBs.update({g.name: g.angledLeftMargin})
        try:
            result = eval(value, LSBs)
        except:
            result = None
        return result

    def RSB_math_value(self, value):
        RSBs = {}
        for g in self.f:
            RSBs.update({g.name: g.angledRightMargin})
        try:
            result = eval(value, RSBs)
        except:
            result = None
        return result

    def set_button_images(self):
        buttons_and_images = {
                self.w.swap_SB:      self.resources_path + '/_icon_Swap.pdf',
                self.w.center_glyph: self.resources_path + '/_icon_Center.pdf',
                self.w.equals_RSB:   self.resources_path + '/_icon_EqualRSB.pdf',
                self.w.equals_LSB:   self.resources_path + '/_icon_EqualLSB.pdf',
                self.w.close_SB:     self.resources_path + '/_icon_Close.pdf',
                self.w.open_SB:      self.resources_path + '/_icon_Open.pdf',
            }   
        for button, image_path in buttons_and_images.items():
            if inDarkMode():
                button.setImage(image_path.replace(".pdf", "-dark.pdf"))
            else:
                button.setImage(image_path)

    
# =========================== CALLBACKS =========================== #

    
    def editLSBCallback(self, sender):
        if self.g != None:
            try:
                des_lsb = round(int(sender.get()))
                with self.g.undo("Edit LSB"):
                    self.g.angledLeftMargin = des_lsb
            except ValueError:
                try:
                    value = str(sender.get())
                    self.f = CurrentFont()
                    math_within = set(value).intersection(set(MATH_SYMBOLS))
                    if math_within:
                        if self.LSB_math_value(value) != None:
                            self.g.angledLeftMargin = self.LSB_math_value(value)
                    elif OTHER_SB in value:
                        value = value.replace(OTHER_SB,"")
                        if value in self.f.keys() and self.f[value] != None:
                            self.g.angledLeftMargin = self.f[value].angledRightMargin
                    else:
                        if value in self.f.keys() and self.f[value] != None:
                            self.g.angledLeftMargin = self.f[value].angledLeftMargin
                except ValueError:
                    pass
            self.updateUI_BothSB()
            self.g.changed()
        
    def editRSBCallback(self, sender):
        if self.g != None:
            try:
                des_rsb = round(int(sender.get()))
                with self.g.undo("Edit RSB"):
                    self.g.angledRightMargin = des_rsb
            except ValueError:
                try:
                    value = str(sender.get())
                    self.f = CurrentFont()
                    math_within = set(value).intersection(set(MATH_SYMBOLS))
                    if math_within:
                        if self.RSB_math_value(value) != None:
                            self.g.angledRightMargin = self.RSB_math_value(value)
                    elif OTHER_SB in value:
                        value = value.replace(OTHER_SB,"")
                        if value in self.f.keys() and self.f[value] != None:
                            self.g.angledRightMargin = self.f[value].angledLeftMargin
                    else:
                        if value in self.f.keys() and self.f[value] != None:
                            self.g.angledRightMargin = self.f[value].angledRightMargin
                except ValueError:
                    pass
            self.updateUI_BothSB()
            self.g.changed()
        
    def swapSBButtonCallback(self, sender):
        if self.g != None:
            if self.marginValidator(self.g) == True:
                with self.g.undo("Swap SB"):
                    prev_LSB = self.g.angledLeftMargin
                    prev_RSB = self.g.angledRightMargin
                    self.g.angledLeftMargin = round(prev_RSB)
                    self.g.angledRightMargin = round(prev_LSB)
                    # print("Swapped sidebearings")
            self.updateUI_BothSB()
            self.g.changed()
        
    def centerGlyphButtonCallback(self, sender):
        # Warning: This may change the set width by 1, in favor of symmetrical SBs
        if self.g != None:
            if self.marginValidator(self.g) == True:
                with self.g.undo("Center glyph"):
                    margins_average = (round(self.g.angledRightMargin) + round(self.g.angledLeftMargin)) // 2
                    self.g.angledLeftMargin = margins_average
                    self.g.angledRightMargin = margins_average
            self.updateUI_BothSB()
            self.g.changed()
                
    def equalsRSBButtonCallback(self, sender):
        # print("Starting Equals RSB")
        if self.g != None:
            # print("There's a glyph.")
            if self.marginValidator(self.g) == True:
                # print("There's a margin.")
                with self.g.undo("LSB = RSB"):
                    self.g.angledLeftMargin = round(self.g.angledRightMargin)
                    # print("Done equals RSB")
            self.updateUI_BothSB()
            self.g.changed()
    
    def equalsLSBButtonCallback(self, sender):
        # print("Starting Equals LSB")
        if self.g != None:
            # print("There's a glyph.")
            if self.marginValidator(self.g) == True:
                # print("There's a margin.")
                with self.g.undo("RSB = LSB"):
                    self.g.angledRightMargin = round(self.g.angledLeftMargin)
                    # print("Done equals LSB")
            self.updateUI_BothSB()
            self.g.changed()
        
    def closeSBButtonCallback(self, sender):
        # print("\nStarting Close SBs")
        if self.g != None:
            # print("There's a glyph.")
            if self.increment <= 0:
                mojo.UI.Message("Sidebear’s expand/contract increment should be a positive number.")
            elif self.marginValidator(self.g) == True:
                # print("There's a margin.")
                with self.g.undo("Close sidebearings"):
                    self.g.angledLeftMargin -= self.increment
                    self.g.angledRightMargin -= self.increment
                    # print("Done Close SBs")
            elif self.widthValidator(self.g) == True:
                # print("There's a width.")
                with self.g.undo("Close glyph width"):
                    self.g.width -= self.increment 
                    # print("Done Close Width")
            else:
                # print('I don’t know what’s going on')
                pass
            self.updateUI_BothSB()
            self.g.changed()
        
    def openSBButtonCallback(self, sender):
        # print("\nStarting Open SBs")
        if self.g != None:
            # print("There's a glyph.")
            if self.increment <= 0:
                mojo.UI.Message("Sidebear’s expand/contract increment should be a positive number.")
            elif self.marginValidator(self.g) == True:
                # print("There's a margin.")
                with self.g.undo("Open sidebearings"):
                    self.g.angledLeftMargin += self.increment
                    self.g.angledRightMargin += self.increment
            elif self.widthValidator(self.g) == True:
                # print("There's a width.")
                with self.g.undo("Open glyph width"):
                    self.g.width -= self.increment 
            self.updateUI_BothSB()
            self.g.changed()
        
    def incrementCallback(self, sender):
        prev_inc = self.increment
        try:
            self.increment = int(sender.get())
        except ValueError:
            self.increment = prev_inc
            self.w.inc_text_box.set(prev_inc)
        setExtensionDefault(self.pref_key, self.increment)
            
    def updateUI_BothSB(self):
        # print("Updating the SBs in Sidebear’s UI")
        if self.marginValidator(self.g) == True:
            self.w.LSB.set(str(round(self.g.angledLeftMargin)))
            self.w.RSB.set(str(round(self.g.angledRightMargin)))
        else:
            self.w.LSB.set('')
            self.w.RSB.set('')


# =========================== OBSERVERS =========================== #
        
    def glyphChanged(self, info):
        self.g = info['glyph']
        if self.glyphNameValidator(self.g) == True:
            #print('Glyph name validator was passed: %s' % g.name)
            self.w.curr_glyph_note.set(self.g.name)
        else:
            self.w.curr_glyph_note.set('None')

        self.updateUI_BothSB()
            
    def glyphDraw(self, view):
        self.updateUI_BothSB()

    def appearanceChanged(self, notification):
        self.set_button_images()
        
# # =========================== VALIDATION =========================== #
        
    def marginValidator(self, glyph):
        try:
            if glyph.leftMargin or glyph.leftMargin == 0:
                return True
            else:
                return False
        except AttributeError:
            return False
            
    def widthValidator(self, glyph):
        try:
            if glyph.width or glyph.width == 0:
                return True
            else:
                return False
        except TypeError:
            return False
            
    def glyphNameValidator(self, glyph):
        try:
            if glyph.name:
                return True
            else:
                return False
        except AttributeError:
            return False
            
            
# ======================== INSERT SIDEBEAR INTO INSPECTOR ======================== #        
    
        
class SidebearInsert:

    def __init__(self):
        self.resources_path = os.path.abspath("../resources")
        addObserver(self, "inspectorWindowWillShowDescriptions", "inspectorWindowWillShowDescriptions")

    def inspectorWindowWillShowDescriptions(self, notification):
        title = "Sidebear"
        bear = Sidebear(self.resources_path)
        item = dict(label=title, view=bear.w, size=bear.window_height, collapsed=False, canResize=False)
        if notification["descriptions"][1]['label'] == title:
            del notification["descriptions"][1]
        notification["descriptions"].insert(1, item)

SidebearInsert()