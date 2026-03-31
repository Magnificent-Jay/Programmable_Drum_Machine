import customtkinter as tk

PROGRAM_NAME = " Explosion Drum Machine "
MAX_NUMBER_OF_PATTERNS = 10
MAX_NUMBER_OF_DRUM_SAMPLES = 5
INITIAL_NUMBER_OF_UNITS = 4
INITIAL_BPU = 4
INITIAL_BEATS_PER_MINUTE = 240

class DrumMachine:
	def __init__(self, root):
		self.root = root
		root.title(PROGRAM_NAME)
		root.geometry("500x400")
		"""self.current_pattern = IntVar()
								self.number_of_units = IntVar()
								self.bpu = IntVar()
								self.to_loop = BooleanVar()
								self.beats_per_minute = IntVar()"""
		self.init_gui()


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

	def create_top_bar(self):
		pass

	def create_play_bar(self):
		pass

	def create_left_drum_loader(self):
		pass

	def create_right_button_matrix(self):
		pass

	def init_gui(self):
		self.create_top_bar()
		self.create_left_drum_loader()
		self.create_right_button_matrix()
		self.create_play_bar()









if __name__ == "__main__":
	root = tk.CTk()
	DrumMachine(root)
	root.mainloop()