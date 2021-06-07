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
import math

class Proofreader:
    def __init__(self):
        self.current = None
        self.current_point = None
        self.current_plot_point = None
        self.current_p = None
        self.next = None
        self.cut = None
        self.next_point = None
        self.next_plot_point = None
        self.next_p = None
        self.selected_row = 0
        self.num_items = 0
        self.activated = False
        self.fname = None
        self.drag_in_current = None
        self.drag_in_next = None
        self.drag_out_current = None
        self.drag_out_next = None
        self.selection_range_current = [None, None]
        self.selection_range_next = [None, None]

    def set_filename(self, fname):
        self.fname = fname

    def get_filename(self):
        return self.fname

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
        add_data("current_path", current_path)
        add_data("next_path", next_path)

        # set_value("current_plot_label", current_path)


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
        add_data("current_path", current_path)
        add_data("next_path", next_path)

        # set_value("current_plot_label", current_path)


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

        # current_x_axis = []
        # next_x_axis = []

        current_polyline = []
        next_polyline = []

        clear_drawing("current_plot_drawing_new")
        clear_drawing("next_plot_drawing_new")

        x_step = float(len(current_float32) / 1200)
        y_max = max(current_float32)
        x_step_count = 0
        c = 0
        
        for i in range(0, len(current_float32)):
            # current_x_axis.append(i)
            if (i >= x_step_count):
                # Draw vertical bars method
                # y_axis_val = ((current_float32[i] + y_max) / (y_max*2)) * 200 
                y_axis_val = (current_float32[i] / y_max) * 100 
                draw_line("current_plot_drawing_new", [c,100], [c, y_axis_val+100], [222, 44, 255, 255], 1)
                # current_polyline.append([ c, y_axis_val ])
                c += 1
                x_step_count += x_step

        x_step = float(len(next_float32) / 1200)
        y_max = max(next_float32)
        x_step_count = 0
        c = 0
        for i in range(0, len(next_float32)):
            # next_x_axis.append(i)
            if (i >= x_step_count):
                # y_axis_val = ((next_float32[i] + y_max) / (y_max*2)) * 200 
                y_axis_val = (next_float32[i] / y_max) * 100 
                draw_line("next_plot_drawing_new", [c,100], [c, y_axis_val+100], [222, 44, 255, 255], 1)
                # next_polyline.append([ c, y_axis_val ])
                c += 1
                x_step_count += x_step 

        #print("current_plot length for sample rate is: {}".format(len(current_x_axis) / 44100))     
        # add_line_series("current_plot", "", current_x_axis, current_float32, weight=2)
        # add_line_series("next_plot", "", next_x_axis, next_float32, weight=2)

        # clear_drawing("current_plot_drawing_new")
        # Polyline method
        # draw_polyline("current_plot_drawing_new", current_polyline, [255,255,0,255], thickness=3)

        draw_text("current_plot_drawing_new", [10, 175], get_data("current_path"), size=20)
        draw_polyline("next_plot_drawing_new", next_polyline, [255,255,0,255], thickness=3)
        draw_text("next_plot_drawing_new", [10, 175], get_data("next_path"), size=20)


    # def current_plot_drawing_set_point(self, point):
    #     self.current_point = point
    #     draw_line("current_plot_drawing", [0,5], [1200, 5], [0,19,94, 255], 10)
    #     if point:
    #         draw_line("current_plot_drawing", [point-3,5], [point+3, 5], [255, 0, 0, 255], 10)
    
    # def next_plot_drawing_set_point(self, point):
    #     self.next_point = point
    #     draw_line("next_plot_drawing", [0,5], [1200, 5], [0,19,94, 255], 10)
    #     if point:
    #         draw_line("next_plot_drawing", [point-3,5], [point+3, 5], [255, 0, 0, 255], 10)

    def draw_selector(self, drawing_name, x_axis):
        delete_draw_command("current_plot_drawing_new", 'selector')
        delete_draw_command("next_plot_drawing_new", 'selector')
        
        draw_line(drawing_name, [x_axis, 0], [x_axis, 200], [0,0,255,255], 3, tag='selector')

    def draw_dragbox(self, drawing_name, x_axis):
        self.set_next_p(None)
        self.set_current_p(None)
        delete_draw_command("current_plot_drawing_new", 'selector')
        delete_draw_command("current_plot_drawing_new", 'dragbox')
        delete_draw_command("current_plot_drawing_new", 'p_selector')
        delete_draw_command("next_plot_drawing_new", 'selector')
        delete_draw_command("next_plot_drawing_new", 'dragbox')
        delete_draw_command("next_plot_drawing_new", 'p_selector')
        if drawing_name == "current_plot_drawing_new":
            draw_rectangle(drawing_name, [self.drag_in_current, 0], [x_axis, 200], [125, 50, 50, 255], fill=[204, 229, 255, 80], rounding=0, thickness=2.0, tag='dragbox')
        elif drawing_name == "next_plot_drawing_new":
            draw_rectangle(drawing_name, [self.drag_in_next, 0], [x_axis, 200], [125, 50, 50, 255], fill=[204, 229, 255, 80], rounding=0, thickness=2.0, tag='dragbox')

    def draw_p_selection(self, drawing_name, x_axis):
        self.set_selection_range_current(None , None)
        self.set_selection_range_next(None, None)
        delete_draw_command("current_plot_drawing_new", 'selector')
        delete_draw_command("current_plot_drawing_new", 'dragbox')
        delete_draw_command("current_plot_drawing_new", 'p_selector')
        delete_draw_command("next_plot_drawing_new", 'selector')
        delete_draw_command("next_plot_drawing_new", 'dragbox')
        delete_draw_command("next_plot_drawing_new", 'p_selector')        
        draw_line(drawing_name, [x_axis, 0], [x_axis, 200], [255,0,0,255], 5, tag='p_selector')

    def set_drag_in_current(self, x_axis):
        self.drag_in_current = x_axis

    def get_drag_in_current(self):
        return self.drag_in_current

    def set_drag_in_next(self, x_axis):
        self.drag_in_next = x_axis

    def get_drag_in_next(self):
        return self.drag_in_next

    def set_drag_out_current(self, x_axis):
        self.drag_out_current = x_axis

    def get_drag_out_current(self):
        return self.drag_out_current

    def set_drag_out_next(self, x_axis):
        self.drag_out_next = x_axis

    def get_drag_out_next(self):
        return self.drag_out_next        

    def set_selection_range_current(self, x, y):
        self.selection_range_current[0] = x
        self.selection_range_current[1] = y

    def get_selection_range_current(self):
        return self.selection_range_current[0], self.selection_range_current[1]

    def set_selection_range_next(self, x, y):
        self.selection_range_next[0] = x
        self.selection_range_next[1] = y

    def get_selection_range_next(self):
        return self.selection_range_next[0], self.selection_range_next[1]

    def set_cut(self, cut):
        self.cut = cut
    
    def get_cut(self):
        return self.cut 

    def set_current_p(self, p):
        self.current_p = p

    def get_current_p(self):
        return self.current_p

    def set_next_p(self, p):
        self.next_p = p

    def get_next_p(self):
        return self.next_p