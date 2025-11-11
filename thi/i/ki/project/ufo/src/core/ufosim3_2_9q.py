# DO NOT CHANGE THIS FILE

# ufoim
# Simulation of Unified Flying Objects
# Copyright (C) 2013-2025 R. Gold
#
# This file is intended for use as an example, and may be used, 
# modified, or distributed in source or object code form, 
# without restriction, as long as # this copyright notice is 
# preserved.
#
# The software is provided "as-is", without warranty of any kind, 
# either expressed or implied, including but not limited to the 
# warranties of merchability, fitness for a particular purpose 
# and noninfringement. In no event shall the autor be liable for 
# any claim, damages or other liability, whether in an action of 
# contract, tort or otherwise, arising from, out of or in 
# connection with the software or the use or other dealings in 
# the software.
#
# Version: 3.2.9q
#
# Requires: 114060-OOYHOE-336.png, thi_icon_258.png, ufo_icon2.png 
#
# Change history: 
# 
# 3.2.8: 
# - ported to Python
# - no obstacles
# - no [] in format_flight_data in the example
# - destinations are added in the constructor of UfoPView
# - both classes UfoSim and UfoPView in one file
# - file header updated
# - print("ufosim: scaling has to be between 1 and 100") deleted
# 3.2.9: 
# - VMAX set to 15

import math
import os
import threading
import time
import tkinter as tk

class UfoSim:

    def __init__(self) -> None:
        # sim constants
        self.__VMAX = 15                    # maximal velocity [km/h]
        self.__ACCELERATION = 1             # constant acceleration [km/h/0.1s]
        self.__SPEEDUP = 1                  # real-time speedup factor > 0
        self.__STEP = 0.1                   # sim step time [s]

        # sim attributes: see reset()
        self.reset()

        # other attributes
        self.__running = False              # simulation running

    # resetter, getter, requester, setter
    def reset(self) -> None:
        self.__x = 0.0                      # x coordinate [m]
        self.__y = 0.0                      # y coordinate [m]
        self.__z = 0.0                      # z coordinate [m]
        self.__v = 0                        # 0 <= velocity <= vMax [km/h]
        self.__d = 90                       # 0 <= direction <= 359 [deg]
        self.__i = 90                       # -90 <= inclination <= 90 [deg]
        self.__dist = 0.0                   # distance covered since reset [m]
        self.__ftime = 0.0                  # elapsed flight time with v > 0 since reset [s]
        self.__xvect = 0.0                  # flight vector in x direction
        self.__yvect = 0.0                  # flight vector in y direction
        self.__zvect = 0.0                  # flight vector in z direction
        self.__delta_v = 0                  # requested change of v
        self.__delta_d = 0                  # requested change of d
        self.__delta_i = 0                  # requested change of i
        self.__vel = 0.0                    # velocity [m/s]
    def get_speedup(self) -> float:
        return self.__SPEEDUP
    def get_step(self) -> float:
        return self.__STEP
    def get_x(self) -> float:
        return self.__x
    def get_y(self) -> float:
        return self.__y
    def get_z(self) -> float:
        return self.__z
    def get_v(self) -> int:
        return self.__v
    def get_d(self) -> int:
        return self.__d
    def get_i(self) -> int:
        return self.__i
    def get_dist(self) -> float:
        return self.__dist
    def get_ftime(self) -> float:
        return self.__ftime
    def request_delta_v(self, delta: int) -> None:
        self.__delta_v = self.__delta_v + delta
    def request_delta_d(self, delta: int) -> None:
        self.__delta_d = self.__delta_d + delta
    def request_delta_i(self, delta: int) -> None:
        self.__delta_i = self.__delta_i + delta
    def set_d(self, new_d: int) -> None:
        if new_d >= 0 and new_d <= 359:
            self.__d = new_d
    def set_i(self, new_i: int) -> None:
        if new_i >= -90 and new_i <= 90:
            self.__i = new_i

    # update simulation
    def __update_sim(self) -> None:
        # update time if flying
        if self.__z > 0.0:
            self.__ftime = self.__ftime + self.__STEP

        # update v, d, i, dist, x, y, z if not crashed
        if self.__z >= 0:
            # update v
            if self.__delta_v > 0:
                if self.__delta_v - self.__ACCELERATION > 0:
                    if self.__v + self.__ACCELERATION < self.__VMAX:
                        self.__v = self.__v + self.__ACCELERATION
                    else:
                        self.__v = self.__VMAX
                    self.__delta_v = self.__delta_v - self.__ACCELERATION
                else:
                    if self.__v + self.__delta_v < self.__VMAX:
                        self.__v = self.__v + self.__delta_v
                    else:
                        self.__v = self.__VMAX
                    self.__delta_v = 0
            elif self.__delta_v < 0:
                if self.__delta_v + self.__ACCELERATION < 0:
                    if self.__v - self.__ACCELERATION > 0:
                        self.__v = self.__v - self.__ACCELERATION
                    else:
                        self.__v = 0
                    self.__delta_v = self.__delta_v + self.__ACCELERATION
                else:
                    if self.__v + self.__delta_v > 0:
                        self.__v = self.__v + self.__delta_v
                    else:
                        self.__v = 0
                    self.__delta_v = 0

            # update d
            if   self.__delta_d > 0 and self.__d == 359: 
                self.__delta_d = self.__delta_d - 1
                self.__d = 0
            elif self.__delta_d > 0 and self.__d < 359:
                self.__delta_d = self.__delta_d - 1
                self.__d = self.__d + 1
            elif self.__delta_d < 0 and self.__d == 0:
                self.__delta_d = self.__delta_d + 1
                self.__d = 359
            elif self.__delta_d < 0 and self.__d > 0:
                self.__delta_d = self.__delta_d + 1
                self.__d = self.__d - 1
            else:
                self.__delta_d = 0
        
            # update i
            if   self.__delta_i > 0 and self.__i < 90: 
                self.__delta_i = self.__delta_i - 1
                self.__i = self.__i + 1
            elif self.__delta_i < 0 and self.__i > -90: 
                self.__delta_i = self.__delta_i + 1
                self.__i = self.__i - 1
            else:
                self.__delta_i = 0
        
            # update velocity in m/s
            self.__vel = self.__v / 3.6
            
            # update distance
            self.__dist = self.__dist + self.__vel * self.__STEP

            # convert flight vector from polar coordinates to cartesian coordinates
            self.__xvect = math.sin((-self.__i+90)/180 * math.pi) * math.cos(self.__d/180 * math.pi)
            self.__yvect = math.sin((-self.__i+90)/180 * math.pi) * math.sin(self.__d/180 * math.pi)
            self.__zvect = math.cos((-self.__i+90)/180 * math.pi)
        
            # calculate new position every self.__STEP ms with velocity self.__STEP * v
            self.__x = self.__x + self.__vel * self.__STEP * self.__xvect
            self.__y = self.__y + self.__vel * self.__STEP * self.__yvect
            self.__z = self.__z + self.__vel * self.__STEP * self.__zvect

        # stop if landed or crashed
        if self.__z <= 0.0:
            if self.__v == 1:               # landed with slow velocity
                self.__z = 0.0
                self.__v = 0
            elif self.__v > 1:              # crashed to the ground
                self.__z = -1.0
                self.__v = 0

    # thread start and terminate functions
    def start(self, speedup: int = 1, scaling: int = 10, destinations: list = []) -> None:
        # check speedup
        if speedup < 1 or speedup > 25:
            print("ufosim: speedup has to be between 1 and 25")
            self.__SPEEDUP = 1
        else:
            self.__SPEEDUP = speedup
        self.__running = True
        # if scaling is invalid, the view is not started
        if scaling < 1 or scaling > 100:
            print("ufosim: starting sim without view")
        else:
            # start view thread
            view_thread = threading.Thread(target=self.__run_view, args=(scaling, destinations, ))
            view_thread.start()
            time.sleep(2)                   # wait for the view to come up
        sim_thread = threading.Thread(target=self.__run_sim)
        sim_thread.start()
    def terminate(self) -> None:
        self.__running = False

    # thread functions
    def __run_sim(self) -> None:
        while self.__running:
            self.__update_sim()
            time.sleep(self.__STEP/self.__SPEEDUP)
    def __run_view(self, scaling: int, destinations: list) -> None:
        view = UfoPView(self, scaling, destinations)

class UfoPView:

    def __init__(self, sim, scaling: int, destinations: list) -> None:
        # constants
        self.__WINDOW_SIZE = 600
        self.__IMAGE_SIZE = 2000
        self.__DOT_RADIUS = 12
        # attributes initialized from parameters
        self.__sim = sim
        self.__scaling = scaling
        self.__destinations = destinations
        # gui attributes
        self.__root = tk.Tk()
        self.__root.geometry(str(self.__WINDOW_SIZE) + "x" + str(self.__WINDOW_SIZE))
        self.__root.title("Ufo Simulation")
        self.__first_resize = True
        self.__canvas_width = self.__WINDOW_SIZE
        self.__canvas_height = self.__WINDOW_SIZE
        self.__root.bind('<Configure>', self.__resize_handler)
        self.__package_dir = os.path.dirname(os.path.abspath(__file__))
        icon_file = os.path.join(self.__package_dir, "thi_icon_258.png")
        icon_image = tk.PhotoImage(file=icon_file, width=258, height=258)
        self.__root.iconphoto(False, icon_image)
        # the map is downloaded license free from http://www.freepik.com
        map_file = os.path.join(self.__package_dir, "114060-OOYHOE-336.png")
        map_image = tk.PhotoImage(file=map_file, width=self.__IMAGE_SIZE, height=self.__IMAGE_SIZE)
        self.__canvas = tk.Canvas(master=self.__root)
        self.__canvas.create_image(0, 0, image=map_image, anchor="nw")
        self.__canvas.place(x=0, y=0, width=self.__IMAGE_SIZE, height=self.__IMAGE_SIZE)
        self.__update_thread = threading.Thread(target=self.__update)
        self.__update_thread.daemon = True
        self.__update_thread.start()
        self.__root.mainloop()

    def __update(self) -> None:
        # create the ufo image
        ufo_file = os.path.join(self.__package_dir, "ufo_icon2.png")
        ufo_image = tk.PhotoImage(file=ufo_file, width=72, height=39)

        # draw starting point
        self.__draw_centered_dot(0, 0, self.__DOT_RADIUS, "white", 5, "start_point")
        
        # draw destinations
        for i in range(len(self.__destinations)):
            self.__draw_centered_dot(self.__destinations[i][0], self.__destinations[i][1], self.__DOT_RADIUS, "white", 5, "destination_out_"+str(i))
            self.__draw_centered_dot(self.__destinations[i][0], self.__destinations[i][1], self.__DOT_RADIUS//2, "black", 0, "destination_in_"+str(i))

        # draw ufo
        ufo = self.__draw_centered_image(self.__sim.get_x(), self.__sim.get_y(), ufo_image, "ufo")
        ufo_dot = self.__draw_centered_dot(self.__sim.get_x(), self.__sim.get_y(), self.__DOT_RADIUS//2, "blue", 0, "ufo_dot")

        # draw ufo annotation text
        ufo_text = self.__canvas.create_text(self.__sim.get_x(), self.__sim.get_y(), fill="blue", font="Courier 10")

        # draw header text
        header_text = self.__canvas.create_text(12, 12, fill="black", font="Courier 10", anchor="nw")

        # draw flight info text
        info_text_status = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_x = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_y = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_z = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_v = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_d = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_i = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_dist = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")
        info_text_time = self.__canvas.create_text(0, 0, fill="black", font="Courier 10", anchor="se")

        # draw size graphics
        size_text = self.__canvas.create_text(0, 0, text="10 m", fill="black", font="Courier 10", anchor="sw")
        size_line = self.__canvas.create_line(0, 0, 0, 0, fill="black")

        while True:
            # update ufo position
            self.__move_centered_item(ufo, self.__sim.get_x(), self.__sim.get_y(), 72, 39)
            self.__move_centered_item(ufo_dot, self.__sim.get_x(), self.__sim.get_y(), self.__DOT_RADIUS, self.__DOT_RADIUS)

            # update ufo annotation text
            if (self.__sim.get_v() != 0 and (self.__sim.get_i() < -1 or self.__sim.get_i() > 1)):
                self.__canvas.itemconfig(ufo_text, text=str(self.__sim.get_i())  + " deg")
            else:
                self.__canvas.itemconfig(ufo_text, text="")
            annotation_width = self.__canvas.bbox(ufo_text)[2] - self.__canvas.bbox(ufo_text)[0]
            self.__move_centered_item(ufo_text, self.__sim.get_x(), self.__sim.get_y(),
                                         self.__canvas.bbox(ufo_text)[2] - self.__canvas.bbox(ufo_text)[0],
                                         self.__canvas.bbox(ufo_text)[3] - self.__canvas.bbox(ufo_text)[1], annotation_width//2, -15)

            # update header text
            self.__canvas.itemconfig(header_text, text=str(self.__sim.get_speedup())+"x real-time")

            # update flight info text
            if (self.__sim.get_z() > 0.0):
                self.__canvas.itemconfig(info_text_status, text="ufo:    flying   ", fill="blue")
            elif (self.__sim.get_z() == 0.0):
                self.__canvas.itemconfig(info_text_status, text="ufo:    grounded ", fill="black")
            elif (self.__sim.get_z() == -1.0):
                self.__canvas.itemconfig(info_text_status, text="ufo:    crashed  ", fill="red")
            else:
                self.__canvas.itemconfig(info_text_status, text="")

            self.__canvas.itemconfig(info_text_x, text="x:    {:6.1f} m   ".format(self.__sim.get_x()))
            self.__canvas.itemconfig(info_text_y, text="y:    {:6.1f} m   ".format(self.__sim.get_y()))
            self.__canvas.itemconfig(info_text_z, text="z:    {:6.1f} m   ".format(self.__sim.get_z()))
            self.__canvas.itemconfig(info_text_v, text="v:     {:3d}   km/h".format(self.__sim.get_v()))
            self.__canvas.itemconfig(info_text_d, text="d:     {:3d}   deg ".format(self.__sim.get_d()))
            self.__canvas.itemconfig(info_text_i, text="i:     {:3d}   deg ".format(self.__sim.get_i()))
            self.__canvas.itemconfig(info_text_dist, text="dist: {:6.1f} m   ".format(self.__sim.get_dist()))
            self.__canvas.itemconfig(info_text_time, text="time: {:6.1f} s   ".format(self.__sim.get_ftime()))

            self.__canvas.coords(info_text_status, self.__canvas_width - 12, self.__canvas_height - 116) 
            self.__canvas.coords(info_text_x, self.__canvas_width - 12, self.__canvas_height - 103) 
            self.__canvas.coords(info_text_y, self.__canvas_width - 12, self.__canvas_height - 90) 
            self.__canvas.coords(info_text_z, self.__canvas_width - 12, self.__canvas_height - 77) 
            self.__canvas.coords(info_text_v, self.__canvas_width - 12, self.__canvas_height - 64) 
            self.__canvas.coords(info_text_d, self.__canvas_width - 12, self.__canvas_height - 51) 
            self.__canvas.coords(info_text_i, self.__canvas_width - 12, self.__canvas_height - 38) 
            self.__canvas.coords(info_text_dist, self.__canvas_width - 12, self.__canvas_height - 25) 
            self.__canvas.coords(info_text_time, self.__canvas_width - 12, self.__canvas_height - 12)

            # update size graphics
            self.__canvas.coords(size_text, 12, self.__canvas_height - 12) 
            self.__canvas.coords(size_line, 12, self.__canvas_height - 10, 12 + 10 * self.__scaling, self.__canvas_height - 10)  

            # update and sleep
            self.__canvas.update()
            time.sleep(self.__sim.get_step()/self.__sim.get_speedup())
        
    # move a canvas item
    def __move_centered_item(self, item: int, x: int, y: int, width: int = 0, height: int = 0, offset_x: int = 0, offset_y: int = 0) -> None:
        local_x = self.__scaling * x + self.__canvas_width / 2
        local_y = self.__scaling * -y + self.__canvas_height / 2

        try:
            self.__canvas.coords(item, local_x - width / 2 + offset_x, local_y - height / 2 + offset_y)
        except tk.TclError:
            self.__canvas.coords(item, local_x - width / 2 + offset_x, local_y - height / 2 + offset_y, local_x + width / 2 + offset_x, local_y + height / 2 + offset_y)


    # draw a canvas dot
    def __draw_centered_dot(self, x: int, y: int, radius: int, color: str, width: int, tag: str):
        local_x = self.__scaling * x + self.__canvas_width / 2
        local_y = self.__scaling * -y + self.__canvas_height / 2
        return self.__canvas.create_oval(local_x - radius, local_y + radius , local_x + radius, local_y - radius, fill=color, width=width, tags=tag)

    # draw a canvas image
    def __draw_centered_image(self, x: int, y: int, image, tag: str):
        local_x = self.__scaling * x + self.__canvas_width / 2
        local_y = self.__scaling * -y + self.__canvas_height / 2
        return self.__canvas.create_image(local_x - image.width() / 2, local_y - image.height() / 2, image=image, anchor="nw", tags=tag)

    # handle window resize event
    def __resize_handler(self, event):
        if self.__first_resize:
            if (event.width == self.__IMAGE_SIZE) and (event.height == self.__IMAGE_SIZE):
                self.__first_resize = False
            return
        # store new canvas dimensions
        self.__canvas_width = event.width
        self.__canvas_height = event.height
        # move starting point and destinations
        self.__move_centered_item("start_point", 0, 0, self.__DOT_RADIUS*2, self.__DOT_RADIUS*2)
        for i in range(len(self.__destinations)):
            self.__move_centered_item("destination_out_"+str(i), self.__destinations[i][0], self.__destinations[i][1], self.__DOT_RADIUS*2, self.__DOT_RADIUS*2)
            self.__move_centered_item("destination_in_"+str(i), self.__destinations[i][0], self.__destinations[i][1], self.__DOT_RADIUS, self.__DOT_RADIUS)
