# menuTitle : Sidebear

'''
Robofont extension that installs an Inspector panel that enables 
you to quickly manipulating your glyph’s sidebearings.

Ryan Bugden
v1.0.3: 2019.04.09
v1:     2019.03.28
'''

# from AppKit import *
import vanilla
import mojo.UI
from mojo.events import addObserver

other_SB = ','

class UI_Group(vanilla.Group):
	
	def __init__(self, posSize):
		# subscribe here
		super().__init__(posSize)
		
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
	
		# Current glyph
		self.curr_glyph_note = vanilla.TextBox(
			(window_margin + third_width/2, window_margin + row_1_y, third_width*2 + gutter*2, text_box_height), 
			"None",
			sizeStyle = "regular", 
			alignment = "center")

		# Left width span rule
		self.left_w_span = vanilla.HorizontalLine((window_margin + 2, window_margin + row_1_y + (text_box_height/2), third_width, 1))
		
		# Left width vert rule
		self.left_w_vert = vanilla.VerticalLine((window_margin + 1, window_margin + row_1_y, 1, text_box_height))
		
		# Right width span rule
		self.right_w_span = vanilla.HorizontalLine((window_margin + third_width*2 + gutter*2, window_margin + row_1_y + (text_box_height/2), third_width - 1, 1))
		
		# Right width vert rule
		self.right_w_vert = vanilla.VerticalLine((window_margin + third_width*3 + gutter*2 - 1, window_margin + row_1_y, 1, text_box_height))
		
		# Left side-bearing
		self.LSB = vanilla.EditText(
			(window_margin, window_margin + row_2_y, third_width, text_box_height), 
			text = "", 
			sizeStyle = "small", 
			callback = Sidebear.editLSBCallback,
			continuous = False
			)
		self.LSB.getNSTextField().setAlignment_(2)
			
		# Left swap bridge rule
		self.left_sw_rule = vanilla.HorizontalLine((window_margin + third_width, window_margin + row_2_y + text_box_height/2, gutter, 1))
			
		# Swap SB button
		self.swap_SB = vanilla.ImageButton(
			(window_margin + third_width + gutter, window_margin + row_2_y, third_width, text_box_height), 
			imagePath = '../resources/_icon_Swap.pdf',
			callback = Sidebear.swapSBButtonCallback, 
			sizeStyle = 'regular'
			)
			
		# Right swap bridge rule
		self.right_sw_rule = vanilla.HorizontalLine((window_margin + third_width*2 + gutter, window_margin + row_2_y + text_box_height/2, gutter, 1))
		
		# Right side-bearing
		self.RSB = vanilla.EditText(
			(window_margin + third_width*2 + gutter*2, window_margin + row_2_y, third_width, text_box_height), 
			text = "", 
			sizeStyle = "small", 
			callback = Sidebear.editRSBCallback,
			continuous = False
			)
		self.RSB.getNSTextField().setAlignment_(2)
	
		# Center Glyph button
		self.center_glyph = vanilla.ImageButton(
			(window_margin + third_width + gutter, window_margin + row_3_y, third_width, text_box_height), 
			imagePath = '../resources/_icon_Center.pdf',
			callback = Sidebear.centerGlyphButtonCallback, 
			sizeStyle = 'regular'
			)
			
		# Left vert bridge rule
		self.left_vert_rule = vanilla.VerticalLine((window_margin + third_width/2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
		
		# Right vert bridge rule
		self.right_vert_rule = vanilla.VerticalLine((window_margin + third_width*2.5 + gutter*2, window_margin + row_2_y + text_box_height, 1, vert_gutter))
			
		# Equals RSB button
		self.equals_RSB = vanilla.ImageButton(
			(window_margin, window_margin + row_3_y, third_width, text_box_height), 
			imagePath = '../resources/_icon_EqualRSB.pdf',
			callback = Sidebear.equalsRSBButtonCallback, 
			sizeStyle = 'regular'
			)
			
		# Equals LSB button
		self.equals_LSB = vanilla.ImageButton(
			(window_margin + third_width*2 + gutter*2, window_margin + row_3_y, third_width, text_box_height), 
			imagePath = '../resources/_icon_EqualLSB.pdf',
			callback = Sidebear.equalsLSBButtonCallback, 
			sizeStyle = 'regular'
			)
		
		# Rule
		self.rule = vanilla.HorizontalLine((window_margin, window_margin + row_4_y, third_width*3 + gutter*2, 1))
	
		# Increment input
		self.increment = 2
		self.inc_text_box = vanilla.EditText(
			(window_margin + gutter + third_width, window_margin + row_5_y, third_width, text_box_height), 
			text = "%s" % self.increment, 
			sizeStyle="small", 
			callback = Sidebear.incrementCallback
			)
		self.inc_text_box.getNSTextField().setAlignment_(2)
			
		# Left expand/contract bridge rule
		self.left_ec_rule = vanilla.HorizontalLine((window_margin + third_width, window_margin + row_5_y + text_box_height/2, gutter, 1))
			
		# Right expand/contract bridge rule
		self.right_ec_rule = vanilla.HorizontalLine((window_margin + third_width*2 + gutter, window_margin + row_5_y + text_box_height/2, gutter, 1))
		
		# Close SBs
		self.close_SB = vanilla.ImageButton(
			(window_margin, window_margin + row_5_y, third_width, text_box_height), 
			imagePath='../resources/_icon_Close.pdf',
			callback = Sidebear.closeSBButtonCallback, 
			sizeStyle='regular'
			)
		
		# Open SBs
		self.open_SB = vanilla.ImageButton(
			(window_margin + third_width*2 + gutter*2, window_margin + row_5_y, third_width, text_box_height), 
			imagePath = '../resources/_icon_Open.pdf',
			callback = Sidebear.openSBButtonCallback, 
			sizeStyle = 'regular'
			)
			
		# Increment
		self.incr_caption = vanilla.TextBox(
			(window_margin + third_width, window_margin + row_5_y + 23, third_width + gutter*2, text_box_height), 
			"Increment",
			sizeStyle = "mini", 
			alignment = "center")

	
	# def getCurrentGlyph(self):
	#     return self.i.get()
	
	# Current Glyph
	def setCurrentGlyph(self, input):
		self.curr_glyph_note.set(str(input))

	# LSB
	def getLSBInput(self):
		return self.LSB.get()

	def setLSB(self, input):
		self.LSB.set(str(input))

	# RSB
	def getRSBInput(self):
		return self.RSB.get()

	def setRSB(self, input):
		self.RSB.set(str(input))

	# SB
	def getIncrementInput(self):
		return self.inc_text_box.get()

	def setIncrement(self, input):
		self.inc_text_box.set(str(input))



class Sidebear(object):

	def __init__(self):

		self.g = None

		self.view = UI_Group((0, 0, -0, -0))
				
		addObserver(self, "inspectorWindowWillShowDescriptions", "inspectorWindowWillShowDescriptions")
		addObserver(self, "glyphChanged", "currentGlyphChanged")
		addObserver(self, "glyphDraw", "draw")
		
	
# =========================== CALLBACKS =========================== #

	
	def editLSBCallback(self):
		if self.g != None:
			try:
				des_lsb = int(self.view.getLSBInput())
				with self.g.undo("Edit LSB"):
					self.g.leftMargin = des_lsb
					self.view.setLSB(self.g.leftMargin)
			except ValueError:
				try:
					spc2glyph = str(self.view.getLSBInput())
					self.f = CurrentFont()
					if other_SB in spc2glyph:
						spc2glyph = spc2glyph.replace(other_SB,"")
						if self.f[spc2glyph] != None:
							self.g.leftMargin = self.f[spc2glyph].rightMargin
						self.view.setLSB(self.g.leftMargin)
					else:
						if self.f[spc2glyph] != None:
							self.g.leftMargin = self.f[spc2glyph].leftMargin
						self.view.setLSB(self.g.leftMargin)
				except ValueError:
					self.view.setLSB(self.g.leftMargin)
		
		
	def editRSBCallback(self):
		if self.g != None:
			try:
				des_rsb = int(self.view.getRSBInput())
				with self.g.undo("Edit RSB"):
					self.g.rightMargin = des_rsb
					self.view.setRSB(self.g.rightMargin)
			except ValueError:
				try:
					spc2glyph = str(self.view.getRSBInput())
					self.f = CurrentFont()
					if other_SB in spc2glyph:
						spc2glyph = spc2glyph.replace(other_SB,"")
						if self.f[spc2glyph] != None:
							self.g.rightMargin = self.f[spc2glyph].leftMargin
						self.view.setRSB(self.g.rightMargin)
					else:
						if self.f[spc2glyph] != None:
							self.g.rightMargin = self.f[spc2glyph].rightMargin
						self.view.setRSB(self.g.rightMargin)
				except ValueError:
					self.view.setRSB(self.g.rightMargin)
		
	def swapSBButtonCallback(self):
		if self.g != None:
			if self.marginValidator(self.g) == True:
				with self.g.undo("Swap SB"):
					prev_LSB = self.g.leftMargin
					prev_RSB = self.g.rightMargin
					self.g.leftMargin = int(prev_RSB)
					self.g.rightMargin = int(prev_LSB)
					# print("Swapped sidebearings")
					self.g.update()
		
	def centerGlyphButtonCallback(self):
		# Note: this may change the set width by 1, in favor of symmetrical SBs
		if self.g != None:
			if self.marginValidator(self.g) == True:
				with self.g.undo("Center glyph"):
					margins_average = (self.g.rightMargin + self.g.leftMargin) // 2
					self.g.leftMargin = margins_average
					self.g.rightMargin = margins_average
					self.g.update()
				
	
	def equalsRSBButtonCallback(self):
		print("Starting Equals RSB")
		if self.g != None:
			print("There's a glyph.")
			if self.marginValidator(self.g) == True:
				print("There's a margin.")
				with self.g.undo("LSB = RSB"):
					self.g.leftMargin = int(self.g.rightMargin)
					self.g.update()
					print("Done equals RSB")
	
	
	def equalsLSBButtonCallback(self):
		print("Starting Equals LSB")
		if self.g != None:
			print("There's a glyph.")
			if self.marginValidator(self.g) == True:
				print("There's a margin.")
				with self.g.undo("RSB = LSB"):
					self.g.rightMargin = int(self.g.leftMargin)
					self.g.update()
					print("Done equals LSB")
		
	def closeSBButtonCallback(self):
		print("\nStarting Close SBs")
		if self.g != None:
			print("There's a glyph.")
			if self.view.increment <= 0:
				mojo.UI.Message("Sidebear’s expand/contract increment should be a positive number.")
			elif self.marginValidator(self.g) == True:
				print("There's a margin.")
				with self.g.undo("Close sidebearings"):
					self.g.leftMargin -= self.view.increment
					self.g.rightMargin -= self.view.increment
					self.g.update()
					print("Done Close SBs")
			elif self.widthValidator(self.g) == True:
				print("There's a width.")
				with self.g.undo("Close glyph width"):
					self.g.width -= self.view.increment 
					self.g.update()
					print("Done Close Width")
			else:
				print('I don’t know what’s going on')
		
		
	def openSBButtonCallback(self):
		print("\nStarting Open SBs")
		if self.g != None:
			print("There's a glyph.")
			if self.view.increment <= 0:
				mojo.UI.Message("Sidebear’s expand/contract increment should be a positive number.")
			elif self.marginValidator(self.g) == True:
				print("There's a margin.")
				with self.g.undo("Open sidebearings"):
					self.g.leftMargin += self.view.increment
					self.g.rightMargin += self.view.increment
					self.g.update()
					print("Done Open SBs")
			elif self.widthValidator(self.g) == True:
				print("There's a width.")
				with self.g.undo("Open glyph width"):
					self.g.width -= self.view.increment 
					self.g.update()
					print("Done Open Width")
			else:
				print('I don’t know what’s going on')
			
		
	def incrementCallback(self):
		prev_inc = self.view.increment
		try:
			self.view.increment = int(self.view.getIncrementInput())
		except ValueError:
			self.view.increment = prev_inc
			self.view.inc_text_box.set(prev_inc)
		
		
# =========================== OBSERVERS =========================== #
		
	def glyphChanged(self, info):
		self.g = CurrentGlyph()
		if self.glyphNameValidator(self.g) == True:
			#print('Glyph name validator was passed: %s' % g.name)
			self.view.setCurrentGlyph(self.g.name)
			if self.marginValidator(self.g) == True:
				#print('Margin validator was passed: %s' % g.name)
				self.view.setLSB(int(self.g.leftMargin))
				self.view.setRSB(int(self.g.rightMargin))
			else:
				#print('Margin validator was NOT passed: %s' % g.name)
				self.view.setLSB('')
				self.view.setRSB('')
		else:
			#print('Glyph name validator was NOT passed.')
			self.view.setCurrentGlyph("None")
			self.view.setLSB('')
			self.view.setRSB('')
			
	def glyphDraw(self, view):
		if self.marginValidator(self.g) == True:
			self.view.setLSB(int(self.g.leftMargin))
			self.view.setRSB(int(self.g.rightMargin))
		else:
			self.view.setLSB('')
			self.view.setRSB('')
		
		
# # =========================== VALIDATION =========================== #
		
	def marginValidator(self, glyph):
		try:
			if glyph.leftMargin == None:
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
			
			
# =========================== BUILD PANEL =========================== #        
	
	def inspectorWindowWillShowDescriptions(self, notification):
		print('Putting a panel on Inspector')
		title = "Sidebear"
		item = dict(label=title, view=self.view, size=self.view.window_height, collapsed=False, canResize=False)
		if notification["descriptions"][1]['label'] == title:
		    del notification["descriptions"][1]
		notification["descriptions"].insert(1, item)
		
		
Sidebear()