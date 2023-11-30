from threading import Thread
import dearpygui.dearpygui as dpg
import serial
import numpy as np
import time


class UiCOntroller:
    def __init__(self, serialPort, baudRate):
        self.serialHandler = serial.Serial(serialPort, baudRate)
        # self.buffer = []
        # self.timeAxis = np.arange(0, len(self.buffer), 1)
        # self.resistanceFsrAxis = np.array(self.buffer)
        self.initialCountTimeFlag = False
        # self.resetFlag = False
        self.resistanceFsrUpperBound = 800000
        self.resistanceFsrLowerBound = 50000
        
    
    def render(self):
        with dpg.window(label="Monitor Window", height=400, width=300):
            with dpg.group(horizontal=True):
                dpg.add_text("Resistance from FSR:")
                dpg.add_text("", tag="Resistance FSR")
            with dpg.group(horizontal=True):
                dpg.add_text("Time Taken:")
                dpg.add_text("", tag="Time Taken")
            with dpg.group(horizontal=True):
                dpg.add_text("Status:")
                dpg.add_text("", tag="Experiment Status")
            dpg.add_button(label="Reset", callback=self.cb_reset)
        # with dpg.window(label="Resistance Value", height=400, width=800):
        #         with dpg.plot(label="Plot", height=-1, width=-1):
        #             dpg.add_plot_legend()
        #             x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis",no_tick_labels=True)
        #             y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
        #             dpg.set_axis_limits(y_axis, 0, 102300000)
                    
        #             dpg.add_line_series(self.timeAxis, self.resistanceFsrAxis, label="Resistance FSR", parent="y_axis", tag="tag_plot")
        
                
    
    def cb_reset(self):
        '''Resets the experiment status and the time taken'''
        dpg.set_value("Experiment Status", "Program Running")
        dpg.set_value("Time Taken", 0)
        self.initialCountTimeFlag = False
        # self.resetFlag = True
        # self.buffer = []
        # self.timeAxis = np.arange(0, len(self.buffer), 1)
        # self.resistanceFsrAxis = np.array(self.buffer)
        # dpg.delete_item("tag_plot")
        # dpg.add_line_series(self.timeAxis, self.resistanceFsrAxis, label="Resistance FSR", parent="y_axis", tag="tag_plot")
    
    
    def update_serial(self):
        '''Updates the serial data from the Arduino, and updates the buffer
        with the new data. If the buffer is full, it will pop the oldest data
        If the resistance is out of bounds, it will set the initialCountTimeFlag'''
        
        while True:
            try:
                data = self.serialHandler.readline().decode('utf-8', 'ignore').strip()
                print(f"Serial Data: {data}")
                self.buffer.append(int(data))
                if len(self.buffer) >= 500000:
                    self.buffer.pop(0)
            except Exception as e:
                print(e)
            # check that the resistance is within the bounds
            if (float(data) > float(self.resistanceFsrUpperBound)) or (float(data) < float(self.resistanceFsrLowerBound)):
                self.initialCountTimeFlag = True   
            else:
                self.initialCountTimeFlag = False 
            dpg.set_value("Resistance FSR", data)
        
        
    def count_time(self):
        '''while loop check flag, if flag is true, start counting time. 
        if flag is false, stop counting time. If no new experiment is started, 
        then the time is of the previous experiment.'''

        while True:    
            startTime = time.time()
            while self.initialCountTimeFlag:
                currentTime = time.time()
                timeTaken = currentTime - startTime
                dpg.set_value("Time Taken", timeTaken)
                # if time taken is greater than 10 seconds, warning on status
                if timeTaken > 10:
                    dpg.set_value("Experiment Status", "Warning: Time Exceeded")
                else:
                    dpg.set_value("Experiment Status", "Counting Time")
                time.sleep(0.1)
            dpg.set_value("Time Taken", 0)
            startTime = 0
            dpg.set_value("Experiment Status", "Exert Force on FSR does not reach threshold")   
    
    def thread_handler(self):
        '''Starts the threads for the serial update and the time counting'''
        serialThread = Thread(target=self.update_serial)
        timeThread = Thread(target=self.count_time)
        serialThread.start()
        timeThread.start()
        
        
    def ui_init(self):
        dpg.create_context()
        dpg.create_viewport(title='Main UI', width=600, height=600)
        dpg.setup_dearpygui()
    
    
    def ui_draw(self):
        self.render()
        self.thread_handler()
        
    
    def ui_startRenderer(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
    def main(self):
        self.ui_init()
        self.ui_draw()
        self.ui_startRenderer()


        
        
        
if  __name__ == "__main__":
    #----------------Test: UI class----------------#
    uiHandler = UiCOntroller("COM6", 9600)
    uiHandler.main()
    
    