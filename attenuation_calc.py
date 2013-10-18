#!/usr/bin/env python

import sys

import matplotlib
matplotlib.use('GTK')
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar
from numpy import arange, sin, pi

from scipy import interpolate

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
		self.gladefile = "attenuation_calc.glade"
		windowname = "MainWindow"
		self.wTree=gtk.glade.XML(self.gladefile, windowname)

		dic = { "on_GetDataButton_clicked" : self.button1_clicked,
			"on_SaveImageMenuItem_activate" : self.save_image,
			"on_ExportMenuItem_activate" : self.save_data,
			"on_MainWindow_destroy" : (gtk.main_quit) ,
			"on_QuitMenuItem_activate" : (gtk.main_quit),
			"on_about_menuitem_activate" : self.about }

		self.wTree.signal_autoconnect(dic)

		self.figure = Figure(figsize=(6,4), dpi=72)
		self.axis = self.figure.add_subplot(111)
		self.axis.set_xlabel('Energies')
		self.axis.set_ylabel('Attenuation Length (microns)')
		self.axis.set_title('Attenuation Lengths vs Energy')
		self.axis.grid(True)
		self.canvas = FigureCanvasGTK(self.figure)
		self.canvas.show()
		self.graphview = self.wTree.get_widget("vbox1")
		self.graphview.pack_start(self.canvas,True,True)
		#self.graphview.pack_start(self.canvas,True,True)

		self.wTree.get_widget(windowname).maximize()

		self.E = {}
		self.attlen = {}

		return

	def about(self,widget):
		print 'Hello World'
		
		t = gtk.glade.XML(self.gladefile, "aboutdialog1")
	
		about = t.get_widget("aboutdialog1")

		about.run()
		about.hide()

		return

	def button1_clicked(self,widget):
		self.graphview.remove(self.canvas) # important else they just get inserted again each time (not replaced)
		self.axis.cla()
		eltext = self.wTree.get_widget("ElementText").get_text()
		if eltext.find(',') == -1:
			el = self.wTree.get_widget("ElementText").get_text().split()
		else:
			el = self.wTree.get_widget("ElementText").get_text().split(',')		
		
		[self.E,self.attlen] = nx.calclengths(el)
		for e in self.attlen.keys():
			self.axis.loglog(self.E[e],self.attlen[e],label=e);
		self.axis.set_xlabel('Energy (MeV)')
		self.axis.set_ylabel('Attenuation Length (cm)')
		self.axis.set_title('Attenuation Lengths vs Energy')
		self.axis.legend(loc='lower right')
		self.axis.grid(True)
		self.canvas.destroy()
                self.canvas = FigureCanvasGTK(self.figure)
                self.canvas.show()
		self.graphview = self.wTree.get_widget("vbox1")
                self.graphview.pack_end(self.canvas, True, True)
                #self.graphview.pack_start(self.canvas, True, True)

		#print dir(self.canvas)

	def save_image(self,widget):
		chooser = gtk.FileChooserDialog(title='Save File',action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		chooser.set_default_response(gtk.RESPONSE_OK)

		response = chooser.run()
		if response == gtk.RESPONSE_OK:	
			print chooser.get_filename()
			self.figure.savefig(chooser.get_filename())
		else:
			print 'No files selected'

		chooser.destroy()
	
	def save_data(self,widget):
		chooser = gtk.FileChooserDialog(title='Save File',action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
	
		chooser.set_default_response(gtk.RESPONSE_OK)

		response = chooser.run()
		if response == gtk.RESPONSE_OK:
			print chooser.get_filename()

			filename = chooser.get_filename()

			Eint = []
			# ==Interpolate data==

			# Find unique energies
			for e in self.E.keys():
				Eint = Eint + self.E[e]
			
			# Uniquify list
			Eint = list(set(Eint))
			Eint.sort()
			
			att_ints = []
			# Interpolate the data
			for e in self.attlen.keys():
				buff = interpolate.interp1d(self.E[e], self.attlen[e], kind='linear', bounds_error=False)
				att_ints.append(buff(Eint))

			print 'Writing data to file:',filename

			fout = open(filename,'w')

			fout.write('# Data output from attenuation calculator\n')
			fout.write('Energy,'+ ','.join(self.E.keys())+'\n')
		
			print len(Eint), len(self.attlen.keys())
			for i in range(len(Eint)):
				fout.write(str(Eint[i]))
				for j in range(len(self.attlen.keys())):
					fout.write(',' + str(att_ints[j][i]))
				fout.write('\n')
				#fout.write(str(energy)+','+','.join([i(energy) for i in att_ints])+'\n')

			print 'Done'

		else:
			print 'No files selected'

		chooser.destroy()	
	
app = appgui()
gtk.main()
