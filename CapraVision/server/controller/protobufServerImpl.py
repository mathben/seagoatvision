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

"""
Description : Server Service implementation using vServer_pb2, generate by .proto file
Authors: Mathieu Benoit (mathben963@gmail.com)
Date : October 2012
"""

# Import required RPC modules
from CapraVision.proto import server_pb2

import facadeServer

class ProtobufServerImpl(server_pb2.CommandService):
    def __init__(self, *args, **kwargs):
        server_pb2.CommandService.__init__(self, *args, **kwargs)
        
        self.facadeServer = facadeServer.FacadeServer()
    
    def GetFilterList(self, controller, request, done):
        # Create a reply
        response = server_pb2.GetFilterListResponse()
        for filter in self.facadeServer.getFilter():
            response.filters.append(filter) 
        
        # We're done, call the run method of the done callback
        done.run(response)
        
