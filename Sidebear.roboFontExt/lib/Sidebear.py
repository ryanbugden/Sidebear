# menuTitle : Sidebear

'''
Robofont extension to quickly adjust glyph spacing.

Ryan Bugden
v0.1
2019-03-28
'''

from AppKit import *
import vanilla
from defcon import Font
from defconAppKit.windows.baseWindow import BaseWindowController
import mojo.UI
from mojo.events import addObserver, removeObserver

class Sidebear:

    def __init__(self):
        
        self.f = None
        self.g = None
    
        window_width = 255
        window_margin = 20
        gutter = 25
        vert_gutter = 12
        rule_gutter = vert_gutter -2
        text_box_height = 20
        row_1_y = -4
        row_2_y = row_1_y + vert_gutter + text_box_height - 5
        row_3_y = row_2_y + vert_gutter + text_box_height
        row_4_y = row_3_y + text_box_height + rule_gutter
        row_5_y = row_4_y + rule_gutter
        third_width = (window_width - (window_margin * 2) - (gutter * 2)) / 3
        self.window_height = window_margin*2 + row_5_y + text_box_height + 11
            
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
            
        # Left swap bridge rule
        self.w.left_sw_rule = vanilla.HorizontalLine((window_margin + third_width, window_margin + row_2_y + text_box_height/2, gutter, 1))
            
        # Swap SB button
        self.w.swap_SB = vanilla.ImageButton(
            (window_margin + third_width + gutter, window_margin + row_2_y, third_width, text_box_height), 
            imagePath='../resources/_icon_Swap.pdf',
            callback=self.swapSBButtonCallback, 
            sizeStyle='regular'
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
    
        # Center Glyph button
        self.w.center_glyph = vanilla.ImageButton(
            (window_margin + third_width + gutter, window_margin + row_3_y, third_width, text_box_height), 
            imagePath='../resources/_icon_Center.pdf',
            callback=self.centerGlyphButtonCallback, 
            sizeStyle='regular'
            )
            
        # Left vert bridge rule
        self.w.left_vert_rule = vanilla.VerticalLine((window_margin + third_width/2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
        
        # Right vert bridge rule
        self.w.right_vert_rule = vanilla.VerticalLine((window_margin + third_width*2.5 + gutter*2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
            
        # Equals RSB button
        self.w.equals_RSB = vanilla.ImageButton(
            (window_margin, window_margin + row_3_y, third_width, text_box_height), 
            imagePath='../resources/_icon_EqualRSB.pdf',
            callback=self.equalsRSBButtonCallback, 
            sizeStyle='regular'
            )
            
        # Equals LSB button
        self.w.equals_LSB = vanilla.ImageButton(
            (window_margin + third_width*2 + gutter*2, window_margin + row_3_y, third_width, text_box_height), 
            imagePath='../resources/_icon_EqualLSB.pdf',
            callback=self.equalsLSBButtonCallback, 
            sizeStyle='regular'
            )
        
        # Rule
        self.w.rule = vanilla.HorizontalLine((window_margin, window_margin + row_4_y, third_width*3 + gutter*2, 1))
    
        # Increment input
        self.increment = 2
        self.w.inc_text_box = vanilla.EditText(
            (window_margin + gutter + third_width, window_margin + row_5_y, third_width, text_box_height), 
            text = "%s" % self.increment, 
            sizeStyle="small", 
            callback=self.incrementCallback
            )
            
        # Left expand/contract bridge rule
        self.w.left_ec_rule = vanilla.HorizontalLine((window_margin + third_width, window_margin + row_5_y + text_box_height/2, gutter, 1))
            
        # Right expand/contract bridge rule
        self.w.right_ec_rule = vanilla.HorizontalLine((window_margin + third_width*2 + gutter, window_margin + row_5_y + text_box_height/2, gutter, 1))
        
        # Close SBs
        self.w.close_SB = vanilla.ImageButton(
            (window_margin, window_margin + row_5_y, third_width, text_box_height), 
            imagePath='../resources/_icon_Close.pdf',
            callback=self.closeSBButtonCallback, 
            sizeStyle='regular'
            )
        
        # Open SBs
        self.w.open_SB = vanilla.ImageButton(
            (window_margin + third_width*2 + gutter*2, window_margin + row_5_y, third_width, text_box_height), 
            imagePath='../resources/_icon_Open.pdf',
            callback=self.openSBButtonCallback, 
            sizeStyle='regular'
            )
            
        # Increment
        self.w.incr_caption = vanilla.TextBox(
            (window_margin + third_width, window_margin + row_5_y + 23, third_width + gutter*2, text_box_height), 
            "Increment",
            sizeStyle = "mini", 
            alignment = "center")
            
        addObserver(self, "inspectorWindowWillShowDescriptions", "inspectorWindowWillShowDescriptions")
        addObserver(self, "glyphChanged", "currentGlyphChanged")
        addObserver(self, "glyphDraw", "draw")
        
        

    
# =========================== CALLBACKS =========================== #

    
    def editLSBCallback(self, sender):
        self.g = CurrentGlyph()
        try:
            des_lsb = int(sender.get())
            if self.g:
                with self.g.undo("Edit LSB"):
                    self.g.leftMargin = des_lsb
        except ValueError:
            try:
                spc2glyph = str(sender.get())
                self.f = CurrentFont()
                if self.f[spc2glyph]:
                    self.g.leftMargin = self.f[spc2glyph].leftMargin
            except ValueError:
                self.w.LSB.set(self.g.leftMargin)
        
        
    def editRSBCallback(self, sender):
        self.g = CurrentGlyph()
        try:
            des_rsb = int(sender.get())
            if self.g:
                with self.g.undo("Edit RSB"):
                    self.g.rightMargin = des_rsb
        except ValueError:
            try:
                spc2glyph = str(sender.get())
                self.f = CurrentFont()
                if self.f[spc2glyph]:
                    self.g.rightMargin = self.f[spc2glyph].rightMargin
            except ValueError:
                self.w.RSB.set(self.g.rightMargin)
        
    def swapSBButtonCallback(self, sender):
        if self.g:
            if self.marginValidator(self.g) == True:
                with self.g.undo("Swap SB"):
                    prev_LSB = self.g.leftMargin
                    prev_RSB = self.g.rightMargin
                    self.g.leftMargin = int(prev_RSB)
                    self.g.rightMargin = int(prev_LSB)
                    # print("Swapped sidebearings")
        
    def centerGlyphButtonCallback(self, sender):
        # Note: this may change the set width by 1, in favor of symmetrical SBs
        if self.g:
            if self.marginValidator(self.g) == True:
                with self.g.undo("Center glyph"):
                    margins_average = (self.g.rightMargin + self.g.leftMargin) // 2
                    self.g.leftMargin = margins_average
                    self.g.rightMargin = margins_average
                
    
    def equalsRSBButtonCallback(self, sender):
        if self.g:
            if self.marginValidator(self.g) == True:
                with self.g.undo("LSB = RSB"):
                    self.g.leftMargin = self.g.rightMargin
    
    
    def equalsLSBButtonCallback(self, sender):
        if self.g:
            if self.marginValidator(self.g) == True:
                with self.g.undo("RSB = LSB"):
                    self.g.rightMargin = int(self.g.leftMargin)
        
    def closeSBButtonCallback(self, sender):
        
        if self.g == None:
            print("Do you have an active glyph?")
        elif self.marginValidator(self.g) == True:
            with self.g.undo("Close sidebearings"):
                self.g.leftMargin -= self.increment
                self.g.rightMargin -= self.increment
        elif self.widthValidator(self.g) == True:
            with self.g.undo("Close glyph width"):
                # print(self.g.contours + self.g.components)
                self.g.width -= self.increment 
        elif self.increment < 0: 
            mojo.UI.Message("Increment should be positive.")
        else:
            print('Something’s up! CloseSB')
        
        
    def openSBButtonCallback(self, sender):

        if self.g == None:
            print("Do you have an active glyph?")
        elif self.marginValidator(self.g) == True:
            with self.g.undo("Close sidebearings"):
                self.g.leftMargin += self.increment
                self.g.rightMargin += self.increment
        elif self.widthValidator(self.g) == True:
            with self.g.undo("Close glyph width"):
                # print(self.g.contours + self.g.components)
                self.g.width += self.increment  
        elif self.increment < 0: 
            mojo.UI.Message("Increment should be positive.")
        else:
            print('Something’s up! OpenSB')
            
        
    def incrementCallback(self, sender):
        self.increment = int(sender.get())
        
        
# =========================== OBSERVERS =========================== #
        
    def glyphChanged(self, info):
        self.g = CurrentGlyph()
        if self.glyphNameValidator(self.g) == True:
            print('Glyph name validator was passed: %s' % self.g.name)
            self.w.curr_glyph_note.set(self.g.name)
            if self.marginValidator(self.g) == True:
                print('Margin validator was passed: %s' % self.g.name)
                self.w.LSB.set(int(self.g.leftMargin))
                self.w.RSB.set(int(self.g.rightMargin))
            else:
                print('Margin validator was NOT passed: %s' % self.g.name)
                self.w.LSB.set('')
                self.w.RSB.set('')
        else:
            print('Glyph name validator was NOT passed.')
            self.w.curr_glyph_note.set('None')
            self.w.LSB.set('')
            self.w.RSB.set('')
            
    def glyphDraw(self, view):
        if self.marginValidator(self.g) == True:
            self.w.LSB.set(self.g.leftMargin)
            self.w.RSB.set(self.g.rightMargin)
        else:
            self.w.LSB.set('')
            self.w.RSB.set('')
        
        
# # =========================== VALIDATION =========================== #
        
    def marginValidator(self, glyph):
        if glyph.leftMargin == None:
            return False
        else:
            return True
            
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
            
            
# =========================== BUILD PANEL =========================== #        
    
    def inspectorWindowWillShowDescriptions(self, notification):
        title = "Sidebear"
        item = dict(label=title, view=self.w, size=self.window_height, collapsed=False, canResize=False)
        if notification["descriptions"][1]['label'] == "Sidebear":
            del notification["descriptions"][1]
            
        notification["descriptions"].insert(1, item)
        
        
Sidebear()