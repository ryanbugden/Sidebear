# menuTitle : Sidebear

'''
Installs an Inspector panel that enables one to 
quickly manipulating the current glyph’s sidebearings.

Ryan Bugden
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

other_SB = ','

class Sidebear(object):

    def __init__(self, resources_path):
        
        self.g = None
    
        window_width = 255
        window_margin = 20
        gutter = 25
        vert_gutter = 12
        rule_gutter = vert_gutter - 2
        text_box_height = 20
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
            (window_margin + third_width + gutter, window_margin + row_2_y, third_width, text_box_height), 
            imagePath = resources_path + '/_icon_Swap.pdf',
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
            (window_margin + third_width + gutter, window_margin + row_3_y, third_width, text_box_height), 
            imagePath = resources_path + '/_icon_Center.pdf',
            callback = self.centerGlyphButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Left vert bridge rule
        self.w.left_vert_rule = vanilla.VerticalLine((window_margin + third_width/2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
        
        # Right vert bridge rule
        self.w.right_vert_rule = vanilla.VerticalLine((window_margin + third_width*2.5 + gutter*2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
            
        # Equals RSB button
        self.w.equals_RSB = vanilla.ImageButton(
            (window_margin, window_margin + row_3_y, third_width, text_box_height), 
            imagePath = resources_path + '/_icon_EqualRSB.pdf',
            callback = self.equalsRSBButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Equals LSB button
        self.w.equals_LSB = vanilla.ImageButton(
            (window_margin + third_width*2 + gutter*2, window_margin + row_3_y, third_width, text_box_height), 
            imagePath = resources_path + '/_icon_EqualLSB.pdf',
            callback = self.equalsLSBButtonCallback, 
            sizeStyle = 'regular'
            )
        
        # Rule
        self.w.rule = vanilla.HorizontalLine((window_margin, window_margin + row_4_y, third_width*3 + gutter*2, 1))
    
        # Increment input
        self.increment = 2
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
            (window_margin, window_margin + row_5_y, third_width, text_box_height), 
            imagePath = resources_path + '/_icon_Close.pdf',
            callback = self.closeSBButtonCallback, 
            sizeStyle = 'regular'
            )
        
        # Open SBs
        self.w.open_SB = vanilla.ImageButton(
            (window_margin + third_width*2 + gutter*2, window_margin + row_5_y, third_width, text_box_height), 
            imagePath = resources_path + '/_icon_Open.pdf',
            callback = self.openSBButtonCallback, 
            sizeStyle = 'regular'
            )
            
        # Increment
        self.w.incr_caption = vanilla.TextBox(
            (window_margin + third_width, window_margin + row_5_y + 23, third_width + gutter*2, text_box_height), 
            "Increment",
            sizeStyle = "mini", 
            alignment = "center")
            
        addObserver(self, "glyphChanged", "currentGlyphChanged")
        addObserver(self, "glyphChanged", "viewDidChangeGlyph")
        addObserver(self, "glyphChanged", "glyphWindowDidOpen")
        addObserver(self, "glyphDraw", "draw")

    
# =========================== CALLBACKS =========================== #

    
    def editLSBCallback(self, sender):
        if self.g != None:
            try:
                des_lsb = int(sender.get())
                with self.g.undo("Edit LSB"):
                    self.g.angledLeftMargin = des_lsb
                    self.w.LSB.set(self.g.angledLeftMargin)
            except ValueError:
                try:
                    spc2glyph = str(sender.get())
                    self.f = CurrentFont()
                    if other_SB in spc2glyph:
                        spc2glyph = spc2glyph.replace(other_SB,"")
                        if self.f[spc2glyph] != None:
                            self.g.angledLeftMargin = self.f[spc2glyph].angledRightMargin
                        self.w.LSB.set(self.g.angledLeftMargin)
                    else:
                        if self.f[spc2glyph] != None:
                            self.g.angledLeftMargin = self.f[spc2glyph].angledLeftMargin
                        self.w.LSB.set(self.g.angledLeftMargin)
                except ValueError:
                    self.w.LSB.set(self.g.angledLeftMargin)
        
    def editRSBCallback(self, sender):
        if self.g != None:
            try:
                des_rsb = int(sender.get())
                with self.g.undo("Edit RSB"):
                    self.g.angledRightMargin = des_rsb
                    self.w.RSB.set(self.g.angledRightMargin)
            except ValueError:
                try:
                    spc2glyph = str(sender.get())
                    self.f = CurrentFont()
                    if other_SB in spc2glyph:
                        spc2glyph = spc2glyph.replace(other_SB,"")
                        if self.f[spc2glyph] != None:
                            self.g.angledRightMargin = self.f[spc2glyph].angledLeftMargin
                        self.w.RSB.set(self.g.angledRightMargin)
                    else:
                        if self.f[spc2glyph] != None:
                            self.g.angledRightMargin = self.f[spc2glyph].angledRightMargin
                        self.w.RSB.set(self.g.angledRightMargin)
                except ValueError:
                    self.w.RSB.set(self.g.angledRightMargin)
        
    def swapSBButtonCallback(self, sender):
        if self.g != None:
            if self.marginValidator(self.g) == True:
                with self.g.undo("Swap SB"):
                    prev_LSB = self.g.angledLeftMargin
                    prev_RSB = self.g.angledRightMargin
                    self.g.angledLeftMargin = int(prev_RSB)
                    self.g.angledRightMargin = int(prev_LSB)
                    # print("Swapped sidebearings")
                    self.g.changed()
        
    def centerGlyphButtonCallback(self, sender):
        # Note: this may change the set width by 1, in favor of symmetrical SBs
        if self.g != None:
            if self.marginValidator(self.g) == True:
                with self.g.undo("Center glyph"):
                    margins_average = (round(self.g.angledRightMargin) + round(self.g.angledLeftMargin)) // 2
                    self.g.angledLeftMargin = margins_average
                    self.g.angledRightMargin = margins_average
                    self.g.changed()
                
    def equalsRSBButtonCallback(self, sender):
        print("Starting Equals RSB")
        if self.g != None:
            print("There's a glyph.")
            if self.marginValidator(self.g) == True:
                print("There's a margin.")
                with self.g.undo("LSB = RSB"):
                    self.g.angledLeftMargin = int(self.g.angledRightMargin)
                    self.g.changed()
                    print("Done equals RSB")
    
    def equalsLSBButtonCallback(self, sender):
        print("Starting Equals LSB")
        if self.g != None:
            print("There's a glyph.")
            if self.marginValidator(self.g) == True:
                print("There's a margin.")
                with self.g.undo("RSB = LSB"):
                    self.g.angledRightMargin = int(self.g.angledLeftMargin)
                    self.g.changed()
                    print("Done equals LSB")
        
    def closeSBButtonCallback(self, sender):
        print("\nStarting Close SBs")
        if self.g != None:
            print("There's a glyph.")
            if self.increment <= 0:
                mojo.UI.Message("Sidebear’s expand/contract increment should be a positive number.")
            elif self.marginValidator(self.g) == True:
                print("There's a margin.")
                with self.g.undo("Close sidebearings"):
                    self.g.angledLeftMargin -= self.increment
                    self.g.angledRightMargin -= self.increment
                    self.g.changed()
                    print("Done Close SBs")
            elif self.widthValidator(self.g) == True:
                print("There's a width.")
                with self.g.undo("Close glyph width"):
                    self.g.width -= self.increment 
                    self.g.changed()
                    print("Done Close Width")
            else:
                print('I don’t know what’s going on')
        
        
    def openSBButtonCallback(self, sender):
        print("\nStarting Open SBs")
        if self.g != None:
            print("There's a glyph.")
            if self.increment <= 0:
                mojo.UI.Message("Sidebear’s expand/contract increment should be a positive number.")
            elif self.marginValidator(self.g) == True:
                print("There's a margin.")
                with self.g.undo("Open sidebearings"):
                    self.g.angledLeftMargin += self.increment
                    self.g.angledRightMargin += self.increment
                    self.g.changed()
                    print("Done Open SBs")
            elif self.widthValidator(self.g) == True:
                print("There's a width.")
                with self.g.undo("Open glyph width"):
                    self.g.width -= self.increment 
                    self.g.changed()
                    print("Done Open Width")
            else:
                print('I don’t know what’s going on')
            
        
    def incrementCallback(self, sender):
        prev_inc = self.increment
        try:
            self.increment = int(sender.get())
        except ValueError:
            self.increment = prev_inc
            self.w.inc_text_box.set(prev_inc)
        
        
# =========================== OBSERVERS =========================== #
        
    def glyphChanged(self, info):
        self.g = CurrentGlyph()
        if self.glyphNameValidator(self.g) == True:
            #print('Glyph name validator was passed: %s' % g.name)
            self.w.curr_glyph_note.set(self.g.name)
            if self.marginValidator(self.g) == True:
                #print('Margin validator was passed: %s' % g.name)
                self.w.LSB.set(int(self.g.angledLeftMargin))
                self.w.RSB.set(int(self.g.angledRightMargin))
            else:
                self.w.LSB.set('')
                self.w.RSB.set('')
        else:
            self.w.curr_glyph_note.set('None')
            self.w.LSB.set('')
            self.w.RSB.set('')
            
    def glyphDraw(self, view):
        if self.marginValidator(self.g) == True:
            self.w.LSB.set(int(self.g.angledLeftMargin))
            self.w.RSB.set(int(self.g.angledRightMargin))
        else:
            self.w.LSB.set('')
            self.w.RSB.set('')
        
        
# # =========================== VALIDATION =========================== #
        
    def marginValidator(self, glyph):
        try:
            if glyph.angledLeftMargin == None:
                return False
            else:
                return True
        except AttributeError:
            return False
            
    def widthValidator(self, glyph):
        try:
            v = glyph.width
            return True
        except TypeError:
            return False
            
    def glyphNameValidator(self, glyph):
        try:
            v = glyph.name
            return True
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
