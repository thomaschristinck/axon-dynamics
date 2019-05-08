import numpy as np
from skimage import io
import os
import scipy
from scipy.ndimage.morphology import generate_binary_structure
from argparse import ArgumentParser 
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import cv2
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

"""
A simple preprocessing script for neuron images provided by Ed Ruthazer; the script uses the scripy.morphology
package to parse images into binary structures, separating the image into connected component structures. We assume
here that the largest connected structure is the axon of interest, which should be true except for cases where there 
are large artifacts in the image. The processed images are then coregistered using ImageJ (registration_macro.java) 
and then thresholded to produce maps of locations along the axon that see the most dynamic behavior - i.e. branches 
extending and retracting (analyze.py).

See usage below

Author: Thomas Christinck
Feb 2019
"""

def main(args):
	# Get a list of the input files
	os.chdir(args.input)
	input_list = sorted(os.listdir(os.getcwd()))

	# Remove anything non .tif from folder
	for item in input_list:
		if not item.endswith('.tif') and not item.endswith('.tiff'):
			input_list.remove(item)
	if not input_list:
		print("Error! No files in input directory ", args.input)

	# Get sample image to extract image dimensions. Have to ensure that all images
	min_depth = 500
	for item in input_list:
		sample_image = io.imread(item)
		depth = sample_image.shape[0]
		if depth < min_depth:
			min_depth = depth
	print('Smallest image depth is ', min_depth)
	image_array = np.zeros((len(input_list), min_depth, sample_image.shape[1], sample_image.shape[2]))
	print('Image size:', image_array.shape)

	# Now create an image array that is [number of images x height x length x width]
	for idx, file_name in enumerate(input_list):
		single_image = io.imread(file_name)
		min_nonzero = (np.min(single_image[single_image > 0]))
		max_nonzero = (np.max(single_image))
		threshold = min_nonzero + (max_nonzero * 1/80) #Get rid of some background
		single_image[single_image < threshold] = 0
		image_array[idx, :,:,:] = single_image[:min_depth, :, :]

	# Ensure data is in uint16 format
	image_array = image_array.astype(np.uint16)

	# Now we'll be writing to output directory. Make directory if it doesn't exist
	if not os.path.isdir(args.output):
		os.mkdir(args.output)
	os.chdir(args.output)

	# Defines a binary structure describing connectivity of structures in image
	s = generate_binary_structure(3,3)
	print('Cleaning images (might take a few minutes)...')
	start = timer()
	for input_idx in range(len(input_list)):
		image = image_array[input_idx]
		#Group image into connected regions - we're interested in the biggest region
		label, nb_features = scipy.ndimage.label(image, structure=s)
		largest_group = 0
		#Get the counts for each label, then, find label with largest count
		unique, counts = np.unique(label, return_counts=True)
		largest_index = unique[np.argmax(counts[1:]) + 1]
		largest_struct = np.max(counts[1:])
		largest_group = np.sum(image[label == largest_index])
		image[label != largest_index] = 0
		# Now normalize the image:
		image=cv2.normalize(image,None,0,65535,cv2.NORM_MINMAX)
		# Save
		io.imsave('cleaned_image' + '_' + str(input_idx) + '.tiff', image)
	
		if input_idx % 5 == 0 and input_idx != 0:
			print("Done image {} of {}  {:.2f}m".format(input_idx + 1, len(input_list), (timer()-start)/60))

	print('Done writing {} images to {}'.format(len(input_list), args.output))

def _parser():
	usage = 'python preprocess.py -i /path/to/folder/with/tiffimages -o /path/to/folder/for/outputs'
	parser = ArgumentParser(usage=usage)
	parser.add_argument('-i', '--input', help='Path to input images to be cleaned', required=True)
	parser.add_argument('-o', '--output', help='Path to where you want cleaned images to go', required=True)
	return parser

if __name__ == '__main__':
	main(_parser().parse_args())