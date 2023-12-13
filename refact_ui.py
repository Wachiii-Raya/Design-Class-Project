from threading import Thread
import dearpygui.dearpygui as dpg
import serial
import numpy as np
import time


class UiController:
    def __init__(self, serialPort, baudRate):
        self.serialHandler = serial.Serial(serialPort, baudRate)
        self.buffer = self.get_buffer()
        self.currentTime = None
        self.currentStatus = None
        self.currentFileName = None
        self.forceUpperBound = 1000
        self.forceLowerBound = 200
        self.isRunning = False
        
        
    def get_buffer(self):
        buffer = [[0, ''] for _ in range(15)]
        return buffer
    
    
    def clear_buffer(self, buffer):
        for i in range(len(buffer)):
            buffer[i][0] = 0
            buffer[i][1] = ''
            
            
    def add_to_buffer(self, time, status):
        if len(self.buffer) >= 15:
            self.buffer.pop(0)  # Remove the oldest item if the buffer is full
        self.buffer.append([time, status])  # Add the new item
        
        
    def save_buffer_to_file(self, filename):
        studentName = filename.split('.')[0]
        with open(filename, 'w') as f:
            f.write(f"Student Name: {studentName}\n\n")
            f.write('Time  |    Status\n')
            f.write('------------------------------\n')
            for item in self.buffer:
                f.write(f'{item[0]}     |   {item[1]}\n')


    def render(self):
        # use .ini
        dpg.configure_app(init_file="UI_config.ini")
        dpg.set_global_font_scale(1.25)
        with dpg.window(label="Monitor Window", height=400, width=300):
            with dpg.group(horizontal=True):
                # input box for student name and save thae value to a variable self.currentFileName
                dpg.add_text("Student Name:")
                dpg.add_input_text(label="", callback=self.cb_get_student_name, tag="student name")
                
            with dpg.group(horizontal=True):
                # force from FSR
                dpg.add_text("Force from FSR:")
                dpg.add_text("", tag="force FSR")
            
            with dpg.group(horizontal=True):
                # time taken
                dpg.add_text("Time Taken:")
                dpg.add_text("", tag="Time Taken")
                
            with dpg.group(horizontal=True):
                # status
                dpg.add_text("Status:")
                dpg.add_text("", tag="Experiment Status")
                
            with dpg.group(horizontal=True):
                # start button
                dpg.add_button(label="Start", callback=self.cb_start)
                # reset button
                dpg.add_button(label="Reset", callback=self.cb_reset)
                
                
                
    
    def cb_get_student_name(self):
        self.currentFileName = dpg.get_value("student name")
        # print(self.currentFileName)
        
        
    def cb_start(self):
        self.isRunning = True
        self.currentTime = time.time()
        ## Start Thread        


    def cb_reset(self):
        '''Resets the experiment status and the time taken'''
        dpg.set_value("Time Taken", "")
        self.currentTime = None
        self.currentStatus = None
        self.currentFileName = None
        self.isRunning = False
        # clear buffer
        self.clear_buffer(self.buffer)
        # clear input box
        dpg.set_value("student name", "")
        
        
    # def update_serial(self):
    #     '''Updates the serial data from the Arduino, and updates the buffer
    #     with the new data. If the buffer is full, it will pop the oldest data
    #     If the force is out of bounds, it will set the initialCountTimeFlag'''
        
    #     while True:
    #         try:
    #             data = self.serialHandler.readline().decode('utf-8', 'ignore').strip() 


    def ui_init(self):
        dpg.create_context()
        dpg.create_viewport(title='Main UI', width=600, height=600)
        dpg.setup_dearpygui()
    
    
    def ui_draw(self):
        self.render()
        # self.thread_handler()
        
    
    def ui_startRenderer(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        
    def main(self):
        self.ui_init()
        self.ui_draw()
        self.ui_startRenderer()









if __name__ == '__main__':
    uiController = UiController('COM3', 9600)
    # buffer = uiController.get_buffer()
    # # uiController.clear_buffer(buffer)
    # # print(buffer)
    # uiController.add_to_buffer(1, 'hello')
    # uiController.add_to_buffer(2, 'hello')
    # uiController.add_to_buffer(5, 'hello')
    # # print(buffer)
    # print(uiController.buffer)
    # uiController.save_buffer_to_file('test.txt')
    #----------------------test UI----------------------
    uiController.main()
    print(uiController.currentFileName)
        
    
        
   