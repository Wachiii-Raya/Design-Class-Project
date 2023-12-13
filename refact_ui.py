from threading import Thread
import dearpygui.dearpygui as dpg
import serial
import numpy as np
import time


class UiController:
    def __init__(self, serialPort, baudRate):
        self.serialHandler = serial.Serial(serialPort, baudRate)
        self.buffer = self.get_buffer()
        self.timeTaken = None
        self.currentStatus = None
        self.currentFileName = None
        self.forceUpperBound = 12
        self.forceLowerBound = 2
        self.isRunning = False
        self.inProgressFlag = False
        self.x_axis = self.buffer["time"]
        # self.x_axis = np.linspace(0, 10, 100)
        self.y_axis = self.buffer["force"]

    
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
                
        
    def add_to_buffer(self, time: float, force: float):
        '''Adds the time and force to the buffer dictionary'''
        # the value is add in the end of the array
        self.buffer["time"] = np.append(self.buffer["time"], time)
        self.buffer["force"] = np.append(self.buffer["force"], force)
        self.buffer["status"] = np.append(self.buffer["status"], self.currentStatus)
        

    def save_buffer_to_file(self, filename):
        '''Saves the buffer to a file'''
        studentName = filename.split('.')[0]
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
        # plot
        with dpg.window(label="force Value", height=400, width=800):
            with dpg.plot(label="Plot", height=-1, width=-1):
                dpg.add_plot_legend()
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis",no_tick_labels=True)
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
                dpg.set_axis_limits(y_axis, 0, 102300000)
                dpg.add_line_series(self.x_axis, self.y_axis, label="force FSR", parent="y_axis", tag="tag_plot")
                
    
    def cb_get_student_name(self):
        self.currentFileName = dpg.get_value("student name")
                
        
    def thread_record_data(self, start_time):
        while True:
            while self.isRunning:
                data = self.serialHandler.readline().decode('utf-8', 'ignore').strip()
                print(f"Serial Data: {data}")
                # append data and time taken to buffer
                current_time = time.time()
                self.timeTaken = current_time - start_time
                self.add_to_buffer(self.timeTaken, data)


    def update_ui(self, start_time):
        while True:
            while self.isRunning:
                data = self.serialHandler.readline().decode('utf-8', 'ignore').strip()
                current_time = time.time()
                timeTakenUI = current_time - start_time
                dpg.set_value("Time Taken", timeTakenUI)
                dpg.set_value("force FSR", data)
                if (float(data) > self.forceUpperBound & self.inProgressFlag == False):
                    self.currentStatus = "Force is too high"
                    dpg.set_value("Experiment Status", self.currentStatus)
                elif (float(data) < self.forceLowerBound & self.inProgressFlag == False):
                    self.currentStatus = "Force is too low"
                    dpg.set_value("Experiment Status", self.currentStatus)
                else:
                    self.currentStatus = "Start collecing blood"
                    dpg.set_value("Experiment Status", self.currentStatus)
                    self.inProgressFlag = True
                    time.sleep(3)
                    dpg.set_value("Experiment Status", "In progress")
                    time.sleep(12)
                    self.currentStatus = "Time is up!"
        
        
    def thread_running(self, start_time):
        thread_record_data = Thread(target=self.thread_record_data, args=(start_time,))
        thread_update_ui = Thread(target=self.update_ui, args=(start_time,))
        thread_record_data.start()
        thread_update_ui.start()
        
        
    def cb_start(self):
        self.isRunning = True
        start_time = time.time()
        self.thread_running(start_time)


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
        # clear buffer
        self.clear_buffer(self.buffer)
        # clear input box
        dpg.set_value("student name", "")
            

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


    def ui_init(self):
        dpg.create_context()
        dpg.create_viewport(title='Main UI', width=600, height=600)
        dpg.setup_dearpygui()
    
    
    def ui_draw(self):
        self.render()
        
    
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
   
        
    
        
   