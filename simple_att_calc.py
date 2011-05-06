#!/usr/bin/env python

import sys

import math
import pickle

import nistxcom as nx

try:
	import pygtk
	pygtk.require("2.0")
except:
	pass

try:
	import gtk
	import gtk.glade
except:
	print "You need to install pyGTK or GTKv2 ",
	print "or set your PYTHONPATH correctly."
	print "try: export PYTHONPATH=",
	print "/usr/local/lib/python2.2/site-packages/"
	sys.exit(1)

class appgui:
	def __init__(self):
		gladefile = "simple_main.glade"
		windowname = "mainwindow"
		self.wTree=gtk.glade.XML(gladefile, windowname)

		dic = { "on_attlen_calculate_clicked" : self.attlen_calculate_clicked,
			"on_abseff_calculate_clicked" : self.abseff_calculate_clicked,
			"on_efflen_calculate_clicked" : self.efflen_calculate_clicked,
			"on_mainwindow_destroy" : (gtk.main_quit) ,
			"on_QuitMenuItem_activate" : (gtk.main_quit) }

		self.wTree.signal_autoconnect(dic)

		densities = pickle.load(open('densities.dat','rb'))

		elements = densities.keys()
		elements.sort()

		combo = self.wTree.get_widget("element_combo_box")
		combo2 = self.wTree.get_widget("element_combo_box2")
		combo3 = self.wTree.get_widget("element_combo_box3")
		for el in elements:
			combo.append_text(el)
			combo2.append_text(el)
			combo3.append_text(el)

		combo.set_active(0)
		combo2.set_active(0)
		combo3.set_active(0)
	
		return

	def attlen_calculate_clicked(self,widget):
		el = self.wTree.get_widget("element_combo_box").get_active_text()
		energy = self.wTree.get_widget("attlen_energy_box").get_text()
		[self.E,self.attlen] = nx.calclengths([el],energy)

		if eval(energy) in self.E[el]:
			i = self.E[el].index(eval(energy))
			self.wTree.get_widget("attlen_box").set_text(str(self.attlen[el][i]) + ' cm')
		else:
			print "Some carazy happened. Bailing!"

	def abseff_calculate_clicked(self,widget):
		el = self.wTree.get_widget("element_combo_box2").get_active_text()
		energy = self.wTree.get_widget("abseff_energy_entry").get_text()
		length = eval(self.wTree.get_widget("abseff_thickness_entry").get_text())
		[self.E,self.attlen] = nx.calclengths([el],energy)

		if eval(energy) in self.E[el]:
			i = self.E[el].index(eval(energy))
			al = self.attlen[el][i] / 100 # convert to m

			eff = (1 - math.exp(-length/al)) * 100
			effstr = "%3.2f %% Absorption" % (eff)
			
			self.wTree.get_widget("abseff_eff_entry").set_text(effstr)
		else:
			print "I'm a outta here!"
		
	def efflen_calculate_clicked(self,widget):
		el = self.wTree.get_widget("element_combo_box3").get_active_text()
		energy = self.wTree.get_widget("efflen_energy_entry").get_text()
		abs = eval(self.wTree.get_widget("efflen_absorption_entry").get_text())/100.0

		[self.E,self.attlen] = nx.calclengths([el],energy)

		if eval(energy) in self.E[el]:
			i = self.E[el].index(eval(energy))
			al = self.attlen[el][i] / 100 # convert to m

			length = -al * math.log(1 - abs)

			#print abs,al,math.log(1-abs),length

			self.wTree.get_widget("efflen_len_entry").set_text(str(length) + " m")



app = appgui()
gtk.main()
