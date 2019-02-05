import numpy as np
from skimage import io
import os
import scipy
from scipy.ndimage.morphology import generate_binary_structure
from argparse import ArgumentParser 
import matplotlib.pyplot as plt
"""
A simple preprocessing script for neuron images provided by Dr Ed Ruthazer; the script uses the scripy.morphology
package to parse images into binary structures, separating the image into connected component structures. We assume
here that the largest connected structure is the axon of interest, which is usually true except for cases where there 
are large artifacts in the image. The processed images are then coregistered using ImageJ and then thresholded to 
produce maps of locations along the axon that see the most dynamic behavior - i.e. branches extending and retracting.

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
		if not item.endswith('.tif'):
			input_list.remove(item)
	if not input_list:
		print("Error! No files in input directory ", args.input)
	sample_image = io.imread(input_list[1])
	image_array = np.zeros((len(input_list), sample_image.shape[0], sample_image.shape[1], sample_image.shape[2]))
	# Now create an image array that is [number of images x height x length x width]
	for idx, file_name in enumerate(input_list):
		single_image = io.imread(file_name)
		min_nonzero = (np.min(single_image[single_image > 0]))
		max_nonzero = (np.max(single_image))
		threshold = min_nonzero + (max_nonzero * 1/80)
		single_image[single_image < threshold] = 0
		image_array[idx] = single_image

	# Ensure data is in uint16 format
	image_array = image_array.view(np.uint16)

	# Now we'll be writing to output directory
	os.chdir(args.output)

	# Defines a binary structure describing connectivity of structures in image
	s = generate_binary_structure(3,3)
	print('Cleaning images (might take a few minutes)...')
	for input_idx in range(len(input_list)):
		image = image_array[input_idx]
		label, nb_features = scipy.ndimage.label(image, structure=s)
		largest_group = 0
		group_label = 0

		# Find the largest structure in the image 
		for i in range(1, nb_features + 1):
			nb_vox = np.sum(image[label == i])
			if nb_vox > largest_group:
				largest_group = nb_vox

		# Now, we assume that the largest coherent group is the axon
		# we're looking at, not the noise
		nvox = largest_group
		for i in range(1, nb_features + 1):
			nb_vox = np.sum(image[label == i])
			if nb_vox < nvox:
				image[label == i] = 0

		io.imsave('cleaned_image' + '_' + str(input_idx) + '.tiff', image)
		print("Done image {} of {}".format(input_index + 1, len(input_list)))

	print('Done writing {} images to {}'.format(len(input_list), args.output))

def _parser():
	usage = 'python preprocess.py -i /path/to/folder/with/tiffimages -o /path/to/folder/for/outputs'
	parser = ArgumentParser(usage=usage)
	parser.add_argument('-i', '--input', help='Path to input images to be cleaned', required=True)
	parser.add_argument('-o', '--output', help='Path to where you want cleaned images to go', required=True)
	return parser

if __name__ == '__main__':
	main(_parser().parse_args())