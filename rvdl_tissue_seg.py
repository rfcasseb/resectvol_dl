# --------------------------------------------------------------
# Function to segment brain image into tissues using spm New 
# Segment function via nipype library.
# --------------------------------------------------------------
# Call example
# python rvdl_tissue_seg.py $brn_path/post.nii
# --------------------------------------------------------------
# =========================================================================
# Raphael Fernandes Casseb & Brunno Machado de Campos
# University of Campinas, 2025
#
# Copyright (c) 2025
# Raphael Fernandes Casseb & Brunno Machado de Campos
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# =========================================================================
 
# According to this, spm:
# https://github.com/nipy/nipype/issues/2342

import sys
import nipype.interfaces.spm as spm
# import datetime

# Brain Extract
# ---------------------------------------------------------------
# start_time = datetime.datetime.now()
seg = spm.NewSegment()
seg.inputs.channel_files = sys.argv[1]
seg.inputs.channel_info = (0.0001, 60, (True, True))
seg.run() 
# end_time = datetime.datetime.now()
# print(f'Time-elapsed:{end_time-start_time}')