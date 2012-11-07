#! /usr/bin/env python

#    Copyright (C) 2012  Club Capra - capra.etsmtl.ca
#
#    This file is part of CapraVision.
#    
#    CapraVision is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk

import cv2
import numpy as np

from CapraVision.client.analysis.linetest import LineTest
from CapraVision.client.gui.utils import *
from CapraVision.core import filterchain

class WinLineTest:
    
    def __init__(self):
        ui = get_ui(self, 'imageListStore', 'paramsListStore')
        self.window = ui.get_object(win_name(self))
        self.imageListStore = ui.get_object('imageListStore')
        self.txtFilterchain = ui.get_object('txtFilterchain')
        self.txtTestFolder = ui.get_object('txtTestFolder')
        self.lblPrecision = ui.get_object('lblPrecision')
        self.lblNoise = ui.get_object('lblNoise')
        self.lblNbImages = ui.get_object('lblNbImages')
        self.lstImage = ui.get_object('lstImage')
        self.imgOriginal = ui.get_object('imgOriginal')
        self.imgExample = ui.get_object('imgExample')
        
        self.paramsListStore = ui.get_object('paramsListStore')
        self.cboParams = ui.get_object('cboParams')
        self.spnFrom = ui.get_object('spnFrom')
        self.spnFrom.set_adjustment(self.create_adj(0))
        self.spnTo = ui.get_object('spnTo')
        self.spnTo.set_adjustment(self.create_adj(255))
        self.lblBestPrecision = ui.get_object('lblBestPrecision')
        self.lblBestNoise = ui.get_object('lblBestNoise')
        self.lblOverallBest = ui.get_object('lblOverallBest')
        self.imgGraphEval = ui.get_object('imgGraphEval')
        
        self.test = None
        self.chain = None
        
    def init_window(self):
        pass
    
    def msg_on_no_filterchain(self):
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR, 
                                   Gtk.ButtonsType.OK, 
                                   "You must select a filterchain file.")
        result = dialog.run()
        dialog.destroy()
        return result
    
    def msg_on_no_test_folder(self):
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR, 
                                   Gtk.ButtonsType.OK, 
                                   "You must select a test folder.")
        result = dialog.run()
        dialog.destroy()
        return result
    
    def msg_on_no_test_images(self):
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR, 
                            Gtk.ButtonsType.OK, 
                            "There are no image map files in the test folder.")
        result = dialog.run()
        dialog.destroy()
        return result
    
    def create_adj(self, init_val):
        return Gtk.Adjustment(init_val, 0, 65535, 1, 10, 0)

    def fill_labels(self, test):
        self.lblNbImages.set_text(str(test.total_images()))
        noise = str(round(test.avg_noise() * 100.0, 2)) + '%'
        self.lblNoise.set_text(noise)
        precision = str(round(test.avg_precision() * 100.0, 2)) + '%'
        self.lblPrecision.set_text(precision)

    def fill_image_list(self, images):
        self.imageListStore.clear()
        for i in xrange(len(images)):
            self.imageListStore.append([images.keys()[i], i])
        if len(images) > 0:
            self.lstImage.set_cursor(0)
        
    def fill_paramsListStore(self, chain):
        self.paramsListStore.clear()
        for fname, params in filterchain.params_list(chain):
            for name, value in params:
                if filterchain.isnumeric(value) and not isinstance(value, bool):
                    self.paramsListStore.append(
                                [fname, name, fname + ' - ' + name, value])
        self.cboParams.set_active(0)
        
    def validate_folder(self, folder):
        if folder == '':
            self.msg_on_no_test_folder()
            return False
        else:
            return True
        
    def validate_filterchain(self, chain):
        if chain == '':
            self.msg_on_no_filterchain()
            return False
        else:
            return True
    
    def validate_image_number(self, image_number):
        if image_number == 0:
            self.msg_on_no_test_images()
            return False
        else:
            return True
    
    def on_btnExecPrecision_clicked(self, widget):
        folder = self.txtTestFolder.get_text()
        chain = self.txtFilterchain.get_text()
        if (self.validate_folder(folder) and 
            self.validate_filterchain(chain)):
            
            self.test = LineTest(folder, self.chain)
            image_number = self.test.total_images()
            if self.validate_image_number(image_number):
                self.test.launch()
                self.fill_labels(self.test)
                self.fill_image_list(self.test.testable_images)
            
    def on_btnExecParams_clicked(self, widget):
        pass
    
    def on_btnClear_clicked(self, widget):
        self.txtFilterchain.set_text('')
        self.txtTestFolder.set_text('')
        self.lblNoise.set_text('0%')
        self.lblPrecision.set_text('0%')
        self.lblNbImages.set_text('0')
        self.imageListStore.clear()
        self.test = None
        self.chain = None
        
    def on_btnOpenFilterchain_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Choose a filterchain file", None,
                                   Gtk.FileChooserAction.OPEN,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OK, Gtk.ResponseType.OK))
        ff = Gtk.FileFilter()
        ff.set_name('Filterchain')
        ff.add_pattern('*.filterchain')
    
        dialog.set_filter(ff)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.txtFilterchain.set_text(dialog.get_filename())
            self.chain = filterchain.read(self.txtFilterchain.get_text())
            self.fill_paramsListStore(self.chain)
        dialog.destroy()

    def on_btnOpenTestFolder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Choose an image folder", None,
                                   Gtk.FileChooserAction.SELECT_FOLDER,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OK, Gtk.ResponseType.OK))    
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.txtTestFolder.set_text(dialog.get_filename())
        dialog.destroy()

    def on_lstImage_cursor_changed(self, widget):
        index = tree_selected_index(self.lstImage)
        if index >= 0:
            file_name = self.imageListStore[index][0]
            self.imgExample.set_from_pixbuf(numpy_to_pixbuf(
                                        self.test.example_image(file_name)))
            self.imgOriginal.set_from_pixbuf(numpy_to_pixbuf(
                                        self.test.original_image(file_name)))
