import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from skimage import img_as_uint
import scipy
from scipy.ndimage.morphology import generate_binary_structure
import os
from argparse import ArgumentParser 
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

"""
An analyzer script for axon images provided by Dr Ed Ruthazer; the script assumes images have been preprocessed (see
preprocess.py) and registered correctly using the sample_macro.java script provided (see instructions in the README in
this repository; also see sample_macro.java)).
This script simply subtracts the overlap between two timepoints, applies a threshold, and counts pixels that have seen 
significant change from one time point to another (i.e. regions of growth or loss). The script produces files in the 
output directory specified when the script is run as follows:

output (folder specified by -output; see usage below)
|
|_____ plots (relevant plots will go here)
|
|_____ growth_loss (.tiff images of growth and loss for each time point will be found here. For example, growth0.tif will
		consist of image regions where there is growth from time 0 to time 1; loss0.tif where there is loss from time 0 to
		time 1)

See usage below (at bottom of this script)

Author: Thomas Christinck
2019
"""

def main(args):

	# Variables to tune: thresh_factor discards all all voxels with magnitude less than 
	# thresh_factor x maximum_voxel intensity; cluster_level considers only groups of growth/
	# loss that are > cluster_level voxels
	thresh_factor = 1/20
	cluster_level = 100

	# Get a sorted list of the input files
	file_list = sorted(os.listdir(args.input))
	superimposed_list = [item for item in file_list if item.startswith('superimposed')]

	# Make sure we're looking in the right directory
	if len(superimposed_list) == 0:
		raise LookupError("Couldn't find superimposed images. Make sure you have correctly run the registration_macro.java file and that" \
			+ " you have correctly specified the input directory (flagged by -i)")
	superimposed_list.sort(key=sort_superimposed)

	# Make output folders
	if not os.path.isdir(args.output):
		os.mkdir(args.output)
	if not os.path.isdir(os.path.join(args.output, 'Results')):
		os.mkdir(os.path.join(args.output, 'Results'))
	if not os.path.isdir(os.path.join(args.output, 'Plots')):
		os.mkdir(os.path.join(args.output, 'Plots'))

	# Initialize lists to be plotted
	ratios = []
	normalized_growth = []
	normalized_loss = []
	normalized_activity = []

	# Now iterate through all files
	for idx, item in enumerate(superimposed_list):
		two_chan = io.imread(os.path.join(args.input, item))
		two_chan = img_as_uint(two_chan)
		# Get image shape and return two matrices (mat1 and mat2) that contain 
		# timepoint 1 and timepoint 2 information
		im_shape = two_chan.shape
		color_axis = min(im_shape)
		axis_idx = im_shape.index(color_axis)

		if axis_idx == 0:
			mat1 = two_chan[0,:,:,:]
			mat2 = two_chan[1,:,:,:]
		elif axis_idx == 1:
			mat1 = two_chan[:,0,:,:]
			mat2 = two_chan[:,1,:,:]
		elif axis_idx == 2:
			mat1 = two_chan[:,:,0,:]
			mat2 = two_chan[:,:,1,:]
		else:
			mat1 = two_chan[:,:,:,0]
			mat2 = two_chan[:,:,:,1]
			
		# Make sure registrations are alligned (not cut off)
		nb_slices = min(mat1.shape)
		for i in range(nb_slices):
			if (np.max(mat1[i,:,:]) == 0 and np.max(mat2[i,:,:]) != 0) or (np.max(mat2[i,:,:]) == 0 and np.max(mat1[i,:,:]) != 0):
				mat1[i,:,:] = 0
				mat2[i,:,:] = 0

		# Now we'll try the intersect subtraction method
		temp1 = np.copy(mat1)
		temp2 = np.copy(mat2)
		temp1[np.where(mat1 != 0)] = 1
		temp2[np.where(mat2 != 0)] = 1
		overlap = temp1 * temp2
		intersect = np.copy(overlap)
		overlap[np.where(overlap != 0)] = np.max(mat1)
	
		# Now subtract intersect from mat1 and mat 2
		mat1_unique = np.copy(mat1)
		mat1_unique[np.where(overlap != 0)] = 0
		mat2_unique = np.copy(mat2)
		mat2_unique[np.where(overlap != 0)] = 0

		# Theshold the matrices 
		mat1_max = np.max(mat1_unique)
		mat2_max = np.max(mat2_unique)
		thresh1 = thresh_factor * mat1_max
		thresh2 = thresh_factor * mat2_max
		mat1_unique[mat1_unique < thresh1] = 0
		mat2_unique[mat2_unique < thresh2] = 0

		# Now, normalize the two images (growth and loss) for statistical purposes
		norm_mat1_unique = mat1_unique / np.max(mat1_unique)
		norm_mat2_unique = mat2_unique / np.max(mat2_unique)
		total_add = np.sum(norm_mat2_unique)
		total_loss = np.sum(norm_mat1_unique)

		if idx % 10 == 0 and idx != 0:
			print('Done writing {} images to {}/Results'.format(idx, args.output))

		#Group image into connected regions - we're interested in the biggest regions
		s = generate_binary_structure(3,3)
		label1, nb_features1 = scipy.ndimage.label(mat1_unique , structure=s)
		label2, nb_features2 = scipy.ndimage.label(mat2_unique , structure=s)
		
		#Get the counts for each label, then, find labels with largest count
		unique1, counts1 = np.unique(label1, return_counts=True)
		unique2, counts2 = np.unique(label2, return_counts=True)
		largest_indices1 = unique1[np.argwhere(counts1[1:] > cluster_level).flatten() + 1]
		largest_indices2 = unique2[np.argwhere(counts2[1:] > cluster_level).flatten() + 1]
	
		# Set up multiplier matrices (0 everywhere except for large connected regions)
		multiplier1 = np.zeros(np.shape(mat1_unique))
		multiplier2 = np.zeros(np.shape(mat2_unique))
		
		for item in largest_indices1:
			multiplier1[label1 == item] += 1
		for item in largest_indices2:
			multiplier2[label2 == item] += 1

		# Now multiply the original images by the multiplier matrices (hopefully getting rid
		# of some more noise)
		filtered_mat1_unique = mat1_unique * multiplier1
		filtered_mat2_unique = mat2_unique * multiplier2

		# Now, normalize the two images (growth and loss) for statistical purposes
		normf_mat1_unique = filtered_mat1_unique / np.max(filtered_mat1_unique)
		normf_mat2_unique = filtered_mat2_unique / np.max(filtered_mat2_unique)
		total_add = np.sum(normf_mat2_unique)
		total_loss = np.sum(normf_mat1_unique)
		
		filtered_mat1_unique = filtered_mat1_unique.astype(np.uint16)
		filtered_mat2_unique = filtered_mat2_unique.astype(np.uint16)
			

		loss_string = "%s/Results/loss%d.tiff" % (args.output, idx)
		growth_string = "%s/Results/growth%d.tiff" % (args.output, idx)
		io.imsave(loss_string, filtered_mat1_unique)
		io.imsave(growth_string, filtered_mat2_unique)

		# Update lists
		if idx == 0:
			normalization_factor = total_add + total_loss
			normalization_loss_factor = total_loss
			normalization_growth_factor = total_add
		ratios.append(total_add / total_loss)
		normalized_activity.append((total_add + total_loss) / normalization_factor)
		normalized_growth.append((total_add) / normalization_growth_factor)
		normalized_loss.append((total_loss) / normalization_loss_factor)

	plt.figure()
	plt.plot(ratios, '-o')
	plt.xlabel('Time point')
	plt.ylabel('Growth-Loss Ratio')
	plt.savefig(os.path.join(args.output, 'Plots', 'ratios.jpeg'))

	plt.figure()
	plt.plot(normalized_activity, '-o',label='activity')
	plt.plot(normalized_growth, '-o',label='growth')
	plt.plot(normalized_loss, '-o',label='loss')
	plt.xlabel('Time point')
	plt.ylabel('Normalized Growth')
	plt.legend()
	plt.savefig(os.path.join(args.output, 'Plots', 'growth.jpeg'))



def sort_superimposed(val): 
	"""
	Ensures superimposed.tif images are sorted correctly (passed as an argument to python sort())
	"""
	vals = val.split('_')
	int_val = int(vals[1])
	return int_val

def _parser():
	usage = 'python analyze.py -i complete/path/to/folder/with/tiffimages -o complete/path/to/folder/for/outputs'
	parser = ArgumentParser(usage=usage)
	parser.add_argument('-i', '--input', help='Path to input images produced by fiji macro', required=True)
	parser.add_argument('-o', '--output', help='Path to where you want the output data (plots and growth/loss images) to go', required=True)
	return parser

if __name__ == '__main__':
	main(_parser().parse_args())