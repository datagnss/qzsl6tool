#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# libgale6.py: library for Galileo E6B message processing
# A part of QZS L6 Tool, https://github.com/yoronneko/qzsl6tool
#
# Copyright (c) 2023 Satoshi Takahashi, all rights reserved.
#
# Released under BSD 2-clause license.
#
# References:
# [1] Europe Union Agency for the Space Programme,
#     Galileo High Accuracy Service Signal-in-Space Interface Control
#     Document (HAS SIS ICD), Issue 1.0 May 2022.

import argparse
import sys
import bitstring
import galois
import numpy as np
import libcolor
import libssr

GF = galois.GF(256)
g = np.array([  # Reed-Solomon generator matrix
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[19,143,180,59,221,29,49,45,231,9,73,73,159,2,158,136,212,218,14,113,215,20,187,55,137,181,203,113,97,135,14,251],
[27,27,1,50,255,109,251,156,148,151,85,21,74,116,250,77,60,203,113,196,213,23,202,125,31,252,90,1,176,226,44,252],
[98,153,190,38,223,28,28,149,170,219,41,235,236,175,113,182,239,31,74,241,127,121,207,137,205,70,88,218,250,129,99,5],
[95,235,199,105,168,182,233,133,201,135,171,89,50,230,115,227,21,122,41,226,93,59,20,36,30,150,134,240,34,91,183,83],
[172,171,163,123,27,81,14,251,24,56,15,35,244,148,24,35,96,195,47,232,148,85,117,91,39,5,74,71,104,116,14,128],
[117,108,167,111,201,61,244,13,5,236,75,124,11,233,60,127,101,117,144,13,51,70,138,247,188,171,120,104,141,220,39,86],
[243,8,122,204,147,89,112,127,204,217,20,179,8,167,203,254,95,38,22,249,215,127,101,46,99,252,183,17,8,122,191,32],
[90,195,11,73,110,20,55,185,206,241,12,193,185,72,141,27,97,29,251,144,6,109,129,203,222,64,164,49,173,37,167,169],
[164,41,177,10,34,58,123,165,122,70,108,145,240,246,208,134,248,114,237,129,149,218,70,63,105,5,184,222,9,255,213,153],
[211,255,215,20,146,60,12,202,1,95,234,192,175,223,81,99,59,136,191,82,138,174,112,1,21,14,137,7,4,238,50,246],
[220,94,230,67,248,163,186,77,68,20,1,180,150,94,127,36,154,47,101,114,172,174,172,248,130,250,55,68,17,106,3,123],
[110,20,220,172,53,110,224,20,10,192,59,46,159,96,14,203,214,144,215,141,13,190,175,232,55,123,104,223,79,38,146,169],
[164,29,102,221,199,97,1,114,215,130,93,166,31,208,248,5,40,197,96,173,136,209,149,17,74,236,131,18,231,29,214,172],
[251,94,49,176,56,250,251,10,237,114,111,176,78,90,148,97,69,174,3,178,4,16,151,192,36,202,212,81,210,20,219,216],
[116,79,18,201,172,40,33,232,54,187,32,61,5,227,55,18,43,107,202,220,141,66,224,166,158,176,61,11,143,232,112,47],
[187,194,174,69,228,144,68,94,189,124,254,101,65,91,176,76,117,203,236,169,202,251,11,110,242,80,181,94,162,92,111,54],
[29,150,209,144,66,224,111,137,81,38,230,100,15,45,7,31,208,240,210,18,111,85,199,64,247,215,164,75,231,34,69,82],
[191,102,106,86,63,166,105,80,243,169,231,39,86,171,77,223,72,220,171,98,179,115,160,191,202,89,192,20,178,54,121,137],
[254,252,23,88,159,236,167,50,34,70,225,175,28,89,25,150,163,25,241,87,152,213,166,176,237,50,249,60,144,205,27,81],
[138,9,193,221,141,92,54,239,124,193,92,251,33,190,134,68,160,220,80,210,146,184,240,135,188,129,101,218,102,213,132,199],
[184,160,40,202,31,235,178,121,225,205,231,122,61,178,191,195,55,13,2,41,245,69,128,182,5,90,7,28,79,58,11,43],
[247,8,171,147,180,87,67,121,151,143,177,155,64,107,163,222,211,152,178,184,68,211,218,210,252,37,84,189,44,186,133,134],
[31,50,155,253,213,220,84,174,239,85,87,105,214,81,160,211,90,32,239,171,171,238,177,234,36,233,216,77,44,173,205,253],
[113,18,35,135,205,43,156,23,127,169,162,160,15,49,202,100,165,163,175,30,199,19,141,197,211,200,134,41,215,154,34,31],
[204,239,127,208,89,187,30,192,37,152,221,214,211,49,93,9,93,38,25,9,6,86,219,250,25,161,185,32,98,177,32,121],
[72,7,24,67,1,245,154,234,84,179,37,96,222,33,64,228,78,254,194,19,197,60,60,241,58,151,184,179,233,70,85,97],
[253,151,182,118,101,136,118,241,195,26,152,14,225,28,193,165,140,82,138,36,216,2,152,228,117,234,180,94,11,25,50,148],
[20,35,254,1,198,250,222,43,98,131,180,54,101,212,227,212,85,247,217,50,117,7,116,145,101,136,176,12,83,1,146,170],
[145,235,144,178,16,181,198,59,220,241,197,242,187,44,243,109,86,53,21,48,83,149,252,147,181,124,48,89,151,149,227,188],
[214,115,72,209,6,224,24,39,114,233,248,204,31,222,125,2,236,241,19,132,104,150,172,254,222,170,104,161,199,252,179,230],
[241,67,229,75,108,250,81,179,127,247,83,66,159,206,107,96,58,217,252,157,139,17,235,115,5,174,191,230,233,49,241,241],
[165,246,113,208,142,14,235,211,178,85,75,239,238,96,147,129,143,18,30,123,124,195,21,230,104,198,220,56,202,53,246,99],
[219,121,50,105,81,61,239,218,41,238,236,242,77,40,161,123,92,58,122,26,3,147,12,163,109,207,110,216,66,41,93,220],
[56,105,223,38,38,53,34,72,93,91,133,135,1,232,7,61,70,61,102,124,94,21,181,225,227,23,51,104,159,94,117,98],
[200,107,25,252,122,136,229,62,85,8,171,117,186,197,183,103,52,41,91,19,211,165,97,52,227,241,116,70,115,251,56,164],
[99,62,142,10,191,175,135,155,202,184,151,52,17,239,5,26,201,44,159,38,76,235,82,145,61,162,223,9,169,204,77,189],
[197,14,41,244,99,82,51,75,53,246,248,215,70,118,32,124,79,180,4,127,169,157,105,103,85,151,125,63,246,69,228,179],
[55,161,79,12,207,40,253,100,230,119,111,97,76,61,94,122,5,74,200,112,206,160,19,75,142,167,222,9,180,99,57,177],
[17,80,149,28,144,190,229,240,26,182,124,100,217,51,52,9,182,169,42,94,114,239,69,95,173,11,101,72,64,50,3,135],
[12,91,119,248,135,229,140,37,129,209,39,237,182,202,102,204,89,159,208,66,154,204,54,66,32,13,61,13,184,70,75,128],
[117,204,87,187,74,161,64,143,219,117,162,84,197,171,98,1,138,76,204,242,153,72,19,180,165,172,112,31,199,12,21,19],
[24,225,130,141,144,160,197,221,109,80,74,157,237,227,1,143,161,216,190,28,103,248,231,29,74,248,192,160,226,203,254,14],
[242,17,183,221,223,54,147,94,222,19,137,147,116,241,4,34,163,217,140,42,34,191,244,240,48,18,110,84,212,155,159,85],
[198,3,198,145,91,104,40,111,171,25,48,170,91,222,108,67,99,147,168,118,148,82,76,9,226,178,78,148,151,183,234,136],
[237,10,198,207,133,149,88,94,250,23,24,49,14,86,242,63,235,232,176,37,91,230,60,107,210,175,217,195,113,111,148,57],
[252,70,251,156,71,58,104,35,181,22,29,18,45,124,115,246,91,204,171,171,10,8,109,87,86,26,6,194,111,15,44,249],
[61,247,189,11,255,205,190,159,73,215,216,211,50,194,165,173,247,237,123,131,188,226,189,197,112,84,126,46,193,255,184,53],
[40,156,37,206,118,220,97,4,164,201,150,153,5,88,33,143,80,1,230,22,33,31,14,175,218,151,224,19,52,213,244,149],
[7,121,65,169,163,244,187,17,112,237,46,113,109,50,57,188,171,241,132,47,144,234,210,48,167,146,6,41,127,185,80,151],
[33,85,209,187,99,27,241,145,182,43,152,91,166,94,114,169,45,163,104,175,26,115,76,130,55,152,136,45,135,225,32,216],
[116,149,25,41,167,115,192,226,173,224,121,202,238,11,51,244,227,3,199,183,144,92,131,125,220,163,111,87,243,189,133,212],
[160,202,250,200,192,43,249,18,14,151,249,96,181,91,160,155,39,28,47,110,5,38,203,203,1,103,73,198,63,163,145,49],
[100,7,242,101,230,151,67,247,146,170,239,129,240,215,250,144,17,158,47,155,183,246,28,5,202,8,216,253,69,13,144,119],
[186,166,166,145,230,236,133,44,96,122,206,139,96,30,65,96,251,202,46,177,105,85,144,33,232,28,135,70,64,24,189,122],
[125,253,144,215,58,109,158,6,140,237,28,168,63,148,208,125,70,43,60,183,25,111,239,227,103,164,69,30,44,240,238,236],
[79,231,215,32,107,20,43,26,230,83,183,70,84,250,132,244,30,68,74,255,253,232,200,251,43,161,44,134,187,133,145,204],
[21,229,206,84,62,194,60,102,75,4,220,56,176,209,192,112,8,94,248,15,74,182,177,114,195,206,113,105,159,63,57,165],
[112,108,180,230,202,246,252,111,117,175,210,10,195,231,143,229,10,202,230,244,135,102,250,118,242,55,43,125,231,167,135,71],
[205,154,65,115,150,138,189,176,159,48,250,135,228,77,78,173,208,178,71,189,8,130,129,62,19,152,204,112,34,15,42,112],
[195,133,16,131,217,207,15,17,168,72,182,124,156,4,38,75,208,55,40,147,80,134,226,57,75,233,92,24,247,205,149,27],
[128,91,2,15,14,219,62,231,152,107,5,251,73,170,42,255,5,28,181,87,240,145,152,73,251,215,147,35,202,183,79,5],
[95,9,5,213,129,103,46,167,187,181,27,117,34,67,118,184,92,144,42,29,251,180,252,115,222,160,23,59,219,107,129,127],
[34,145,97,163,240,99,224,52,91,27,163,13,24,220,81,216,61,25,80,27,25,185,99,100,162,201,57,38,169,202,171,224],
[155,178,152,248,234,66,116,165,4,232,10,178,59,197,10,91,34,238,48,229,220,24,121,14,142,75,92,140,53,106,227,201],
[74,184,197,204,104,42,159,160,168,203,23,245,157,180,35,108,4,247,100,221,252,211,44,40,161,48,91,177,109,16,224,231],
[226,80,154,253,172,137,170,25,31,36,56,228,57,78,159,182,128,235,244,155,5,145,21,196,90,100,238,164,152,28,19,89],
[18,25,164,149,142,135,198,151,60,180,76,80,230,139,21,246,110,97,210,120,168,133,5,145,244,247,37,98,209,145,37,68],
[248,116,245,46,159,233,159,253,83,98,58,194,2,110,157,178,162,165,254,26,224,145,178,152,114,92,76,237,158,173,14,194],
[231,91,11,41,98,144,242,73,175,207,52,108,221,155,179,74,98,154,77,47,145,115,196,31,141,207,26,157,128,99,69,145],
[75,176,108,107,23,148,51,54,134,194,17,234,222,226,184,52,25,140,39,93,210,10,104,38,9,43,85,10,104,43,222,237],
[92,94,46,231,10,36,227,154,49,80,209,2,137,25,108,20,131,193,227,149,192,55,22,75,103,122,104,231,206,70,68,7],
[121,214,117,143,206,89,179,32,21,14,178,51,248,135,228,243,2,191,235,169,138,172,49,147,211,75,49,34,221,124,108,159],
[185,39,183,74,227,158,201,236,236,6,9,181,104,219,67,64,140,148,86,111,106,201,187,196,168,45,71,181,163,15,149,111],
[15,111,192,134,62,204,46,57,198,220,244,251,221,182,220,133,4,232,180,36,154,117,97,116,109,32,152,53,121,42,47,255],
[87,1,11,170,17,250,238,55,59,146,185,145,190,62,12,21,70,84,123,167,251,10,125,123,66,246,196,139,109,220,185,22],
[71,74,17,6,15,146,107,234,137,157,221,246,241,146,72,115,22,129,144,3,158,222,200,152,18,68,90,188,142,192,24,146],
[126,156,188,60,66,222,98,216,17,255,152,216,248,200,14,74,65,139,46,19,154,57,21,115,8,118,158,217,234,177,111,160],
[47,142,147,67,44,227,21,168,151,216,89,62,250,165,74,185,147,22,5,138,55,242,24,57,100,167,83,58,175,115,63,33],
[73,144,57,155,60,182,188,241,254,163,68,197,171,184,17,18,242,11,197,242,162,153,183,129,64,242,52,164,231,5,160,210],
[202,242,96,114,134,254,154,128,117,242,17,246,223,18,112,174,3,235,3,87,136,108,179,77,236,98,152,166,151,130,13,52],
[59,228,148,40,210,184,99,13,92,252,250,25,191,183,111,210,135,47,238,31,34,63,59,150,219,190,29,132,221,4,135,219],
[65,3,105,33,78,229,48,7,5,17,117,115,16,20,101,108,249,218,89,162,68,88,31,83,78,141,9,81,249,115,114,99],
[219,157,199,113,160,253,4,1,253,89,168,204,209,214,213,141,177,76,178,93,218,171,151,169,216,233,37,13,43,26,27,88],
[1,175,221,243,223,150,131,20,195,95,120,137,81,97,19,52,129,138,123,79,185,78,132,36,16,192,99,216,25,165,45,183],
[123,99,4,20,155,224,253,96,2,165,255,216,84,34,11,83,58,203,206,214,133,224,22,122,211,12,130,206,202,170,225,179],
[55,31,34,33,47,208,79,170,205,64,60,102,67,47,10,81,42,63,183,186,103,140,110,52,147,33,69,246,69,95,214,180],
[78,217,117,166,51,55,232,219,136,176,59,71,7,54,250,207,62,19,105,137,20,2,4,201,69,77,35,123,71,98,9,88],
[1,58,153,65,8,5,73,248,25,42,145,26,218,183,243,27,195,5,36,148,109,128,45,183,112,93,199,222,111,201,85,165],
[112,120,107,177,223,192,59,26,235,253,252,71,225,141,233,214,97,1,189,40,28,65,204,234,55,132,184,203,80,87,113,43],
[247,192,115,208,207,151,104,240,244,133,129,128,125,183,156,136,198,206,190,7,69,58,222,158,160,23,138,2,251,165,232,252],
[98,117,101,84,61,44,230,6,198,187,59,63,121,152,178,208,42,229,79,62,188,233,226,157,46,249,179,10,249,202,36,193],
[210,77,203,244,98,21,100,71,96,65,54,182,156,230,250,224,97,97,31,13,209,19,108,22,14,81,255,241,196,144,48,171],
[130,162,74,188,56,12,24,172,87,250,78,57,164,215,95,252,182,219,141,135,187,37,83,188,187,162,34,103,11,133,124,229],
[196,155,245,4,123,227,238,196,192,201,155,47,214,115,221,199,165,240,196,144,236,254,136,213,193,9,247,63,140,105,154,46],
[168,253,206,153,244,90,190,188,118,131,197,151,204,138,190,46,116,159,121,214,81,142,12,49,8,186,199,229,247,216,224,39],
[35,18,213,92,18,32,163,180,130,116,180,242,103,130,93,241,167,10,104,181,54,135,118,39,89,7,169,11,99,104,47,45],
[157,150,134,244,214,20,46,134,50,218,163,99,173,61,240,43,35,238,145,233,16,104,165,150,124,224,137,40,96,163,243,130],
[83,94,239,60,225,202,211,119,171,212,59,66,104,180,180,154,216,159,161,81,129,234,220,73,126,135,22,73,32,199,236,64],
[180,51,88,137,101,242,22,92,8,209,99,140,86,232,224,9,185,92,56,176,178,232,11,157,180,56,55,7,44,122,96,192],
[193,20,57,242,98,80,139,154,221,134,21,167,176,203,20,58,108,40,168,11,136,9,214,200,135,126,245,4,168,194,142,20],
[97,223,113,66,240,219,163,213,247,105,91,200,228,152,156,102,140,2,240,50,129,133,160,93,174,246,89,111,195,22,26,78],
[70,8,143,72,73,69,52,183,169,243,7,53,53,120,43,2,105,112,241,117,239,48,104,246,141,176,208,220,126,224,229,157],
[159,27,28,198,131,35,183,49,168,168,102,146,77,18,157,130,200,86,133,151,5,132,76,243,194,4,55,182,159,191,21,13],
[199,26,140,14,238,2,67,91,6,205,170,100,199,87,74,59,207,195,16,130,205,225,88,2,88,88,210,48,97,114,249,174],
[221,62,67,44,76,233,250,18,23,177,178,213,175,134,50,222,206,224,25,32,152,125,204,99,56,175,235,226,50,129,168,28],
[249,207,146,253,136,29,143,209,20,235,30,29,26,151,85,116,134,62,72,44,92,53,101,226,57,136,158,222,10,192,41,227],
[174,229,7,70,206,29,89,189,213,188,33,212,151,193,254,218,239,38,5,110,143,97,37,81,142,18,93,184,110,93,251,91],
[52,86,100,126,146,223,48,62,75,108,70,219,245,33,187,154,183,167,3,107,238,39,158,207,110,84,216,51,15,116,120,71],
[205,222,123,163,14,210,148,124,206,14,57,19,53,123,136,153,175,15,42,88,151,235,192,90,170,4,175,131,108,231,249,143],
[148,139,48,211,158,147,117,33,102,77,237,218,77,54,170,68,39,24,6,237,106,137,131,98,25,203,36,104,92,38,238,241],
[165,147,185,5,22,252,130,247,32,76,241,81,118,178,107,64,171,15,223,129,12,34,141,142,121,218,185,163,68,128,225,124],
[23,231,58,82,90,211,40,239,63,155,129,60,128,142,31,64,164,157,221,125,225,114,37,76,217,172,3,27,146,193,82,144],
[88,207,100,97,177,177,65,193,199,91,12,22,17,189,51,16,199,144,46,188,87,110,210,240,211,202,253,98,143,190,114,1],
[19,215,123,95,188,172,128,108,38,206,18,69,137,19,35,187,196,29,158,95,107,67,213,229,121,102,1,140,3,8,176,137],
[254,80,166,73,150,111,173,219,30,147,134,90,126,134,161,248,199,149,48,98,165,13,150,197,183,129,198,253,8,124,37,152],
[192,42,26,56,12,149,104,49,152,50,118,99,251,83,191,154,145,109,86,254,190,138,28,230,102,101,198,8,70,104,191,253],
[113,205,59,6,8,242,213,43,224,222,197,129,5,28,200,123,236,104,226,167,146,6,233,104,223,138,10,55,146,240,231,109],
[41,164,95,124,213,29,32,127,210,194,190,165,202,223,58,3,138,33,84,114,225,165,197,72,206,32,180,154,57,8,204,102],
[132,124,62,144,115,15,9,136,217,163,11,119,222,6,194,64,125,170,127,248,166,74,7,152,84,50,72,24,24,123,86,214],
[134,57,102,153,222,197,231,129,183,241,40,128,43,111,140,103,38,43,154,52,249,56,182,33,235,152,83,3,178,91,75,9],
[139,5,68,152,226,43,97,191,13,246,202,19,147,57,117,48,93,98,85,68,21,77,50,36,148,159,69,141,77,121,37,59],
[218,35,129,104,183,103,180,64,135,243,110,82,44,229,61,124,225,211,61,172,216,110,173,55,22,43,189,188,227,32,38,163],
[26,166,237,51,2,49,255,9,59,85,142,19,204,119,216,15,196,197,79,10,236,140,159,216,166,123,78,138,105,238,188,120],
[91,94,229,234,63,179,33,38,122,164,161,122,132,60,152,233,156,189,47,52,17,194,93,130,145,157,169,53,34,202,4,6],
[106,94,193,127,30,113,21,207,78,76,15,10,31,136,95,143,43,122,153,20,252,105,127,239,147,8,29,146,110,23,238,36],
[22,92,183,30,142,237,219,104,197,87,160,227,70,87,224,149,103,38,159,198,144,22,65,13,1,94,91,66,183,101,242,51],
[66,178,17,94,151,227,231,143,59,115,189,74,80,32,215,221,170,119,9,201,172,75,71,225,3,127,106,13,3,150,74,255],
[87,76,214,123,201,83,193,254,141,111,22,216,15,179,154,30,30,250,228,26,22,60,67,93,215,152,155,121,85,166,5,115],
[246,147,7,89,171,183,133,26,210,65,50,75,127,233,103,26,2,138,114,163,147,164,140,162,174,239,28,220,93,46,46,36],
[22,192,122,216,168,88,29,248,16,203,173,222,7,55,129,173,242,15,111,45,39,121,140,254,76,99,188,67,249,86,203,243],
[131,18,135,57,186,240,43,197,42,40,229,131,81,252,75,102,247,115,212,10,127,71,22,239,234,248,154,217,173,54,141,178],
[36,104,231,153,223,236,110,81,143,97,248,53,135,40,74,153,203,40,1,209,108,98,114,3,143,173,122,159,51,191,68,35],
[111,152,170,153,65,127,209,208,212,169,111,246,131,193,189,31,103,250,231,20,74,234,76,133,117,110,181,111,128,138,112,66],
[146,12,235,186,103,104,193,4,124,188,140,74,193,7,180,13,137,74,65,20,68,11,96,99,119,68,85,70,200,201,49,183],
[123,240,167,34,210,88,3,34,18,26,28,44,151,178,109,244,3,195,14,236,222,29,83,158,148,107,6,248,84,123,141,175],
[206,13,29,60,189,200,145,127,137,172,44,42,120,212,73,113,213,246,23,79,33,122,139,95,45,214,19,71,155,51,175,147],
[109,154,79,11,165,113,9,15,99,246,224,96,187,67,214,195,151,146,87,229,1,146,10,7,70,252,199,225,112,35,146,236],
[79,247,176,255,183,139,55,141,239,188,172,186,156,126,83,242,160,149,243,148,175,240,53,30,207,128,116,4,68,217,66,176],
[2,167,119,216,190,219,119,23,20,182,254,238,157,225,233,140,234,214,251,20,65,154,174,78,113,255,137,147,44,69,183,7],
[121,136,140,214,241,237,76,180,152,43,84,28,20,147,28,118,154,214,252,177,11,45,156,43,214,93,180,195,169,158,111,108],
[58,35,174,240,216,249,14,203,170,179,2,125,200,204,43,95,83,141,228,29,32,40,85,10,4,156,168,85,172,180,172,21],
[114,171,242,238,47,124,59,125,65,23,39,150,161,226,5,209,61,231,91,15,64,57,58,233,229,192,112,67,243,149,98,151],
[33,32,3,8,36,151,121,17,218,26,98,82,65,146,162,149,64,53,126,112,58,163,159,106,238,218,218,91,237,109,12,234],
[37,190,149,41,64,68,119,19,153,51,235,147,203,136,225,145,52,164,112,134,242,179,185,57,179,177,210,34,165,113,40,14],
[242,44,232,202,123,230,119,236,16,231,234,50,122,215,111,194,189,76,240,228,184,42,191,174,20,235,39,70,86,220,37,131],
[64,190,225,105,2,122,16,3,38,255,79,66,166,97,192,141,229,219,13,65,91,86,37,100,207,90,214,150,47,118,157,109],
[41,149,44,166,186,23,168,186,250,4,159,47,9,124,71,11,124,40,231,157,7,108,149,132,194,48,100,70,152,181,74,28],
[249,59,57,146,2,235,113,131,188,6,171,48,224,49,175,1,83,140,128,210,225,170,116,187,222,114,1,81,174,106,29,1],
[19,118,143,2,79,31,218,92,100,181,79,226,175,226,175,39,213,137,130,241,5,245,17,67,50,107,185,112,48,41,100,230],
[241,134,224,140,191,179,174,113,4,225,15,245,177,126,87,178,31,224,132,12,254,124,136,206,184,66,126,55,56,198,36,38],
[48,196,26,73,218,118,123,137,168,15,159,113,154,253,55,144,239,187,25,57,59,60,63,148,47,2,154,195,208,32,63,18],
[11,43,62,251,191,45,35,203,140,42,121,233,87,190,201,82,228,103,71,184,123,78,40,6,227,199,165,59,95,91,220,223],
[13,53,76,103,206,252,97,243,120,229,154,201,166,244,46,208,14,246,41,210,152,81,184,156,192,91,123,48,223,215,21,243],
[131,9,114,15,5,150,143,185,33,64,203,180,70,93,136,201,138,143,45,76,128,248,62,219,136,116,162,30,222,16,12,108],
[58,217,47,14,1,13,117,8,167,10,105,226,96,158,229,203,236,157,189,204,221,163,128,168,244,194,129,67,113,195,34,118],
[169,119,204,119,80,22,46,55,120,70,39,68,156,140,150,247,116,237,35,82,233,43,126,138,204,151,134,110,159,171,125,51],
[66,13,58,37,254,61,28,122,100,206,172,205,247,250,12,171,200,100,194,117,56,50,122,222,132,178,163,208,47,190,132,112],
[195,10,135,248,143,167,184,176,98,179,72,42,214,23,145,9,214,47,254,22,152,182,82,194,171,126,118,119,87,192,36,181],
[93,162,212,56,55,138,174,1,117,22,129,122,212,161,92,220,178,53,119,177,111,233,133,194,58,192,183,57,167,247,152,81],
[138,170,159,30,237,244,80,230,79,150,12,155,244,118,126,1,234,205,124,84,116,79,204,164,206,86,151,148,99,226,190,68],
[248,236,70,21,20,138,236,107,34,17,24,130,201,124,96,217,85,33,82,180,204,77,120,81,71,102,237,95,104,31,125,89],
[18,3,24,73,102,63,197,209,78,137,121,112,128,123,39,9,1,180,24,222,135,76,217,252,97,234,39,97,42,97,38,42],
[228,45,188,152,234,51,166,35,216,41,188,76,213,212,244,206,205,116,5,211,100,181,104,188,63,244,47,236,48,88,208,80],
[153,156,164,77,144,52,216,195,138,50,122,239,93,117,149,33,44,104,51,87,193,80,43,126,57,230,104,125,215,242,31,247],
[207,155,49,11,124,188,131,180,170,150,37,109,38,174,75,104,12,226,139,143,126,241,233,148,116,99,20,212,10,62,17,173],
[232,186,3,220,51,92,23,165,204,6,50,129,26,97,116,90,252,80,42,40,241,242,12,139,40,65,144,183,117,126,246,228],
[215,126,89,118,198,245,143,230,46,91,46,26,241,207,245,100,215,96,65,70,148,160,228,189,127,47,223,252,61,144,111,95],
[120,41,21,204,241,163,28,92,171,179,152,237,125,79,247,139,126,208,125,246,189,108,137,210,156,75,238,104,210,1,141,24],
[181,108,111,71,59,212,1,131,225,115,37,14,100,77,222,171,164,193,64,145,241,64,162,123,150,194,113,2,25,6,145,13],
[199,48,251,125,111,186,180,237,180,132,113,39,91,126,21,120,230,175,135,71,203,21,156,236,208,12,20,118,213,244,64,42],
[228,248,143,123,222,58,35,82,228,211,177,68,130,15,241,252,188,147,30,76,253,249,49,249,47,69,201,223,39,167,69,54],
[29,201,235,177,124,218,197,238,93,127,73,43,46,238,83,94,96,57,138,224,138,98,197,122,96,10,177,55,102,167,190,120],
[91,89,138,236,189,205,202,28,157,194,139,189,188,222,1,98,205,25,211,241,251,164,179,216,51,91,216,202,159,197,77,4],
[76,93,179,102,191,201,9,126,167,185,251,178,251,180,156,27,21,130,33,10,138,171,114,111,198,221,80,1,83,185,253,134],
[31,137,206,229,32,215,202,228,232,101,97,35,255,234,127,236,159,230,245,56,25,32,201,66,153,211,32,73,144,210,206,133],
[42,86,219,213,217,111,135,80,70,49,102,98,210,232,158,138,9,31,131,127,79,143,146,160,50,78,110,170,123,133,183,166],
[69,223,198,190,49,54,2,163,119,185,60,107,37,131,9,62,145,184,181,28,147,95,19,12,166,4,235,241,135,215,47,217],
[103,126,39,5,127,60,220,60,120,40,162,39,65,138,112,7,160,101,210,27,244,193,20,21,219,135,56,69,78,58,189,32],
[90,87,125,20,167,248,82,21,141,69,253,119,45,1,160,160,152,226,184,84,228,78,63,186,229,248,223,190,249,99,231,171],
[130,42,80,10,216,201,245,154,5,23,74,242,101,102,184,166,246,34,14,32,226,16,14,239,23,73,139,71,68,184,143,50],
[81,169,211,130,94,168,242,140,46,186,180,233,222,1,120,13,77,60,3,41,157,45,250,153,104,220,182,172,103,226,153,121],
[72,154,94,239,83,242,137,6,24,184,7,9,225,44,112,193,74,238,216,9,229,167,71,208,89,230,197,188,101,67,6,216],
[116,252,214,166,243,67,41,154,58,78,234,85,188,76,65,246,139,100,138,7,54,163,87,118,142,205,17,26,98,95,39,242],
[144,255,15,174,25,182,1,220,175,11,41,141,69,69,174,46,120,208,177,158,130,66,119,3,235,143,255,5,149,42,138,165],
[112,233,174,39,48,209,136,82,207,75,221,255,118,18,27,139,84,186,104,189,22,174,14,176,131,31,106,243,139,173,146,244],
[250,254,133,76,108,59,53,147,15,200,135,17,138,131,147,99,199,233,75,71,240,26,199,232,60,27,173,69,39,246,92,48],
[119,210,114,33,191,38,98,22,244,162,249,182,30,234,188,43,61,164,212,142,73,23,155,62,96,128,111,104,167,146,203,65],
[167,152,96,47,165,177,203,192,142,135,92,7,61,156,32,137,220,99,13,180,186,52,77,237,74,147,251,15,108,122,59,28],
[249,181,52,222,139,244,215,224,198,114,40,243,200,5,79,102,209,44,203,56,200,23,44,99,183,250,162,206,231,158,210,112],
[195,177,63,246,116,210,113,123,248,17,244,174,232,40,110,74,27,54,182,31,213,70,119,148,22,77,62,118,73,8,4,227],
[174,223,121,235,197,225,150,67,127,80,219,62,36,51,65,225,209,187,13,144,188,232,86,67,248,61,152,24,198,30,51,118],
[169,227,202,33,181,210,194,212,51,158,125,246,64,200,59,83,94,208,5,226,181,74,53,92,39,155,121,119,196,28,160,34],
[124,154,149,143,36,8,222,81,182,28,217,58,223,4,195,230,121,181,17,97,174,39,223,245,163,115,72,29,9,250,221,93],
[94,129,132,118,175,123,131,87,207,57,77,136,126,101,29,176,73,215,180,68,41,126,101,135,219,224,57,29,241,38,251,65],
[167,177,51,217,242,161,150,33,207,188,199,179,3,252,175,40,71,23,126,212,112,84,36,19,243,40,155,89,25,44,143,44],
[142,157,145,41,142,233,158,158,64,158,34,89,115,91,16,81,46,212,130,142,166,58,205,243,193,255,109,107,83,94,185,217],
[103,181,101,82,232,131,3,160,69,31,133,57,115,220,168,30,207,218,190,44,102,244,113,203,36,224,195,195,212,238,52,182],
[104,138,170,151,231,202,217,205,81,42,246,108,123,2,40,96,196,95,144,98,49,43,23,184,181,141,105,31,176,224,164,81],
[138,159,183,96,66,36,16,145,131,178,48,236,226,217,221,117,86,187,22,179,167,17,14,54,180,217,218,74,69,245,169,120],
[91,206,220,176,108,243,52,201,226,28,70,196,123,18,54,236,230,47,81,109,168,137,192,19,127,143,11,161,226,230,31,19],
[24,207,128,6,155,134,151,169,43,105,35,121,125,93,184,219,76,180,221,129,248,201,38,206,237,34,227,219,92,238,20,4],
[76,30,37,108,85,239,66,35,18,15,80,26,63,117,31,162,172,3,140,4,250,168,31,250,208,3,41,58,66,122,214,223],
[13,114,121,124,89,22,163,146,144,123,191,224,85,156,229,6,254,190,77,25,36,208,94,171,60,104,191,188,222,202,52,249],
[61,6,137,137,31,211,146,84,248,242,181,113,192,186,69,59,7,72,9,101,14,204,101,246,140,62,12,151,191,78,125,45],
[157,136,146,168,3,25,221,183,210,160,37,98,46,154,200,51,233,78,211,136,192,80,238,133,173,53,176,141,252,127,213,208],
[236,37,13,175,18,251,87,187,224,204,128,5,91,147,115,122,151,89,90,163,65,38,17,122,231,248,212,192,124,138,107,170],
[145,19,150,65,190,97,199,178,76,115,138,198,136,18,180,253,248,247,187,179,194,161,221,246,94,254,64,61,91,186,104,69],
[235,120,75,39,150,196,72,209,145,27,180,77,11,2,154,155,125,233,102,2,252,239,45,119,156,67,142,249,160,160,43,116],
[143,165,24,101,222,187,133,80,114,98,164,11,16,227,43,133,145,213,75,107,148,34,89,73,28,136,140,131,231,105,2,209],
[255,184,148,30,2,59,196,206,224,101,11,205,173,175,148,17,245,251,207,74,117,102,216,250,162,252,162,141,19,22,115,134],
[31,58,43,194,88,106,56,41,88,34,189,211,128,188,100,228,149,6,140,214,89,223,4,232,12,183,1,187,28,146,97,11],
[173,159,50,163,30,151,172,58,118,11,139,20,227,150,135,213,107,120,100,176,68,197,190,248,82,15,225,61,55,196,240,250],
[8,42,165,143,186,179,64,44,100,15,30,158,136,10,240,220,181,174,221,223,195,144,160,79,89,146,43,90,157,51,97,249],
[61,3,209,85,236,48,55,183,70,6,193,208,190,103,211,46,221,3,25,245,200,43,37,8,104,91,246,3,89,13,132,120],
[91,121,64,214,89,93,32,238,196,217,242,53,71,78,136,226,189,164,233,98,238,230,250,56,65,83,137,141,171,250,231,62],
[133,122,163,187,119,181,55,152,138,23,49,26,211,59,150,19,144,166,205,184,82,209,107,20,157,165,177,216,27,103,147,81],
[138,114,71,105,110,180,111,127,214,105,13,43,148,113,228,203,37,239,239,238,125,114,244,74,24,241,242,146,130,94,46,79],
[85,108,150,69,191,198,106,86,228,219,78,42,73,10,92,242,16,3,18,27,228,216,36,149,19,179,28,6,226,38,163,82],
[191,46,144,17,234,91,79,85,44,28,26,143,24,237,106,132,165,28,88,162,186,248,45,92,31,189,164,172,255,51,125,111],
[15,105,201,161,101,197,235,191,127,28,238,232,231,198,234,172,192,193,60,42,87,165,80,226,245,151,8,214,96,118,19,23],
[84,157,205,255,217,251,101,194,230,208,26,232,23,201,46,29,123,221,11,53,196,102,220,130,2,70,240,1,178,74,188,195],
[244,120,86,42,110,203,209,158,119,115,207,5,104,140,138,113,25,153,59,171,105,67,136,70,30,10,203,80,13,200,172,216],
[116,64,52,174,54,126,16,194,162,33,33,157,176,197,225,12,59,55,253,228,148,47,179,185,24,138,253,20,142,55,172,88]
])

MAX_PAGES = 32
T_HASS = ['Test', 'Operational', 'Reserved', 'Don''t use']  # HAS status table

class GalE6():
    mid_prev = 0              # previous message id (MID)
    num_has_pages  = 0        # number of has pages of the message id
    storing_has_pages = True  # allow storing has pages
    haspage = [0b0 for i in range(MAX_PAGES)]
    hasindx = [0b0 for i in range(MAX_PAGES)]

    def __init__(self, fp_rtcm, fp_disp, t_level, color, stat):
        self.fp_rtcm = fp_rtcm
        self.fp_disp = fp_disp
        self.t_level = t_level
        self.msg_color = libcolor.Color(fp_disp, color)
        self.stat = stat
        self.ssr = libssr.Ssr(fp_disp, t_level, self.msg_color)

    def __del__(self):
        if self.stat:
            self.ssr.show_cssr_stat()

    def trace(self, level, *args):
        if self.t_level < level or not self.fp_disp:
            return
        for arg in args:
            try:
                print(arg, end='', file=self.fp_disp)
            except (BrokenPipeError, IOError):
                sys.exit()

    def read_from_pocketsdr(self):
        ''' returns True if E6B raw message is read '''
        line = True
        while line:
            line = sys.stdin.readline().strip()
            if not line:  # end of file
                return False
            if line[0:5] == '$CNAV':
                break
        satid = line.split(',')[3]
        e6b   = line.split(',')[4]
        rawb = bitstring.BitArray(bytes.fromhex(e6b))[14:-2-24]
        # discards top 14 bit (reserved)
        # discards tail 2 bit (byte-align) and 24 bit (CRC)
        # HAS raw binary (rawb) size is 448 bit
        self.satid = satid
        self.rawb  = rawb
        return True

    def ready_decoding_has(self):
        ''' returns True if valid HAS message is ready '''
        rawb = self.rawb
        pos = 0
        hass = rawb[pos:pos+2].uint  ; pos += 2  # HAS status
        pos += 2                                 # reserved
        mt   = rawb[pos:pos+2].uint  ; pos += 2  # message type, should be 1
        mid  = rawb[pos:pos+5].uint  ; pos += 5  # message id
        ms   = rawb[pos:pos+5].uint+1; pos += 5  # message size
        pid  = rawb[pos:pos+8].uint  ; pos += 8  # page id
        disp_msg = self.msg_color.fg('green') + f'E{int(self.satid):02d}' + \
                   self.msg_color.fg()
        if self.rawb[0:24].hex == 'af3bc3':
            if self.fp_disp:
                disp_msg += self.msg_color.dec('dark')
                disp_msg += ' Dummy page (0xaf3bc3)'
                disp_msg += self.msg_color.dec()
                print(disp_msg, file=self.fp_disp)
            return False
        disp_msg += self.msg_color.fg('yellow')
        disp_msg += f' HASS={T_HASS[hass]}({hass})'
        disp_msg += self.msg_color.fg()
        disp_msg += f' MT={mt}'
        disp_msg += f' MID={mid:2d}'
        disp_msg += f' MS={ms:2d}'
        disp_msg += f' PID={pid:3d}'
        if mid != self.mid_prev:
            # new message id --- reset buffer and message pointer
            disp_msg += f' -> A new page for MID={mid}'
            self.mid_prev = mid
            self.num_has_pages = 0
            self.storing_has_pages = True
        # store the HAS page and its index (pid: page id)
        self.haspage[self.num_has_pages] = [x for x in rawb[pos:].tobytes()]
        self.hasindx[self.num_has_pages] = pid
        self.mt  = mt
        self.mid = mid
        self.ms  = ms
        if self.mt != 1:
            return False  # only MT1 message is defined for E6B
        if self.num_has_pages < MAX_PAGES - 1:
            self.num_has_pages += 1
        if self.num_has_pages < ms:
            # continue to store HAS pages
            if self.fp_disp:
                print(disp_msg, file=self.fp_disp)
            return False
        if not self.storing_has_pages:
            # we already have enough HAS pages related to the message id
            disp_msg += f' -> Enough pages for MID={mid}'
            if self.fp_disp:
                print(disp_msg, file=self.fp_disp)
            return False
        if self.fp_disp:
            print(disp_msg, file=self.fp_disp)
        self.storing_has_pages = False  # we don't need additional HAS pages
        return True

    def obtain_has_message(self):
        ''' returns HAS message '''
        d = GF(g[np.array(self.hasindx[:self.ms])-1, :self.ms])
        w = GF(self.haspage[:self.ms])
        m = np.linalg.inv(d) @ w
        has_msg = bitstring.BitArray(m.tobytes())
        self.trace(2, f'------ HAS decode with the pages of MID={self.mid} MS={self.ms} ------\n')
        self.trace(2, has_msg, '\n------\n')
        return has_msg

    def decode_has_message(self, has_msg):
        pos = self.decode_has_header(has_msg)
        if self.f_mask:
            pos = self.ssr.decode_has_mask(has_msg, pos)
        if self.f_orbit:
            pos = self.ssr.decode_has_orbit(has_msg, pos)
        if self.f_ckful:
            pos = self.ssr.decode_has_ckful(has_msg, pos)
        if self.f_cksub:
            pos = self.ssr.decode_has_cksub(has_msg, pos)
        if self.f_cbias:
            pos = self.ssr.decode_has_cbias(has_msg, pos)
        if self.f_pbias:
            pos = self.ssr.decode_has_pbias(has_msg, pos)
        self.trace(2, '------ padding bits ------\n')
        self.trace(2, has_msg[pos:].bin)
        self.trace(2, '\n------\n')

    def decode_has_header(self, has_msg):
        ''' returns new HAS message position '''
        pos = 0
        self.toh     = has_msg[pos:pos+12].uint; pos += 12
        self.f_mask  = has_msg[pos:pos+1]; pos += 1
        self.f_orbit = has_msg[pos:pos+1]; pos += 1
        self.f_ckful = has_msg[pos:pos+1]; pos += 1
        self.f_cksub = has_msg[pos:pos+1]; pos += 1
        self.f_cbias = has_msg[pos:pos+1]; pos += 1
        self.f_pbias = has_msg[pos:pos+1]; pos += 1
        pos += 4 # reserved
        self.maskid  = has_msg[pos:pos+5].uint; pos += 5
        self.iodset  = has_msg[pos:pos+5].uint; pos += 5
        disp_msg = ''
        disp_msg += f'Time of hour TOH: {self.toh} s\n'
        disp_msg += f'Mask            : {"on" if self.f_mask  else "off"}\n'
        disp_msg += f'Orbit correction: {"on" if self.f_orbit else "off"}\n'
        disp_msg += f'Clock full-set  : {"on" if self.f_ckful else "off"}\n'
        disp_msg += f'Clock subset    : {"on" if self.f_cksub else "off"}\n'
        disp_msg += f'Code bias       : {"on" if self.f_cbias else "off"}\n'
        disp_msg += f'Phase bias      : {"on" if self.f_pbias else "off"}\n'
        disp_msg += f'Mask ID         : {self.maskid}\n'
        disp_msg += f'IOD Set ID      : {self.iodset}'
        if self.fp_disp:
            print(disp_msg, file=self.fp_disp)
        return pos

def icd_test():
    '''self test described in [1] attached file,
    Galileo-HAS-SIS-ICD_1.0_Annex_D_HAS_Message_Decoding_Example.txt
    To execute this ICD test,
    python
    >>> import libgale6
    >>> libgale6.icd_test()
    '''
    gale6 = GalE6(None, sys.stdout, 2, True, False)
    gale6.mt = 1
    has_msg = bitstring.BitArray('0x000cc00b20ffdfffff008100f7ffff7df55ffdfe0beee8a79a41241000a6000a01a01280400200200113fbc041febbf00080080042ff6822fea21807c193f7598035fd7f6a2f00080080016ff90287e7967f702580587fee217a10c9dfcc0e7f651df577d981603ffe4147f903ff9df7805c15ff9fdcff8008004004000a002407ff9d7c07df7ffe2b5fdcee305519011fd7fd24479f00500e8e7edc31401c43fdb02304007fe5030ff1ac40020020000200100100077fec06e00141feb02afcb2c400200200043ff5f6c022097f7c0e3f4412ff4fe1ff8825fe8ffcff0048081fe3fda097f4c04bf3812fe5ff27f0025fc6ff5ff40480edfa601c08ffe8023fcc0f00b00b80a825fdf00fff704bf71ffffdc097fb400c00812fe781a7f8025fe602203204801001a01607ffd006404012fec00e000825fc7fe500c04bff405605c08804004403012fe27feffbf0bb23dc94458ef0420afe1fa61544abda77c130444320a1104303d3f76f65fbbee7ccf5fe6bddf8bfcff479b7a5f1dc3bf3fce1243b44e90d1784ac350b2f29f2bd607b1a1e7bb207519201003807069f8feb7cf00c0d42d85b061f33d2fa7fa00fc3506a02015c4b09409bf07cbf950400641582a04fc8f40e88d2dd9f73efbdc40080400407c198588ad0e9f43d67aef9009c220420cdefbc9f90f920f0338660401a45a0b411a0841c8380c206c1882d0121243e87d02bf27d1fa2fc6184518a50dcb000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008004002001000800400200100080040020010008002aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    gale6.decode_has_message(has_msg)
    if self.fp_disp:
        print(file=self.fp_disp)
    has_msg = bitstring.BitArray('0x0072000b58afe4002d03000acd5826ae3000aaa5532b15581aaa572aa175b8800516e941454a28550ebd5556aa8c002001546a92c002c08020fd6ff200bbfe4fe2fec41020210207ff7f85ff8007002bfe202d000ffbc052044febaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    gale6.decode_has_message(has_msg)

# EOF
