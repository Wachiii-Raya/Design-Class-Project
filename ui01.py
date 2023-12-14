from threading import Thread
import dearpygui.dearpygui as dpg
import serial
import numpy as np
import time


class UiController:
    def __init__(self, serialPort, baudRate):
        self.serialHandler = serial.Serial(serialPort, baudRate)
        self.startTime = 0
        self.buffer = self.get_buffer()
        self.timeTaken = None
        self.currentStatus = "Running"
        self.currentFileName = None
        self.forceUpperBound = 12
        self.forceLowerBound = 2
        self.isRunning = False
        # self.inProgressFlag = False
        # self.x_axis = self.buffer["time"]
        # # self.x_axis = np.linspace(0, 10, 100)
        # self.y_axis = self.buffer["force"]

    
    def get_buffer(self):
        '''dictinary of time and force'''
        dict_buffer = {"time": np.array([]),
                       "force": np.array([]),
                       "status": np.array([])}
        return dict_buffer

    
    def clear_buffer(self, buffer):
        '''Clears the value in np array in the buffer'''
        buffer["time"] = np.array([])
        buffer["force"] = np.array([])
        buffer["status"] = np.array([])
                
        
    def add_to_buffer(self, time: float, force: float, status: str):
        '''Adds the time and force to the buffer dictionary'''
        # the value is add in the end of the array
        self.buffer["time"] = np.append(self.buffer["time"], time)
        self.buffer["force"] = np.append(self.buffer["force"], force)
        self.buffer["status"] = np.append(self.buffer["status"], self.currentStatus)
        

    def save_buffer_to_file(self, filename):
        '''Saves the buffer to a file'''
        try:
            studentName = filename.split('.')[0]
        except:
            studentName = str("test")
        with open(filename, 'w') as f:
            f.write(f"Student Name: {studentName}\n\n")
            f.write('Time  |   Force   |  Status\n')
            f.write('-----------------------------\n')
            for i in range(len(self.buffer["time"])):
                f.write(f"{self.buffer['time'][i]}      {self.buffer['force'][i]}         {self.buffer['status'][i]}\n")
        f.close()

                
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
                
        
    def thread_record_data(self):
        while True:
            while self.isRunning:
                data = self.serialHandler.readline().decode('utf-8', 'ignore').strip()
                try:
                    data = float(data)
                except:
                    data = 0
                # append data and time taken to buffer
                current_time = time.time()
                self.timeTaken = current_time - self.startTime
                self.add_to_buffer(self.timeTaken, data, self.currentStatus)
                print(self.buffer)
                
                
    def set_status(self):
        while True:
            while self.isRunning:
                try:
                    data = self.buffer["force"][-1]
                except:
                    data = 0
                if (data >= self.forceLowerBound & data < self.forceUpperBound):
                    self.currentStatus = "Start collecing blood"
                    dpg.set_value("Experiment Status", self.currentStatus)
                    time.sleep(3)
                    self.currentStatus = "In progress"
                    dpg.set_value("Experiment Status", self.currentStatus)
                    time.sleep(12)
                    self.currentStatus = "Finished"
                    time.sleep(3)
                if (data < self.forceLowerBound):
                    self.currentStatus = "Force is too low"
                    dpg.set_value("Experiment Status", self.currentStatus)
                if (data > self.forceUpperBound):
                    self.currentStatus = "Force is too high"
                    dpg.set_value("Experiment Status", self.currentStatus)
                print(f"status: {self.currentStatus}")


    def update_ui(self):
        while True:
            while self.isRunning:
                try:
                    data = self.buffer["force"][-1]
                    timeTakenUI = self.buffer["time"][-1]
                except:
                    data = 0
                    timeTakenUI = 0
                dpg.set_value("Time Taken", timeTakenUI)
                dpg.set_value("force FSR", data)
        
        
    def cb_start(self):
        self.isRunning = True
        self.startTime = time.time()


    def cb_reset(self):
        '''Resets the experiment status and the time taken'''
        self.isRunning = False
        # save buffer to file
        self.save_buffer_to_file(self.currentFileName)
        dpg.set_value("Time Taken", "")
        self.currentTime = None
        self.currentStatus = None
        self.currentFileName = None
        self.isRunning = False
        self.inProgressFlag = False
        self.startTime = 0
        # clear buffer
        self.clear_buffer(self.buffer)
        # clear input box
        dpg.set_value("student name", "")
        
        
    def thread_running(self):
        thread_record_data = Thread(target=self.thread_record_data)
        thread_update_ui = Thread(target=self.update_ui)
        thread_status_flag = Thread(target=self.set_status)
        
        
        thread_status_flag.start()
        thread_record_data.start()
        thread_update_ui.start()


    def ui_init(self):
        dpg.create_context()
        dpg.create_viewport(title='Main UI', width=600, height=600)
        dpg.setup_dearpygui()
    
    
    def ui_draw(self):
        self.render()
        self.thread_running()
        
    
    def ui_startRenderer(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        
    def main(self):
        self.ui_init()
        self.ui_draw()
        self.ui_startRenderer()


if __name__ == '__main__':
     #----------------------test UI----------------------
    # uiController = UiController('COM11', 9600)
    # uiController.main()
    # print(uiController.currentFileName)
    serialPort = 'COM11'
    baudRate = 9600
    uiController = UiController(serialPort, baudRate)
    uiController.main()

    
    #----------------------test buffer and file----------------------
    # uiController = UiController('COM3', 9600)
    # uiController.currentStatus = "heo"
    # uiController.add_to_buffer(1, 'hello')
    # uiController.add_to_buffer(2, 'hello')
    # uiController.add_to_buffer(5, 'hello')
    
    # # read the last value of the buffer
    # print(uiController.buffer["time"][-1])
    # print(uiController.buffer["force"][-1])
    
    # print(uiController.buffer)
    # uiController.save_buffer_to_file('test.txt')
    
    
    # print size of np array
    # print(len(uiController.buffer["time"]))
    # uiController.save_buffer_to_file('test.txt')
    # uiController.clear_buffer(buffer)
    # print(buffer)
    # uiController.add_to_buffer(1, 'hello')
    # uiController.add_to_buffer(2, 'hello')
    # uiController.add_to_buffer(5, 'hello')
    # print(buffer)
    # print(uiController.buffer)
    # uiController.save_buffer_to_file('test.txt')
