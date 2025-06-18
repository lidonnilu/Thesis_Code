import argparse
from datetime import datetime
import h5py
from nexusformat.nexus import *
import os
from pathlib import Path
import re
from spe2py import SpeTool
import spe_loader as sl
import subprocess
import tkinter as tk
from tkinter import filedialog
import traceback


#region Convert SPE to NeXuS
def convert_file(filename):
	global output_file
	try:
		spe_file = sl.load_from_files([filename])

		title = Path(filename).stem
		print(f"Title: {title}")
		output_dir = Path(filename).parent
		now_datetime = datetime.now()
		if args.output_filename.strip() == "":
			output_file = output_dir/Path(f"{title}.nxs")
		else:
			desired_filename = now_datetime.strftime(args.output_filename)
			desired_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', desired_filename)
			output_file = output_dir/Path(f"{desired_filename}.nxs")

		# Extract the intensity and wavelength
		intensity = spe_file.data
		wavelength = spe_file.wavelength

		# parsing the metadata
		sensor_types_str = spe_file.footer.SpeFormat.DataHistories.DataHistory.Origin.Experiment.Devices.Cameras.Camera.Sensor.Information.Type.cdata.upper()
		
		print(f"Output: {output_file}")
		print("")

		if args.print_xmltree:
			print("SPE file tree structure")
			print("-----------------------")
			spe_tool = SpeTool(spe_file)
			spe_tool.xmltree(spe_file.footer)
			print("")

		# build the nexus file
		f = h5py.File(output_file, "w")
		f.attrs['default'] = 'entry'

		# /entry
		f.create_group("entry")
		f['/entry'].attrs["NX_class"]= "NXentry"
		f['/entry'].attrs["default"] = "data"

		# /entry/definition
		f['/entry'].create_dataset('definition',data='NXraman')
		f['/entry/definition'].attrs["version"] = 'v2024.02'
		f['/entry/definition'].attrs["URL"] = 'https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fd58c03d6c1be6469c2aff92ae7649fe5ad38a63/contributed_definitions/NXoptical_spectroscopy.nxdl.xml'

		# /entry/end_time
		f['/entry'].create_dataset('end_time',data=now_datetime.astimezone().isoformat())

		# /entry/experiment_description
		f['/entry'].create_dataset('experiment_description',data='Raman Spectroscopy')
		f['/entry/experiment_description'].attrs["description"] = 'Technique'

		# /entry/experiment_type and sub_type
		f['/entry'].create_dataset('experiment_type', data='Raman Spectroscopy')
		f['/entry'].create_dataset('raman_experiment_type', data='other')
		f['/entry/raman_experiment_type'].attrs["custom"] = True

		# /entry/title
		f['/entry'].create_dataset('title',data=title)

		# /entry/user
		f['/entry'].create_group("user")
		f['/entry/user'].attrs["NX_class"] = "NXuser"
		f['/entry/user'].create_dataset('name', data = args.user_name)
		f['/entry/user'].create_dataset('email', data = args.user_email)
		f['/entry/user'].create_dataset('affiliation', data = 'UNIMI') 

		# /entry/instrument
		f['/entry'].create_group("instrument")
		f['/entry/instrument'].attrs['NX_class'] = "NXinstrument"
		f['/entry/instrument'].create_dataset('scattering_configuration', data ='')
		f['/entry/instrument'].create_group('beam_laser')
		f['/entry/instrument/beam_laser'].attrs['NX_class'] = "NXbeam"
		f['/entry/instrument/beam_laser'].create_dataset('wavelength', data = args.beam_laser_wavelength)
		f['/entry/instrument/beam_laser'].create_dataset('parameter_reliability', data = 'nominal')
		#f['/entry/instrument'].create_dataset('beam_incident', data = '')
		#f['/entry/instrument/beam_laser'].create_dataset('wavelength', data = '')
		f['/entry/instrument/beam_laser/wavelength'].attrs["units"] = 'nm'

		# /entry/instrument/source
		f['/entry/instrument'].create_group("source")
		f['/entry/instrument/source'].attrs["NX_class"] = "NXsource"
		f['/entry/instrument/source'].create_dataset('type',data='Optical Laser')
		f['/entry/instrument/source'].create_dataset('wavelength', data = args.source_wavelength)
		f['/entry/instrument/source/wavelength'].attrs["units"] = "nm"

		# /entry/instrument/monochromator
		f['/entry/instrument'].create_group("monochromator")
		f['/entry/instrument/monochromator'].attrs["NX_class"] = "NXmonochromator"

		# /entry/instrument/detector
		f['/entry/instrument'].create_group("detector")
		f['/entry/instrument/detector'].attrs["NX_class"] = "NXdetector"
		f['/entry/instrument/detector'].create_dataset('detector_type', data = sensor_types_str)

		# /entry/sample
		f['/entry'].create_group("sample")
		f['/entry/sample'].attrs["NX_class"] = "NXsample"
		f['/entry/sample'].create_dataset('name', data = args.material)

		# /entry/data
		f['/entry'].create_group("data")
		f['/entry/data'].attrs['NX_class']= "NXdata"
		#f['/entry/data'].attrs['axes'] = "wavelength"
		f['/entry/data'].attrs["signal"] = "intensity"
		f['/entry/data'].create_dataset("intensity", data = intensity)
		f['/entry/data/intensity'].attrs["units"] = "counts"
		f['/entry/data'].create_dataset("wavelength", data = wavelength)
		f['/entry/data/wavelength'].attrs["units"] = "nm"

		f.close()

		if args.print_metadata:
			test=nxload(output_file)
			print("METADATA")
			print("--------")
			print(test.tree)
			print("")

		if args.print_validate:
			os.system(f"C:\DATA\DATA\\nxinspect.exe -f {output_file}")

		if "status_label" in vars():
			status_label.config(text=f"SPE file: {filename}\nExported to {output_file}")
			reveal_button.config(state=tk.NORMAL)
		return str(output_file)
	except Exception:
		if "status_label" in vars():
			status_label.config(text=f"An error occurred, check the console :(")
		traceback.print_exc()
		return False
#endregion


#region Browse the selected file
def browse_file():
	global args
	try:
		reveal_button.config(state=tk.DISABLED)
		filename = filedialog.askopenfilename(filetypes=[("SPE files",('*.spe'))])
		print(f"Filename: {filename}")
		if filename == "":
			status_label.config(text=initial_status)
			return False
		
		# Copy UI values to args, which will be used in convert_file()
		args.beam_laser_wavelength = beam_laser_wavelength.get()
		args.source_wavelength = source_wavelength.get()
		args.material = material.get()
		args.user_name = user_name.get()
		args.user_email = user_email.get()

		args.print_xmltree = print_xmltree.get()
		args.print_metadata = print_metadata.get()
		args.print_validate = print_validate.get()

		args.output_filename = output_filename.get()
		convert_file(filename)
	except Exception:
		status_label.config(text=f"An error occurred, check the console :(")
		traceback.print_exc()
		return False
#endregion


#region Parse command line arguments
parser = argparse.ArgumentParser(prog='Convert SPE to NeXus',
			description='This script converts a SPE file to a NeXus file. Fill the entries and use the button below to select the SPE file and start the conversion.')

# The default values set here will also be used in the UI.
parser.add_argument('-f', '--file', action="store", help="The SPE file to convert.", default="")
parser.add_argument('-blw', '--beam-laser-wavelength', action="store", default=532)
parser.add_argument('-sw', '--source-wavelength', action="store", default=532)
parser.add_argument('-m', '--material', action="store", default="")
parser.add_argument('-un', '--user-name', action="store", default="")
parser.add_argument('-ue', '--user-email', action="store", default="")

parser.add_argument('-px', '--print-xmltree', action="store", default=False)
parser.add_argument('-pm', '--print-metadata', action="store", default=True)
parser.add_argument('-pv', '--print-validate', action="store", default=True)

parser.add_argument('-o', '--output-filename', action="store", help="The output file name without extension.", default="RAMAN_%Y%m%d_%H%M%S")

args = parser.parse_args()
print(f"Command line arguments: {args}")
if args.file != "":
	convert_file(args.file)
#endregion


#region Other methods
def reveal_file():
	subprocess.Popen(fr'explorer /select,"{str(output_file)}"')


def validate_int(P):
	if P.isdigit() or P == "":
		return True
	return False
#endregion


#region Create the main window
if args.file == "":
	root = tk.Tk()
	root.title("Convert SPE to NeXus")
	root.resizable(width=False, height=False)

	output_file = ""
	initial_status = "No file selected.\nBrowse to the SPE file to convert it."
	entry_width = 30
	validate_int_cmd = root.register(validate_int)

	# INFO
	info_frame = tk.LabelFrame(root, text="Info")
	info_frame.pack(padx=10, pady=10, fill=tk.X)

	info_label = tk.Label(info_frame, text="This script converts a SPE file to a NeXus file.\nFill the entries and use the button below to select the SPE file and start the conversion.")
	info_label.pack(padx=10, pady=10)


	# SETTINGS
	settings_frame = tk.LabelFrame(root, text="Settings")
	settings_frame.pack(padx=10, pady=10, fill=tk.X)
	settings_frame.grid_columnconfigure(0, weight=1)
	settings_frame.grid_columnconfigure(1, weight=1)

	# Beam laser wavelength
	beam_laser_wavelength_label = tk.Label(settings_frame, text="Beam laser wavelength: ")
	beam_laser_wavelength_label.grid(row=0, column=0, sticky='e')

	beam_laser_wavelength = tk.IntVar(value=args.beam_laser_wavelength)
	beam_laser_wavelength_entry = tk.Entry(settings_frame, width=entry_width, validate="key", validatecommand=(validate_int_cmd, "%P"), textvariable=beam_laser_wavelength)
	beam_laser_wavelength_entry.grid(row=0, column=1, pady=10, sticky='w')

	# Source wavelength
	source_wavelength_label = tk.Label(settings_frame, text="Source wavelength: ")
	source_wavelength_label.grid(row=1, column=0, pady=(0, 10), sticky='e')

	source_wavelength = tk.IntVar(value=args.source_wavelength)
	source_wavelength_entry = tk.Entry(settings_frame, width=entry_width, validate="key", validatecommand=(validate_int_cmd, "%P"), textvariable=source_wavelength)
	source_wavelength_entry.grid(row=1, column=1, pady=(0, 10), sticky='w')

	# Material
	material_label = tk.Label(settings_frame, text="Material: ")
	material_label.grid(row=2, column=0, sticky='e')

	material = tk.StringVar()
	material_entry = tk.Entry(settings_frame, width=entry_width, textvariable=material)
	material_entry.grid(row=2, column=1, pady=10, sticky='w')

	# User name
	user_name_label = tk.Label(settings_frame, text="User name: ")
	user_name_label.grid(row=3, column=0, sticky='e')

	user_name = tk.StringVar()
	user_name_entry = tk.Entry(settings_frame, width=entry_width, textvariable=user_name)
	user_name_entry.grid(row=3, column=1, pady=10, sticky='w')

	# User email
	user_email_label = tk.Label(settings_frame, text="User email: ")
	user_email_label.grid(row=4, column=0, pady=(0, 10), sticky='e')

	user_email = tk.StringVar()
	user_email_entry = tk.Entry(settings_frame, width=entry_width, textvariable=user_email)
	user_email_entry.grid(row=4, column=1, pady=(0, 10), sticky='w')

	# Output file
	output_filename_label = tk.Label(settings_frame, text="Output filename: ")
	output_filename_label.grid(row=5, column=0, sticky='e')

	output_filename = tk.StringVar(value=args.output_filename)
	output_filename_entry = tk.Entry(settings_frame, width=entry_width, textvariable=output_filename)
	output_filename_entry.grid(row=5, column=1, pady=(10, 0), sticky='w')

	output_filename_info = tk.Label(settings_frame, text="Leave the filename field empty to use the same filename.")
	output_filename_info.grid(row=6, column=0, columnspan=2, pady=(0, 10))


	# DEBUG
	debug_frame = tk.LabelFrame(root, text="Debug")
	debug_frame.pack(padx=10, pady=10, fill=tk.X)

	# Print xmltree
	print_xmltree = tk.BooleanVar(value=args.print_xmltree)
	print_xmltree_checkbox = tk.Checkbutton(debug_frame, text='Print the SPE file tree structure in the console', variable=print_xmltree)
	print_xmltree_checkbox.pack(pady=5)

	# Print metadata
	print_metadata = tk.BooleanVar(value=args.print_metadata)
	print_metadata_checkbox = tk.Checkbutton(debug_frame, text='Print the NeXus file metadata in the console', variable=print_metadata)
	print_metadata_checkbox.pack(pady=5)

	# Validate
	print_validate = tk.BooleanVar(value=args.print_validate)
	print_validate_checkbox = tk.Checkbutton(debug_frame, text='Validate the output file and show the result in the console', variable=print_validate)
	print_validate_checkbox.pack(pady=5)


	# BOTTOM
	bottom_frame = tk.LabelFrame(root, text="Execute")
	bottom_frame.pack(padx=10, pady=10, fill=tk.X)

	# Browse to the file and start the conversion
	browse_button = tk.Button(bottom_frame, text="Browse to the SPE file and convert it", command=browse_file)
	browse_button.pack(pady=10)

	# Show some feedback
	status_label = tk.Label(bottom_frame, text=initial_status)
	status_label.pack(padx=10, pady=10)

	# After the conversion, enable this button to find the exported file
	reveal_button = tk.Button(bottom_frame, text="Find the NeXus file in File Explorer", command=reveal_file)
	reveal_button.config(state=tk.DISABLED)
	reveal_button.pack(pady=10)


	# Run the application
	root.mainloop()

#endregion