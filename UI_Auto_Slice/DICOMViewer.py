import os
from typing import Tuple
import pydicom
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import pickle

from analysis_script import calculate_metrics
from find_reccomended_image import find_recc_file

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Toplevel, Frame, Label, ttk, Button, messagebox
from matplotlib.patches import Circle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Set to true only if you are using linux
LINUX_MODE = True


from functions import ls_circle, \
    detect_knee_bounding_boxes, \
    process_image


""" DICOM LOADER
    root - A TKinter root object, i.e. our root GUI Object
    dicom_folder - A the folder path for the dicom_folder"""

class DICOMLoader:
    def __init__(self, root: tk.Tk, folder_path: str) -> None:
        self.folder_path = folder_path
        self.cache_file = f"{folder_path}_cache.pkl"

        self.root = root
        self.root.title("Loading DICOM Files...")
        self.root.geometry('500x100')
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        self.dicom_folder = folder_path
        self.dicom_filename_array = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.dcm')]
        self.dicom_filename_array.sort()

        self.recc_file_no = 0

        self.progress_frame = Frame(root)
        self.progress_frame.pack(pady=10)

        self.label_title = Label(self.progress_frame, text="Loading DICOM Files...", font=('Helvetica', 14, 'bold'))
        self.label_title.pack()

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress_bar.pack()

        self.label_message = Label(self.progress_frame, text="Processing...", font=('Helvetica', 12))
        self.label_message.pack()

        self.recc_file_no = 0

        """ CACHING SECTION
            Store results calculated already in file in the dicom_folder provided """

        if os.path.exists(self.cache_file):
            self.label_title.config(text="Loading from Cache...")

            try:
                self.multichannel_image_array, self.dicom_filename_array, self.dicom_data, self.recc_file_no = self.load_from_cache()

            except:
                self.multichannel_image_array, self.bounding_boxes, self.dicom_data = self.process_dicom_files()

        else:
            self.multichannel_image_array, self.bounding_boxes, self.dicom_data = self.process_dicom_files()

        self.root.after(100, self.close_window)  # Close window after 100ms (adjust as needed)


    """ Hide the current window for DICOMViewer to show """
    def close_window(self):
        self.root.withdraw()  # Hide the loading window
        self.show_viewer()  # Show the DICOM viewer


    def show_viewer(self):
        viewer_root = Toplevel()
        viewer_root.title("DICOM Viewer")
        viewer_root.protocol("WM_DELETE_WINDOW", self.exit_application)  # Handle close event

        viewer = DICOMViewer(viewer_root, self.multichannel_image_array, self.dicom_filename_array, self.dicom_data, self.recc_file_no)
        _ = viewer


    def exit_application(self):
        self.root.destroy()  # Destroy the main window to exit the application


    """ LOAD ONE DICOM FILE """
    def load_dicom(self, file_path: str) -> Tuple:
        dicom_data = pydicom.dcmread(file_path)
        bounding_boxes, _, edge_points = detect_knee_bounding_boxes(dicom_data)
        multichannel_image = process_image(dicom_data)

        file_metrics = None

        if len(bounding_boxes) == 2:
            metrics = calculate_metrics(dicom_data.pixel_array, bounding_boxes)

            file_metrics = {
                'file_name': os.path.basename(file_path),
                'metrics': metrics
            }

        return os.path.basename(file_path), bounding_boxes, multichannel_image, edge_points, file_metrics, dicom_data


    """ PROCESS ALL DICOM FILES IN DIR AND SHOWS PROGRESS BAR """
    def process_dicom_files(self):
        multichannel_image_array = []
        bounding_boxes = []
        file_names = []
        metrics = []
        dicom_data = []

        for i, file_path in enumerate(self.dicom_filename_array):
            result = self.load_dicom(file_path)

            file_name, bounding_boxes, multichannel_image, _, file_metrics, dicom_data_file = result
            multichannel_image_array.append(multichannel_image)
            bounding_boxes.append(bounding_boxes)
            file_names.append(file_name)
            dicom_data.append(dicom_data_file)

            if file_metrics:
                metrics.append(file_metrics)

            self.progress_bar['value'] = (i + 1) / len(self.dicom_filename_array) * 100
            self.root.update_idletasks()

        self.label_message.config(text="Processing completed. Please close this window if it hasn't automatically.")

        self.recc_file_no = find_recc_file(self.folder_path, metrics)

        self.dicom_data = dicom_data

        # Ask user if they want to cache the processed data
        self.ask_to_cache_data(multichannel_image_array, self.dicom_filename_array, self.dicom_data, self.recc_file_no)

        return multichannel_image_array, bounding_boxes, dicom_data


    """ CACHE FUNCTIONS FOR STORING CACLULATED DATA """
    def ask_to_cache_data(self, multichannel_image_array, dicom_filename_array, dicom_data, recc_file_no):
        if messagebox.askyesno("Cache Data", "Do you want to cache the processed data?\n This will make next run much quicker. \
            Please Delete the Cache file loacted in the dicom folder provided manually should you want to remove the cache."):
            self.save_to_cache(multichannel_image_array, dicom_filename_array, dicom_data, recc_file_no)


    def save_to_cache(self, multichannel_image_array, dicom_filename_array, dicom_data, recc_file_no):
        with open(self.cache_file, 'wb') as f:
            pickle.dump((multichannel_image_array, dicom_filename_array, dicom_data, recc_file_no), f)


    def load_from_cache(self):
        with open(self.cache_file, 'rb') as f:
            return pickle.load(f)


class DICOMViewer:
    def __init__(self, root, multichannel_image_array, dicom_filename_array, dicom_data_array, recc_index: int | None = 0):
        recc_def_text = ""
        if recc_index is None or recc_index < 0:
            recc_index = 0
            recc_def_text="Could not find a suitable image, please manually select"


        self.root = root
        self.multichannel_image_array = multichannel_image_array
        self.dicom_filename_array = dicom_filename_array
        self.dicom_data_array = dicom_data_array
        self.recc_index = recc_index
        self.index = recc_index

        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.multichannel_image_array[self.index], cmap='gray')
        self.dicom_data = self.multichannel_image_array[self.index]
        self.ax.set_title(f'Image {self.index + 1}/{len(self.dicom_filename_array)}')

        self.canvas_frame = Frame(self.root, width=600, height=600)
        self.canvas_frame.pack(side='left', fill='both', expand=True)
        self.canvas_frame.pack_propagate(False)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        self.control_frame = Frame(self.root, bg='lightblue', width=200)
        self.control_frame.pack(side='right', fill='y')
        self.control_frame.pack_propagate(False)

        self.label = Label(self.control_frame, text="Choose Correct Slice", pady=10, wraplength=180)
        self.label.pack(pady=(0, 10), fill='x')

        self.sub_frame = Frame(self.control_frame, bg='lightblue', highlightbackground="lightblue", highlightthickness=5)
        self.sub_frame.pack(pady=0, padx=0, fill='both', expand=True)

        self.recommended_label = Label(self.sub_frame, text=recc_def_text, pady=10, wraplength=180, fg='red')
        self.recommended_label.pack(pady=(0, 10), fill='x')

        self.button_next = Button(self.sub_frame, text="Next", command=self.switch_to_bounding_box_selection)
        self.button_next.pack(pady=10, padx=20, fill='x')

        self.root.bind('<KeyPress-Up>', self.on_key_press)
        self.root.bind('<KeyPress-Down>', self.on_key_press)
        self.root.bind('<KeyRelease-Up>', self.on_key_release)
        self.root.bind('<KeyRelease-Down>', self.on_key_release)

        if LINUX_MODE:
            self.root.bind('<Button-4>', self.linux_on_mouse_scroll_up)
            self.root.bind('<Button-5>', self.linux_on_mouse_scroll_down)

        else:
            self.root.bind('<MouseWheel>', self.on_mouse_scroll)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)  # Handle close event

        self.update_image()

        messagebox.showinfo(title="Scroll information", message="Use up and down keys to navigate the images")


    """ UPDATES IMAGE ON KEY PRESS """
    def update_image(self):
        self.im.set_data(self.multichannel_image_array[self.index])
        self.dicom_data = self.dicom_data_array[self.index]
        self.ax.set_title(f'Image {self.index + 1}/{len(self.dicom_filename_array)}')
        self.recommended_label.config(text="Recommended File" if self.index == self.recc_index else "")
        self.canvas.draw_idle()


    """ KEY PRESS HANDLERS """
    def on_key_press(self, event):
        if event.keysym == 'Up':
            self.prev_image()
        elif event.keysym == 'Down':
            self.next_image()

    # needed
    def on_key_release(self, event):
        pass


    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.update_image()


    def next_image(self):
        if self.index < len(self.dicom_filename_array) - 1:
            self.index += 1
            self.update_image()


    def on_mouse_scroll(self, event):
        print("Working")
        if event.delta > 0:
            self.prev_image()
        elif event.delta < 0:
            self.next_image()


    def linux_on_mouse_scroll_up(self, event):
        self.prev_image()


    def linux_on_mouse_scroll_down(self, event):
        self.next_image()


    def exit_application(self):
        self.root.destroy()  # Destroy the viewer window to exit the application
        # self.root.withdraw()  # Hide the loading window


    def switch_to_bounding_box_selection(self):
        self.bounding_boxes, _, self.edge_points = detect_knee_bounding_boxes(self.dicom_data)

        if len(self.bounding_boxes) != 2:
            self.bounding_boxes = None
            messagebox.showerror("Error", "These slice is of poor quality we did not find two bounding boxes. \
                Please select another")
            return

        for widget in self.sub_frame.winfo_children():
            widget.destroy()

        self.multichannel_image = process_image(self.dicom_data)  # Preprocess the image?

        self.root.unbind('<KeyPress-Up>')
        self.root.unbind('<KeyPress-Down>')
        self.root.unbind('<KeyRelease-Up>')
        self.root.unbind('<KeyRelease-Down>')

        if LINUX_MODE:
            self.root.unbind('<Button-4>')
            self.root.unbind('<Button-5>')

        else:
            self.root.unbind('<MouseWheel>')

        self.selected_box_index = None

        # Control buttons
        button_left = tk.Button(self.sub_frame, text="Left Knee", command=lambda: self.on_enter(0))
        button_right = tk.Button(self.sub_frame, text="Right Knee", command=lambda: self.on_enter(1))
        button_next = tk.Button(self.sub_frame, text="Next", command=lambda: self.switch_to_line_placement()) ## OWN FUNC

        button_left.pack(pady=10, padx=20, fill=tk.X)
        button_right.pack(pady=10, padx=20, fill=tk.X)
        button_next.pack(pady=10, padx=20, fill=tk.X)

        for i, (x, y, w, h) in enumerate(self.bounding_boxes):
            self.ax.add_patch(plt.Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none'))
            plt.text(x, y, f'Box {i+1}', color='r', fontsize=10, verticalalignment='top')

        plt.axis('off')

        self.canvas.draw_idle()

        self.test_d = []


    def event_on_click_points(self, event):
        print(f'Clicked at x={event.xdata}, y={event.ydata}')
        if event.inaxes is not self.ax:
            print(f"Event in axes: {event.inaxes}, Expected axes: {self.ax}")
            return

        (x1, x2), (y1, y2) = self.line.get_data()
        p1, p2 = (x1, y1), (x2, y2)

        # Compute position relative to the line
        position = (p2[0] - p1[0]) * (event.ydata - p1[1]) - (p2[1] - p1[1]) * (event.xdata - p1[0])

        if position > 0:
            self.points_left.append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, 'go', markersize=5)  # green point
        else:
            self.points_right.append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, 'ro', markersize=5)  # red point


        if(len(self.points_left) >= 3):
            xx_l = [item[0] for item in self.points_left]
            yy_l = [item[1] for item in self.points_left]

            xofs_l, yofs_l, R_l = ls_circle(np.array(xx_l), np.array(yy_l))

            if self.circle_l is not None:
                self.circle_l.remove()

            self.circle_l = Circle((xofs_l, yofs_l), R_l, edgecolor='green', facecolor='none', linewidth=2)
            # Add the circle to the plot
            self.ax.add_patch(self.circle_l)

        if(len(self.points_right) >= 3):
            xx_r = [item[0] for item in self.points_right]
            yy_r = [item[1] for item in self.points_right]

            xofs_l, yofs_l, R_l = ls_circle(np.array(xx_r), np.array(yy_r))

            if self.circle_r is not None:
                self.circle_r.remove()

            self.circle_r = Circle((xofs_l, yofs_l), R_l, edgecolor='red', facecolor='none', linewidth=2)
            # Add the circle to the plot
            self.ax.add_patch(self.circle_r)

        if(len(self.points_right) >= 3 and len(self.points_left) >= 3):
            x1, y1 = self.circle_l.center
            x2, y2 = self.circle_r.center

            if self.center_line is not None:
                self.center_line.remove()

            self.center_line, = self.ax.plot([x1, x2], [y1, y2], 'purple')


        self.canvas.draw_idle()


    def event_on_click_line(self, event):
        print(f'Clicked at x={event.xdata}, y={event.ydata}')
        if event.inaxes is not self.ax:
            print(f"Event in axes: {event.inaxes}, Expected axes: {self.ax}")
            return

        if len(self.line_points) >= 3:
            (self.line_points[0]).remove()
            (self.line_points[1]).remove()
            (self.line_points[2]).remove()
            self.line_points.clear()

            if self.line is not None:
                self.line.remove()

        point, = self.ax.plot(event.xdata, event.ydata, 'ro', markersize=6)
        self.line_points.append(point)

        if len(self.line_points) == 2:
            x1, y1 = self.line_points[0].get_data()
            x2, y2 = self.line_points[1].get_data()

            # Draw line between the two points
            self.line, = self.ax.plot([x1[0], x2[0]], [y1[0], y2[0]], 'b-')  # 'b-' specifies a blue line

        self.canvas.draw_idle()


    def switch_to_line_placement(self):

        if self.selected_box_index == None:
            messagebox.showerror("Error", "Please select knee first")
            return

        # Clear the previous canvas and buttons
        for widget in self.sub_frame.winfo_children():
            widget.destroy()

        self.line_points = []
        self.line = None
        self.cid_click = self.canvas.mpl_connect('button_press_event', self.event_on_click_line)

        button_next = tk.Button(self.sub_frame, text="Next", command=lambda: self.switch_to_point_selection()) ## OWN FUNC
        button_next.pack(pady=10, padx=20, fill=tk.X)


        self.label.config(text="Draw Line to Divide Knew into Medial and Lateral Frames")


    def switch_to_point_selection(self):

        if len(self.line_points) < 2:
            messagebox.showerror("Error", "Draw line first")
            return

        if len(self.line_points) == 2:
            messagebox.showerror("Error", "Draw center first")
            return

        (self.line_points[0]).remove()
        (self.line_points[1]).remove()
        self.center = self.line_points[2]
        self.center.set_color("yellow")

        self.line_points.clear()
        self.canvas.draw_idle()

        self.points_left = []
        self.points_right = []
        self.center_line = None

        self.circle_l = None
        self.circle_r = None

        # Clear the previous canvas and buttons
        # self.canvas.get_tk_widget().pack_forget()
        for widget in self.sub_frame.winfo_children():
            widget.destroy()


        # Binding a mouse event
        self.canvas.mpl_disconnect(self.cid_click)
        # self.cid = self.canvas.mpl_connect('button_press_event', self.event_on_click_points)

        self.label.config(text="Select Points")
        button_next = tk.Button(self.sub_frame, text="Next", command=lambda: self.switch_to_resize_circles()) ## OWN FUNC
        button_next.pack(pady=10, padx=20, fill=tk.X)

        (x1, x2), (y1, y2) = self.line.get_data()
        p1, p2 = (x1, y1), (x2, y2)

        np_p1 = np.array(p1)
        np_p2 = np.array(p2)

        # Direction vector of the line
        vector = np_p2 - np_p1

        # Normalize the direction vector
        direction_vector = vector / np.linalg.norm(vector)

        min_l_top = min_r_top = float('inf')

        min_l_point_top = None
        min_r_point_top = None

        min_l = min_r = 0

        min_l_point = None
        min_r_point = None

        center_point = (self.center.get_xdata()[0], self.center.get_ydata()[0])
        np_center = np.array(center_point)

        for point in self.filtered_points:
            px, py = point

            position = (p2[0] - p1[0]) * (py - p1[1]) - (p2[1] - p1[1]) * (px - p1[0])
            np_point = np.array(point)

            # Compute the projection length
            projection_length = abs(np.dot(np_point - np_p1, direction_vector))

            # Compute the projected point
            # p_proj = np_p1 + projection_length * direction_vector

            center_to_point_vector = np_center - np_point

            center_to_point_vector_magnitude = np.linalg.norm(center_to_point_vector)

            dot_product = np.dot(center_to_point_vector, vector)

            cos_theta = dot_product / (center_to_point_vector_magnitude * np.linalg.norm(vector))

            # Ensure the cosine value is within the valid range [-1, 1]
            cos_theta = np.clip(cos_theta, -1.0, 1.0)

            # Compute the angle in radians
            theta_rad = np.arccos(cos_theta)

            # Convert the angle to degrees
            theta_deg = np.degrees(theta_rad)

            if position > 0:
                self.points_left.append(point)

                if abs(theta_deg - 30) < min_l_top:
                    min_l_top = abs(theta_deg - 30)
                    min_l_point_top = point

                if min_l < projection_length:
                    min_l = projection_length
                    min_l_point = point
                    # self.ax.plot(px, py, 'ro', markersize=3)  # red point


            else:
                self.points_right.append(point)

                if abs(theta_deg - 30) < min_r_top:
                    min_r_top = abs(theta_deg - 30)
                    min_r_point_top = point

                if min_r < projection_length:
                    min_r = projection_length
                    min_r_point = point
                    # self.ax.plot(px, py, 'go', markersize=3)  # green point

        # print(min_l_point, min_r_point)

        self.points_drawn_l = []
        self.points_drawn_r = []

        point_1, = self.ax.plot(min_l_point[0], min_l_point[1], 'go', markersize=5)  # red point
        point_r, = self.ax.plot(min_r_point[0], min_r_point[1], 'ro', markersize=5)  # green point

        self.points_drawn_l.append(point_1)
        self.points_drawn_r.append(point_r)

        point_1, = self.ax.plot(min_l_point_top[0], min_l_point_top[1], 'go', markersize=5)  # red point
        point_r, = self.ax.plot(min_r_point_top[0], min_r_point_top[1], 'ro', markersize=5)  # green point

        self.points_drawn_l.append(point_1)
        self.points_drawn_r.append(point_r)
        # Find the angle between points

        min_l_mid = min_r_mid = float('inf')
        min_l_first = min_r_first = float('inf')
        min_l_last = min_r_last = float('inf')

        min_l_point_mid = None
        min_r_point_mid = None
        min_l_point_first = None
        min_r_point_last = None

        np_l_bot = np.array(min_l_point)
        np_l_top = np.array(min_l_point_top)

        vec1 = np_l_top - np_center
        vec2 = np_l_bot - np_center

        dot_product = np.dot(vec1, vec2)

        mag_d1 = np.linalg.norm(vec1)
        mag_d2 = np.linalg.norm(vec2)

        # Compute the cosine of the angle using the dot product formula
        cos_theta = dot_product / (mag_d1 * mag_d2)

        # Ensure the cosine value is within the valid range [-1, 1]
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        # Compute the angle in radians
        theta_rad = np.arccos(cos_theta)

        # Convert the angle to degrees
        theta_deg_goal = np.degrees(theta_rad)
        theta_deg_goal_first = theta_deg_goal * (0.6)
        theta_deg_goal_last = theta_deg_goal * (0.9)

        for point in self.points_left:
            np_point = np.array(point)
            center_to_point_vector = np_point - np_center

            center_to_point_vector_magnitude = np.linalg.norm(center_to_point_vector)

            dot_product = np.dot(center_to_point_vector, vec1)

            cos_theta = dot_product / (center_to_point_vector_magnitude * np.linalg.norm(vec1))

            # Ensure the cosine value is within the valid range [-1, 1]
            cos_theta = np.clip(cos_theta, -1.0, 1.0)

            # Compute the angle in radians
            theta_rad = np.arccos(cos_theta)

            # Convert the angle to degrees
            theta_deg = np.degrees(theta_rad)

            if abs(theta_deg - theta_deg_goal // 2) < min_l_mid:
                min_l_mid = abs(theta_deg - theta_deg_goal // 2)
                min_l_point_mid = point

            if 0 <= (theta_deg_goal_first - theta_deg) < min_l_first:
                min_l_first = theta_deg_goal_first - theta_deg
                min_l_point_first = point

            if 0 <= (theta_deg_goal_last - theta_deg) < min_l_last:
                min_l_last = theta_deg_goal_last - theta_deg
                min_l_point_last = point

        min_r_point_mid = None
        min_r_point_mid = None

        np_r_bot = np.array(min_r_point)
        np_r_top = np.array(min_r_point_top)

        vec1 = np_r_top - np_center
        vec2 = np_r_bot - np_center

        dot_product = np.dot(vec1, vec2)

        mag_d1 = np.linalg.norm(vec1)
        mag_d2 = np.linalg.norm(vec2)

        # Compute the cosine of the angle using the dot product formula
        cos_theta = dot_product / (mag_d1 * mag_d2)

        # Ensure the cosine value is within the valid range [-1, 1]
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        # Compute the angle in radians
        theta_rad = np.arccos(cos_theta)

        # Convert the angle to degrees
        theta_deg_goal = np.degrees(theta_rad)
        theta_deg_goal_first = theta_deg_goal * (0.6)
        theta_deg_goal_last = theta_deg_goal * (0.9)

        # print(theta_deg_goal, theta_deg_goal_first, theta_deg_goal_last)

        for point in self.points_right:
            np_point = np.array(point)
            center_to_point_vector = np_point - np_center

            center_to_point_vector_magnitude = np.linalg.norm(center_to_point_vector)

            dot_product = np.dot(center_to_point_vector, vec1)

            cos_theta = dot_product / (center_to_point_vector_magnitude * np.linalg.norm(vec1))

            # Ensure the cosine value is within the valid range [-1, 1]
            cos_theta = np.clip(cos_theta, -1.0, 1.0)

            # Compute the angle in radians
            theta_rad = np.arccos(cos_theta)

            # Convert the angle to degrees
            theta_deg = np.degrees(theta_rad)

            if abs(theta_deg - theta_deg_goal // 2) < min_r_mid:
                # print("m", theta_deg)
                min_r_mid = abs(theta_deg - theta_deg_goal // 2)
                min_r_point_mid = point

            if 0 <= (theta_deg - theta_deg_goal_first) < min_r_first:
                # print("r", theta_deg)
                min_r_first = theta_deg - theta_deg_goal_first
                min_r_point_first = point

            if 0 <= (theta_deg - theta_deg_goal_first) < min_r_last:
                # print("l", theta_deg)
                min_r_last = theta_deg - theta_deg_goal_last
                min_r_point_last = point

        point1, = self.ax.plot(min_l_point_mid[0], min_l_point_mid[1], 'go', markersize=5)  # red point
        point2, = self.ax.plot(min_l_point_first[0], min_l_point_first[1], 'go', markersize=5)  # red point
        point3, = self.ax.plot(min_l_point_last[0], min_l_point_last[1], 'go', markersize=5)  # red point

        self.points_drawn_l.append(point1)
        self.points_drawn_l.append(point2)
        self.points_drawn_l.append(point3)

        point1, = self.ax.plot(min_r_point_mid[0], min_r_point_mid[1], 'ro', markersize=5)  # red point
        point2, = self.ax.plot(min_r_point_first[0], min_r_point_first[1], 'ro', markersize=5)  # red point
        point3, = self.ax.plot(min_r_point_last[0], min_r_point_last[1], 'ro', markersize=5)  # red point

        self.points_drawn_r.append(point1)
        self.points_drawn_r.append(point2)
        self.points_drawn_r.append(point3)

        self.canvas.draw_idle()


    def switch_to_resize_circles(self):


        # Clear the previous canvas and buttons
        # self.canvas.get_tk_widget().pack_forget()
        for widget in self.sub_frame.winfo_children():
            widget.destroy()


        self.selected_point = None
        # Binding a mouse event
        self.cid = self.canvas.mpl_connect('button_press_event', self.event_on_press)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.event_on_release)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.event_on_drag)

        self.center_x, self.center_y = self.center.get_xdata()[0], self.center.get_ydata()[0]

        self.line.remove()
        self.center.remove()

        xx_l = [item[0] for item in self.points_left]
        yy_l = [item[1] for item in self.points_left]

        xofs_l, yofs_l, R_l = ls_circle(np.array(xx_l), np.array(yy_l))

        self.circle_l = Circle((xofs_l, yofs_l), R_l, edgecolor='green', facecolor='none', linewidth=2)
            # Add the circle to the plot
        self.ax.add_patch(self.circle_l)

        xx_r = [item[0] for item in self.points_right]
        yy_r = [item[1] for item in self.points_right]

        xofs_r, yofs_r, R_r = ls_circle(np.array(xx_r), np.array(yy_r))

        self.circle_r = Circle((xofs_r, yofs_r), R_r, edgecolor='red', facecolor='none', linewidth=2)
            # Add the circle to the plot
        self.ax.add_patch(self.circle_r)

        self.center_line, = self.ax.plot([xofs_r, xofs_l], [yofs_r, yofs_l], 'purple')
        self.center_points, = self.ax.plot([xofs_r, xofs_l], [yofs_r, yofs_l], color="purple", marker="o", markersize="4")

        center_r = np.array((xofs_l, yofs_l))
        center_l = np.array((xofs_r, yofs_r))
        d = center_r - center_l
        d_perp = np.array([-d[1], d[0]])

        # Normalize the perpendicular direction vector for consistent scaling
        d_perp_normalized = d_perp / np.linalg.norm(d_perp)

        # Define the self.line_len for plotting the line (for visualization purposes)
        self.line_len = 50
        # Plot the perpendicular line through point P
        self.og_per_line, = self.ax.plot([self.center_x - self.line_len*d_perp_normalized[0], self.center_x + self.line_len*d_perp_normalized[0]],
            [self.center_y - self.line_len*d_perp_normalized[1], self.center_y + self.line_len*d_perp_normalized[1]], 'black', label='Perpendicular Line through P')

        self.per_line = None

        self.label1 = tk.Label(self.sub_frame, text=f"Original Centers (L, M):  ({xofs_r:.2f}, {yofs_r:.2f}), ({xofs_l:.2f}, {yofs_l:.2f})", pady=10, wraplength=180)
        self.label2 = tk.Label(self.sub_frame, text=f"New Center: NA", pady=10, wraplength=180)
        self.label3 = tk.Label(self.sub_frame, text=f"Angular Diff between original Cobbs Axis: NA", pady=10, wraplength=180)
        self.label1.pack(pady=(0, 10), fill=tk.X)
        self.label2.pack(pady=(0, 10), fill=tk.X)
        self.label3.pack(pady=(0, 10), fill=tk.X)

        self.label.config(text="Resize Points")

        self.canvas.draw_idle()

    def find_closest_point(self, x, y):
        closest_point = None
        closest_distance = float('inf')


        points = [(point, point.get_xdata()[0], point.get_ydata()[0]) for point in self.points_drawn_l + self.points_drawn_r]

        for i, (point, px, py) in enumerate(points):
            distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_point = point

        return closest_point, closest_distance

    def event_on_press(self, event):
        # Find the closest point
        closest_point, distance = self.find_closest_point(event.xdata, event.ydata)

        print(distance)
        if distance < 3:
            self.selected_point = closest_point
            # Calculate the offset between the click position and the point position
            x, y = self.selected_point.get_xdata()[0], self.selected_point.get_ydata()[0]
            self.offset = [x - event.xdata, y - event.ydata]

        print(event.xdata, event.ydata)

        self.start_x = event.xdata
        self.start_y = event.ydata

    def event_on_release(self, event):
        print("Release")
        self.selected_point = None


    def event_on_drag(self, event):
        if not self.selected_point:
            return

        print("Drag", self.selected_point)

        dx = event.xdata - self.start_x
        dy = event.ydata - self.start_y
        x, y = self.selected_point.get_data()

        self.selected_point.set_data(x + dx, y + dy)
        # self.selected_point.set_data(event.x + self.offset[0], event.y + self.offset[1])
        print(event.x, event.y)

        self.start_x = event.xdata
        self.start_y = event.ydata

        # Delete the old circles and line
        self.circle_l.remove()
        self.circle_r.remove()
        self.center_line.remove()
        self.center_points.remove()

        if self.per_line:
            self.per_line.remove()

        xx_l = [item.get_xdata()[0] for item in self.points_drawn_l]
        yy_l = [item.get_ydata()[0] for item in self.points_drawn_l]

        xofs_l, yofs_l, R_l = ls_circle(np.array(xx_l), np.array(yy_l))

        self.circle_l = Circle((xofs_l, yofs_l), R_l, edgecolor='green', facecolor='none', linewidth=2)
            # Add the circle to the plot
        self.ax.add_patch(self.circle_l)

        xx_r = [item.get_xdata()[0] for item in self.points_drawn_r]
        yy_r = [item.get_ydata()[0] for item in self.points_drawn_r]

        xofs_r, yofs_r, R_r = ls_circle(np.array(xx_r), np.array(yy_r))

        self.circle_r = Circle((xofs_r, yofs_r), R_r, edgecolor='red', facecolor='none', linewidth=2)
            # Add the circle to the plot
        self.ax.add_patch(self.circle_r)

        self.center_line, = self.ax.plot([xofs_r, xofs_l], [yofs_r, yofs_l], 'purple')
        self.center_points, = self.ax.plot([xofs_r, xofs_l], [yofs_r, yofs_l], color="purple", marker="o", markersize="4")

        center_r = np.array((xofs_l, yofs_l))
        center_l = np.array((xofs_r, yofs_r))
        d = center_r - center_l
        d_perp = np.array([-d[1], d[0]])

        # Normalize the perpendicular direction vector for consistent scaling
        d_perp_normalized = d_perp / np.linalg.norm(d_perp)

        # Plot the perpendicular line through point P
        self.per_line, = self.ax.plot([self.center_x - self.line_len*d_perp_normalized[0], self.center_x + self.line_len*d_perp_normalized[0]],
            [self.center_y - self.line_len*d_perp_normalized[1], self.center_y + self.line_len*d_perp_normalized[1]], 'y-', label='Perpendicular Line through P')

        (og_x1, og_x2), (og_y1, og_y2) = self.og_per_line.get_data()
        (x1, x2), (y1, y2) = self.per_line.get_data()

        p1 = np.array((og_x1, og_y1))
        p2 = np.array((og_x2, og_y2))
        p3 = np.array((x1, y1))
        p4 = np.array((x2, y2))

        line_1 = p1 - p2
        line_2 = p3 - p4

        dot_product = np.dot(line_1, line_2)

        cos_theta = dot_product / (np.linalg.norm(line_1) * np.linalg.norm(line_2))

        # Ensure the cosine value is within the valid range [-1, 1]
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        # Compute the angle in radians
        theta_rad = np.arccos(cos_theta)

        # Convert the angle to degrees
        theta_deg = np.degrees(theta_rad)

        self.label2.config(text=f"New Centers (L, M): ({xofs_r:.2f}, {yofs_r:.2f}), ({xofs_l:.2f}, {yofs_l:.2f})")
        self.label3.config(text=f"Angular Diff between original Cobbs Axis: {theta_deg:.2f}")

        self.canvas.draw_idle()


    def on_enter(self, selected_box_index):
        self.ax.clear()

        if 0 <= selected_box_index < len(self.bounding_boxes):
            self.selected_box_index = selected_box_index
            x, y, w, h = self.bounding_boxes[selected_box_index]

            # We are getting min max values of our entire image
            height, width, _ = self.multichannel_image.shape

            # Define padding for our bounding box
            x_padding = w // 2
            y_padding = h // 2

            # Ensure padding doesn't excede the image shape
            x_min = max(0, x - x_padding)
            y_min = max(0, y - y_padding)
            x_max = min(width, x + w + x_padding)
            y_max = min(height, y + h + x_padding)

            cropped_image = self.multichannel_image[y_min:y_max, x_min:x_max]

            # Use the Axes object to show the image
            self.ax.imshow(cropped_image)
            self.ax.axis('off')  # Turn off the axis

            for point in self.test_d:
                point.remove()
                self.test_d = []

            self.filtered_points = []
            # print(filtered_points, "\n", self.edge_points)
            for point in self.edge_points:
                px, py = point

                # Key is to not check point within padded margins but with margins
                if x <= px <= x + w and y <= py <= y + h:
                    self.filtered_points.append((point[0] - x_min, point[1] - y_min))

            # Redraw the canvas where the figure is embedded
            self.canvas.draw_idle()
        else:
            messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
