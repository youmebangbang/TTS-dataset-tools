import datetime
from pathlib import Path
import numpy
import simpleaudio as sa
import io
import math
from pydub import AudioSegment
from pydub.utils import mediainfo
from pydub.playback import play
from dearpygui.core import *
from dearpygui.simple import *
import os
import ntpath
import csv
import argparse
import numpy as np
import re
import shutil
import simpleaudio as sa

class Proofreader:
    def __init__(self):
        self.current = None
        self.current_point = None
        self.current_plot_point = None
        self.next = None
        self.next_point = None
        self.next_plot_point = None
        self.selected_row = 0
        self.num_items = 0
        self.activated = False

    def set_activated(self, value):
        self.activated = value

    def is_activated(self):
        return self.activated

    def autosave(self):
        if self.get_current() == None:
            return 
        name = get_value("proofread_project_name")
        if name:
            newline = ""
            with open("{}/{}".format(self.get_project_path(), "autosave.csv"), 'w') as csv_file:
                table = get_table_data("table_proofread")
                for row in table:
                    csv_file.write("{}{}|{}".format(newline, row[0], row[1]))
                    newline = "\n"
            set_value("proofread_status", "{}/{} saved".format(self.get_project_path(), "autosave.csv"))            
            #logging
            with open("{}/logfile.txt".format(self.get_project_path()), 'a') as log_file:
                t = datetime.datetime.now()
                tt = t.strftime("%c")
                row = self.get_selected_row()
                last_wav = get_table_item("table_proofread", row, 0)
                log_file.write("\n{}: Saved {} Last item selected: {}".format(tt, "autosave.csv", last_wav))            

        # save_csv_proofread_call("", "autosave")
        print("autosaving to autosave.csv")

    def scroll_up(self):
        if is_item_active("current_input_text") or is_item_active("next_input_text"):
            return
        row = self.get_selected_row()
        if row == 0:
            return
        if self.get_current() == None:
            return            
        row = row - 1
        self.set_selected_row(row)
        current_path = get_table_item("table_proofread", row, 0)
        next_path = get_table_item("table_proofread", row+1, 0)

        current_wav = AudioSegment.from_wav("{}/{}".format(self.get_project_path(), current_path))
        next_wav = AudioSegment.from_wav("{}/{}".format(self.get_project_path(), next_path))
        #check to see if wav is empty?

        set_value("current_input_text", get_table_item("table_proofread", row, 1))
        set_value("next_input_text", get_table_item("table_proofread", row+1, 1))
        configure_item("current_plot", label=current_path)
        configure_item("next_plot", label=next_path)
        # set_value("wav_current_label", current_path)
        # set_value("wav_next_label", next_path)
        self.set_current(current_wav)
        self.set_next(next_wav)
        self.plot_wavs()

    def scroll_down(self):     
        if is_item_active("current_input_text") or is_item_active("next_input_text"):
            return   
        row = self.get_selected_row()
        if self.get_num_items() <= (row + 2):
            return
        if self.get_current() == None:
            return
            
        row = row + 1    
        self.set_selected_row(row)
        current_path = get_table_item("table_proofread", row, 0)
        next_path = get_table_item("table_proofread", row+1, 0)

        current_wav = AudioSegment.from_wav("{}/{}".format(self.get_project_path(), current_path))
        next_wav = AudioSegment.from_wav("{}/{}".format(self.get_project_path(), next_path))

        set_value("current_input_text", get_table_item("table_proofread", row, 1))
        set_value("next_input_text", get_table_item("table_proofread", row+1, 1))
        configure_item("current_plot", label=current_path)
        configure_item("next_plot", label=next_path)
        # set_value("wav_current_label", current_path)
        # set_value("wav_next_label", next_path)
        self.set_current(current_wav)
        self.set_next(next_wav)
        self.plot_wavs()

    def set_num_items(self, data):
        self.num_items = data

    def get_num_items(self):
        return self.num_items

    def play(self, data):
        wav = data            
        sa.play_buffer(
            wav.raw_data,
            num_channels=wav.channels,
            bytes_per_sample=wav.sample_width,
            sample_rate=wav.frame_rate
        )

    def stop(self):
        sa.stop_all()

    def set_selected_row(self, row):
        self.selected_row = row

    def get_selected_row(self):
        return self.selected_row

    def set_rate(self, rate):
        self.rate = int(rate)

    def get_rate(self):
        return self.rate

    def set_current_point(self, point):
        self.current_point = point

    def get_current_point(self):
        return self.current_point

    def set_next_point(self, point):
        self.next_point = point

    def get_next_point(self):
        return self.next_point

    def set_current(self, wav):  
        self.current = wav         
    
    def set_next(self, wav):
        self.next = wav

    def get_current(self):
        return self.current

    def get_next(self):
        return self.next

    def set_project_path(self, path):
        self.project_path = path

    def get_project_path(self):
        return self.project_path

    def plot_wavs(self):
        audio1 = self.current.get_array_of_samples()   
        current_int16 = numpy.frombuffer(audio1, dtype=numpy.int16)
        current_float32 = list(current_int16.astype(numpy.float32))

        audio2 = self.next.get_array_of_samples()   
        next_int16 = numpy.frombuffer(audio2, dtype=numpy.int16)
        next_float32 = list(next_int16.astype(numpy.float32))

        current_x_axis = []
        next_x_axis = []

        for i in range(0, len(current_float32)):
            current_x_axis.append(i)
        for i in range(0, len(next_float32)):
            next_x_axis.append(i)  

        #print("current_plot length for sample rate is: {}".format(len(current_x_axis) / 44100))     
        add_line_series("current_plot", "", current_x_axis, current_float32, weight=2)
        add_line_series("next_plot", "", next_x_axis, next_float32, weight=2)

    def current_plot_drawing_set_point(self, point):
        self.current_point = point
        draw_line("current_plot_drawing", [0,5], [1200, 5], [0,19,94, 255], 10)
        if point:
            draw_line("current_plot_drawing", [point-3,5], [point+3, 5], [255, 0, 0, 255], 10)
    
    def next_plot_drawing_set_point(self, point):
        self.next_point = point
        draw_line("next_plot_drawing", [0,5], [1200, 5], [0,19,94, 255], 10)
        if point:
            draw_line("next_plot_drawing", [point-3,5], [point+3, 5], [255, 0, 0, 255], 10)