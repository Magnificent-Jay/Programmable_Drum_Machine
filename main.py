"""
Programmable drum machine

The idea for this project was gotten from "Tkinter GUI Application Development Blueprints" by Bhaskar Chaudhary.
The original project was done using tkinter. This version of the project using customtkinter was created by Jeremiah Adejo.
"""


import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os, time, pygame, threading, pickle, sys
from tkinter import filedialog


PROGRAM_NAME = ' Explosion Drum Machine '
MAX_NUMBER_OF_PATTERNS = 10
MAX_NUMBER_OF_DRUM_SAMPLES = 5
MAX_NUMBER_OF_UNITS = 10
MAX_BPU = 10
INITIAL_NUMBER_OF_UNITS = 5
INITIAL_BPU = 5
INITIAL_BEATS_PER_MINUTE = 240
MIN_BEATS_PER_MINUTE = 80
MAX_BEATS_PER_MINUTE = 360
COLOR_1 = 'grey50'
COLOR_2 = 'khaki2'
BUTTON_CLICKED_COLOR = '#98FF98'
BTN_COLOR = "#5A7A5A"

def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller. This function is used for processing the paths of external paths before running them."""
	try: 
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, relative_path)

class MySpinbox(tk.Spinbox):
	"""
	A reusable Spinbox subclass that applies consistent default styling across the app.

	This widget prevents repetitive configuration by centralizing common options
	(background color, text color, width, value range, etc.). Each instance can still
	override defaults as needed, but the shared baseline ensures cleaner code and a
	more uniform interface.
	"""
	def __init__(self, parent, root_bg, **kwargs):
		default = {
		"width":5,
		"fg":"white", 
		"buttonbackground":root_bg,
		"bg":root_bg,
		}
		default.update(kwargs)
		super().__init__(parent, **default)

class DrumMachine:
	def __init__(self, root):
		self.root = root
		self.root.title(PROGRAM_NAME)
		#self.root.geometry("700x400")
		self.beats_per_minute = INITIAL_BEATS_PER_MINUTE
		self.all_patterns = [None] * MAX_NUMBER_OF_PATTERNS
		self.current_pattern_index = 0
		self.drum_load_entry_widget = [None] * MAX_NUMBER_OF_DRUM_SAMPLES
		self.loop = True
		self.now_playing = False
		"""self.current_pattern = IntVar()
								self.number_of_units = IntVar()
								self.bpu = IntVar()"""
		self.mainFrame = ctk.CTkFrame(self.root, fg_color="transparent")
		self.mainFrame.pack(expand=True, fill="both")
		self.init_all_patterns()
		self.init_gui()
		self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

	# ====== Getters and Setters ========

	def get_current_pattern_dict(self):
		return self.all_patterns[self.current_pattern_index]

	def get_bpu(self):
		return self.get_current_pattern_dict()["bpu"]

	def set_bpu(self):
		self.get_current_pattern_dict()["bpu"] = int(self.bpu_widget.get())

	def get_number_of_units(self):
		return self.get_current_pattern_dict()["number_of_units"]

	def set_number_of_units(self):
		self.get_current_pattern_dict()["number_of_units"] = int(self.number_of_units_widget.get())

	def get_list_of_drum_files(self):
		return self.get_current_pattern_dict()["list_of_drum_files"]

	def get_drum_file_path(self, drum_index):
		return self.get_list_of_drum_files()[drum_index]

	def set_drum_file_path(self, drum_index, file_path):
	    self.get_list_of_drum_files()[drum_index] = file_path

	def get_is_button_clicked_list(self):
		return self.get_current_pattern_dict()["is_button_clicked_list"]

	def set_is_button_clicked_list(self, num_of_rows, num_of_columns):
		self.get_current_pattern_dict()["is_button_clicked_list"] = [
			[False] * num_of_columns for x in range(num_of_rows)]

	# ===== End of Setters and Getters ==========


	def init_all_patterns(self):
		self.all_patterns = [
		   {"list_of_drum_files": [None]*MAX_NUMBER_OF_DRUM_SAMPLES,
			"number_of_units": INITIAL_NUMBER_OF_UNITS,
			'bpu': INITIAL_BPU,
			'beats_per_minute': INITIAL_BEATS_PER_MINUTE,
			'is_button_clicked_list': self.init_is_button_clicked_list(MAX_NUMBER_OF_DRUM_SAMPLES, INITIAL_NUMBER_OF_UNITS * INITIAL_BPU)
			} for k in range(MAX_NUMBER_OF_PATTERNS)]

	def init_is_button_clicked_list(self, num_of_rows, num_of_columns):
		return [[False] * num_of_columns for x in range(num_of_rows)]

	def on_pattern_changed(self):
		self.change_pattern()

	def change_pattern(self):
		self.current_pattern_index = int(self.pattern_index_widget.get())
		self.display_pattern_name()

		# Update the UI widgets to reflect the current pattern's settings
		current_pattern = self.get_current_pattern_dict()

		self.number_of_units_widget.delete(0, "end")
		self.number_of_units_widget.insert(0, current_pattern["number_of_units"])

		self.bpu_widget.delete(0, "end")
		self.bpu_widget.insert(0, current_pattern["bpu"])

		self.beats_per_minute_widget.delete(0, "end")
		self.beats_per_minute_widget.insert(0, current_pattern["beats_per_minute"])

		self.beats_per_minute = current_pattern["beats_per_minute"]

		self.create_left_drum_loader()
		self.display_all_drum_file_names()
		self.create_right_button_matrix()
		self.display_all_button_colors()

	def restart_play_of_new_pattern(self):
		self.start_play()

	def on_number_of_units_changed(self):
		# Calculate old columns from current stored data
		current_pattern = self.get_current_pattern_dict()
		old_columns = len(current_pattern["is_button_clicked_list"][0])

		# Update the stored value
		self.set_number_of_units()

		# Calculate new columns
		new_columns = self.find_number_of_columns()

		# Always update the list when size changes
		if old_columns != new_columns:
			# Preserve existing data where possible
			old_list = self.get_is_button_clicked_list()
			new_list = [[False] * new_columns for _ in range(MAX_NUMBER_OF_DRUM_SAMPLES)]

			# Copy existing values that fit in the new size
			for row in range(MAX_NUMBER_OF_DRUM_SAMPLES):
				for col in range(min(old_columns, new_columns)):
					new_list[row][col] = old_list[row][col]

			self.get_current_pattern_dict()["is_button_clicked_list"] = new_list

		self.create_right_button_matrix()

	def on_bpu_changed(self):
		# Calculate old columns from current stored data
		current_pattern = self.get_current_pattern_dict()
		old_columns = len(current_pattern["is_button_clicked_list"][0])

		# Update the stored value
		self.set_bpu()

		# Calculate new columns
		new_columns = self.find_number_of_columns()

		# Only reset if the size is actually changed
		if old_columns != new_columns:
			# Preserve existing data that fit in the new size
			old_list = self.get_is_button_clicked_list()
			new_list = [[False] * new_columns for _ in range(MAX_NUMBER_OF_DRUM_SAMPLES)]

			# Copy existing data where possible
			for row in range(MAX_NUMBER_OF_DRUM_SAMPLES):
				for col in range(min(old_columns, new_columns)):
					new_list[row][col] = old_list[row][col]

			self.get_current_pattern_dict()["is_button_clicked_list"] = new_list
		self.create_right_button_matrix()

	# Loading the drum files
	def on_open_file_button_clicked(self, drum_index):
		def event_handler():
			file_path = filedialog.askopenfilename(defaultextension=".wav",
				filetypes=[("Wave Files", "*wav"), ("OGG Files", "*ogg")])
			if not file_path:
				return 
			self.set_drum_file_path(drum_index, file_path)
			self.display_all_drum_file_names()
		return event_handler

	def display_all_drum_file_names(self):
		for i, drum_name in enumerate(self.get_list_of_drum_files()):
			self.display_drum_name(i, drum_name)

	def display_drum_name(self, text_widget_num, file_path):
		if file_path is None:
			return
		drum_name = os.path.basename(file_path)
		self.drum_load_entry_widget[text_widget_num].delete(0, tk.END)
		self.drum_load_entry_widget[text_widget_num].insert(0, drum_name)

	# New thread
	def play_in_thread(self):
		self.thread = threading.Thread(target = self.play_pattern)
		self.thread.start()

	# Playing the drum files
	def init_pygame(self):
		pygame.mixer.pre_init(44100, -16, 1, 512)
		pygame.init()

	def play_sound(self, sound_filename):
		if sound_filename is not None:
			pygame.mixer.Sound(sound_filename).play()

	def play_pattern(self):
		self.now_playing = True
		while self.now_playing:
			play_list = self.get_is_button_clicked_list()
			num_columns = len(play_list[0])
			for column_index in range(num_columns):
				column_to_play = self.get_column_from_matrix(play_list, column_index)
				for i, item in enumerate(column_to_play):
					if item:
						sound_filename = self.get_drum_file_path(i)
						self.play_sound(sound_filename)
				time.sleep(self.time_to_play_each_column())
				if not self.now_playing: break
			if not self.loop: break
		self.now_playing = False
		self.toggle_play_button_state()

	def toggle_play_button_state(self):
		if self.now_playing:
			self.play_button.configure(state="disabled")
		else:
			self.play_button.configure(state="normal")

	def time_to_play_each_column(self):
		beats_per_second = self.beats_per_minute / 60
		time_to_play_each_column = 1 / beats_per_second
		return time_to_play_each_column

	def get_column_from_matrix(self, matrix, i):
		return [row[i] for row in matrix]

	def on_play_button_clicked(self):
		self.start_play()
		self.toggle_play_button_state()

	def start_play(self):
		self.init_pygame()
		self.play_in_thread()  # Direct call to self.play_pattern()

	def on_stop_button_clicked(self):
		self.stop_play()
		self.toggle_play_button_state()

	def stop_play(self):
		self.now_playing = False

	def on_loop_button_toggled(self):
		self.loop = self.loopbuttonvar.get()
		self.keep_playing = self.loop
		if self.now_playing:
			self.now_playing = self.loop
		self.toggle_play_button_state()

	def on_beats_per_minute_changed(self):
		self.beats_per_minute = int(self.beats_per_minute_widget.get())

	def set_button_value(self, row, col, bool_value):
		self.all_patterns[self.current_pattern_index]["is_button_clicked_list"][row][col] = bool_value

	def process_button_clicked(self, row, col):
		self.set_button_value(row, col, not self.get_button_value(row, col))
		self.display_button_color(row, col)

	def on_button_clicked(self, row, col):
		def event_handler():
			self.process_button_clicked(row, col)
		return event_handler

	def get_button_value(self, row, col):
		return self.all_patterns[self.current_pattern_index]["is_button_clicked_list"][row][col]

	def find_number_of_columns(self):
		return int(self.number_of_units_widget.get()) * int(self.bpu_widget.get())

	def display_button_color(self, row, col):
		bpu = int(self.bpu_widget.get())
		original_color = COLOR_1 if ((col//bpu) %2 ) else COLOR_2
		button_color   = BUTTON_CLICKED_COLOR if self.get_button_value(row, col) else original_color
		self.buttons[row][col].configure(fg_color=button_color)

	def display_all_button_colors(self):
		number_of_columns = self.find_number_of_columns()
		for r in range(MAX_NUMBER_OF_DRUM_SAMPLES):
			for c in range(number_of_columns):
				self.display_button_color(r, c)

	# Adding multiple beat patterns
	def display_pattern_name(self):
		self.current_pattern_name_widget.configure(state="normal")
		self.current_pattern_name_widget.delete(0, "end")
		self.current_pattern_name_widget.insert(0, f"Pattern {self.current_pattern_index}")
		self.current_pattern_name_widget.configure(state="readonly")




	def create_top_bar(self):
		topbar_frame = ctk.CTkFrame(self.mainFrame, height = 25, fg_color="transparent")
		topbar_frame.grid(row = 0, columnspan = 12, rowspan=10, padx=5, pady=5)

		# Pattern Number section
		ctk.CTkLabel(topbar_frame, text="Pattern Number:").grid(row=0, column=1, padx=5)
		self.pattern_index_widget = MySpinbox(topbar_frame, root_bg = self.root.cget("bg"),#bg=self.root.cget("bg") makes the spinbox inherit the color of the root
			values=[str(i) for i in range(1, MAX_NUMBER_OF_PATTERNS + 1)],
			command=self.on_pattern_changed)
		self.pattern_index_widget.grid(row=0, column=2)
		self.current_pattern_name_widget = ctk.CTkEntry(topbar_frame, fg_color="transparent")
		self.current_pattern_name_widget.grid(row=0, column=3, padx=7, pady=2)

		# Display the name
		self.current_pattern_index = int(self.pattern_index_widget.get())
		self.display_pattern_name()

		# Number of Units section
		ctk.CTkLabel(topbar_frame, text="Number of Units:").grid(row=0, column=4)
		self.number_of_units_widget = MySpinbox(topbar_frame, root_bg = self.root.cget("bg"),
			values=[str(i) for i in range(MAX_NUMBER_OF_UNITS + 1)],
			command=self.on_number_of_units_changed)
		self.number_of_units_widget.delete(0, "end")
		self.number_of_units_widget.insert(0, INITIAL_NUMBER_OF_UNITS)
		self.number_of_units_widget.grid(row=0, column=5, padx=5)

		# BPU section
		ctk.CTkLabel(topbar_frame, text="BPUs:").grid(row=0, column=6)
		self.bpu_widget = MySpinbox(topbar_frame, root_bg = self.root.cget("bg"),
			values=[str(i) for i in range(MAX_BPU + 1)],
			command=self.on_bpu_changed)
		self.bpu_widget.grid(row=0, column=7)
		self.bpu_widget.delete(0, "end")
		self.bpu_widget.insert(0, INITIAL_BPU)


	def create_play_bar(self):
		playbar_frame = ctk.CTkFrame(self.mainFrame, height=15, fg_color="transparent")
		start_row = MAX_NUMBER_OF_DRUM_SAMPLES + 10
		playbar_frame.grid(row=start_row, columnspan=13, sticky="we",
			padx=15, pady=10)
		self.play_icon = ctk.CTkImage(
			light_image = Image.open(resource_path("images/play_button.png")),
			dark_image  = Image.open(resource_path("images/play button.png")))
		self.stop_icon = ctk.CTkImage(
			light_image=Image.open(resource_path("images/stop_button.png")),
			dark_image =Image.open(resource_path("images/stop button.png")))
		self.loop_icon = ctk.CTkImage(
			light_image=Image.open(resource_path("images/loop_button.png")),
			dark_image =Image.open(resource_path("images/loop button.png")))
		self.photo = tk.PhotoImage(file=resource_path("images/signature.gif"))


		# Play Button
		self.play_button = ctk.CTkButton(playbar_frame, text="", fg_color=BTN_COLOR,
			image=self.play_icon, compound="left", width=10,
			command=self.on_play_button_clicked)
		self.play_button.grid(row=start_row, column=1, padx=2)

		# Stop Button
		self.stop_button = ctk.CTkButton(playbar_frame, text="", width=10, fg_color=BTN_COLOR,
			command=self.on_stop_button_clicked, image=self.stop_icon, compound="left")
		self.stop_button.grid(row=start_row, column=3, padx=2)

		# Loop button
		self.loopbuttonvar = tk.BooleanVar()
		self.loopbuttonvar.set(True)
		self.loopbutton = ctk.CTkCheckBox(playbar_frame, text="Loop", variable=self.loopbuttonvar,
			command=self.on_loop_button_toggled, textvariable=True, 
			checkbox_width=12, checkbox_height=12, bg_color="transparent")
		self.loopbutton.grid(row=start_row, column=16, padx=5)

		# Beats per minutes checkbox
		ctk.CTkLabel(playbar_frame, text="Beats Per Minute:").grid(row=start_row, column=25)
		self.beats_per_minute_widget = MySpinbox(playbar_frame, root_bg = self.root.cget("bg"),
			values=[str(i) for i in range(MIN_BEATS_PER_MINUTE, MAX_BEATS_PER_MINUTE+1, 5)],
			command=self.on_beats_per_minute_changed)
		self.beats_per_minute_widget.grid(row=start_row, column=30)
		self.beats_per_minute_widget.delete(0,"end")
		self.beats_per_minute_widget.insert(0, INITIAL_BEATS_PER_MINUTE)

		label = ctk.CTkLabel(playbar_frame, text="", image=self.photo)
		label.image = self.photo 
		label.grid(row=start_row, column=50, padx=1, sticky="w")

		# Reset button


	def create_left_drum_loader(self):
		left_frame = ctk.CTkFrame(self.mainFrame, fg_color="transparent")
		left_frame.grid(row=10, column=0, columnspan=6, sticky="news")
		open_file_icon = ctk.CTkImage(
			light_image=Image.open(resource_path("images/openfile2.png")),
			dark_image =Image.open(resource_path("images/openfile2.png")))
		for i in range(MAX_NUMBER_OF_DRUM_SAMPLES):
			open_file_button = ctk.CTkButton(left_frame, image=open_file_icon,
				command=self.on_open_file_button_clicked(i), width=3, height=3, text="", fg_color="transparent")
			open_file_button.image = open_file_icon
			open_file_button.grid(row=i, column=0, padx=5, pady=4)
			self.drum_load_entry_widget[i] = ctk.CTkEntry(left_frame)
			self.drum_load_entry_widget[i].grid(
				row=i, column=4, padx=7, pady=4)


	def create_right_button_matrix(self):
		right_frame = ctk.CTkFrame(self.mainFrame, fg_color="transparent")
		right_frame.grid(row=10, column=6, sticky="news", padx=15, pady=4)
		self.buttons = [[None for x in range(
			self.find_number_of_columns())] for x in range(MAX_NUMBER_OF_DRUM_SAMPLES)]
		for row in range(MAX_NUMBER_OF_DRUM_SAMPLES):
			for col in range(self.find_number_of_columns()):
				self.buttons[row][col] = ctk.CTkButton(
					right_frame, command=self.on_button_clicked(row, col),
					text="", height=35, width=20)
				self.buttons[row][col].grid(row=row, column=col, padx=1)
				self.display_button_color(row, col)

	def create_top_menu(self):
		self.menu_bar = tk.Menu(self.root)

		# File Menu
		self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
		self.file_menu.add_command(label="Load Project", command=self.load_project)
		self.file_menu.add_command(label="Save Project", command=self.save_project)
		self.file_menu.add_separator()
		self.file_menu.add_command(label="Exit", command=self.exit_app)
		self.menu_bar.add_cascade(label="File", menu=self.file_menu) # Add the file menu to the menu bar

		# About Menu
		self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
		self.about_menu.add_command(label="About", command=self.show_about)
		self.menu_bar.add_cascade(label="About", menu=self.about_menu)
		self.root.configure(menu=self.menu_bar)

	def load_project(self):
		file_path = filedialog.askopenfilename(filetypes=[("Explosion Beat File", "*.ebt")], title="Load Project")
		if not file_path: return
		
		pickled_file_object = open(file_path, "rb")

		try:
			self.all_patterns = pickle.load(pickled_file_object)
		except EOFError:
			tk.messagebox.show_error("Error", "Explosion Beat file seems corrupted or invalid ❗")
			pickled_file_object.close()

		try:
			self.change_pattern()
			self.root.title(os.path.basename(file_path) + PROGRAM_NAME)
		except:
			tk.messagebox.show_error("Error", "An unexpected error occured while trying to process the beat file")


	def save_project(self):
		saveas_file_name = filedialog.asksaveasfilename(filetypes=[("Explosion Beat File", "*.ebt")], title="Save Project as...")
		if saveas_file_name is None: return
		pickle.dump(self.all_patterns, open(saveas_file_name, "wb"))

		self.root.title(os.path.basename(saveas_file_name) + PROGRAM_NAME)

	def show_about(self):
		about = """
Programmable Drum Machine by Bhaskar Chaudhary.
Reprogrammed with Customtkinter by Jeremiah Adejo.
		"""
		tk.messagebox.showinfo(PROGRAM_NAME, about)


	def init_gui(self):
		self.create_top_menu()
		self.create_top_bar()
		self.create_left_drum_loader()
		self.create_right_button_matrix()
		self.create_play_bar()

	def exit_app(self):
		self.now_playing = False
		if tk.messagebox.askokcancel("Quit", "Really quit"):
			self.root.destroy()

if __name__ == "__main__":
	root = ctk.CTk()
	DrumMachine(root)
	root.mainloop()