#! /usr/bin/env python

#    Copyright (C) 2012  Octets - octets.etsmtl.ca
#
#    This file is part of SeaGoatVision.
#
#    SeaGoatVision is free software: you can redistribute it and/or modify
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

import cv2
import thread
import numpy as np
try:
    #import pygame
    import pygame.camera
    #from pygame.locals import *
except:
    pass

from SeaGoatVision.server.media.media_streaming import Media_streaming
from SeaGoatVision.server.core.configuration import Configuration
from SeaGoatVision.commons.param import Param
from SeaGoatVision.commons import log

logger = log.get_logger(__name__)

class Pygame_cam(Media_streaming):
    """Return images from the webcam."""

    def __init__(self, config):
        # Go into configuration/template_media for more information
        self.config = Configuration()
        self.own_config = config
        super(Pygame_cam, self).__init__()
        self.media_name = config.name
        self.run = True
        self.video = None
        pygame.init()
        pygame.camera.init()

        self._create_params()
        self.deserialize(self.config.read_media(self.get_name()))
        self.cam = None
        self.isOpened = True
        self.image = None

    def _create_params(self):
        self.dct_params = {}

        default_resolution_name = "800x600"
        self.dct_resolution = {default_resolution_name:(800, 600),
                               "320x240":(320, 240),
                               "640x480":(640, 480),
                               "1024x768":(1024, 768),
                               "1280x960":(1280, 960)}
        param = Param("resolution", default_resolution_name, lst_value=self.dct_resolution.keys())
        param.add_notify_reset(self.reset_property_param)
        self.dct_params["resolution"] = param

        default_fps_name = "30"
        self.dct_fps = {default_fps_name:30, "15":15, "7.5":7.5}
        param = Param("fps", default_fps_name, lst_value=self.dct_fps.keys())
        param.add_notify_reset(self.reset_property_param)
        self.dct_params["fps"] = param

    def serialize(self):
        return {"resolution":self.dct_params.get("resolution").get(), "fps":self.dct_params.get("fps").get()}

    def deserialize(self, data):
        if not data:
            return False
        if type(data) is not dict:
            log.print_function(logger.error, "Wrong format data, suppose to be dict into camera %s" % self.get_name())
            return False
        res = data.get("resolution", None)
        if res:
            self.dct_params.get("resolution").set(res)
        res = data.get("fps", None)
        if res:
            self.dct_params.get("fps").set(res)
        return True

    def open(self):
        try:
            shape = self.dct_resolution[self.dct_params.get("resolution").get()]
            fps = self.dct_fps[self.dct_params.get("fps").get()]
            self.video = pygame.camera.Camera(self.own_config.path, shape)
            self.video.start()
            self.thread_image = True
            thread.start_new_thread(self.update_image, ())
        except Exception as e:
            log.printerror_stacktrace(logger, "Open camera %s: %s" % (self.get_name(), e))
            return False
        # call open when video is ready
        return Media_streaming.open(self)

    def update_image(self):
        while self.thread_image:
            image_surface = self.video.get_image()
            image = pygame.surfarray.pixels3d(image_surface)
            image = np.rot90(image, 3)
            copy_image = np.zeros(image.shape, np.float32)
            copy_image = cv2.cvtColor(image, cv2.cv.CV_BGR2RGB, copy_image)
            self.image = copy_image

    def next(self):
        return self.image

    def close(self):
        Media_streaming.close(self)
        self.thread_image = False
        # TODO add semaphore?
        self.video.stop()
        self.isOpened = False
        return True

    def get_properties_param(self):
        return self.dct_params.values()

    def update_property_param(self, param_name, value):
        param = self.dct_params.get(param_name, None)
        if not param:
            return False
        param_value = param.get()
        if value == param_value:
            return True
        param.set(value)
        self.reload()
        return True

    def reset_property_param(self, param_name, value):
        self.reload()
        return True