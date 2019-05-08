// Fiji Macro for co-registration

// ****************** CHANGE THIS SECTION ****************************
//Specify ouput directory here (e.g. /User/yourname/data/registration)
out_dir = "/some/path"
//Specify number of cleaned images to be registered
nb_images = 12
// *******************************************************************

for (i = 0; i < nb_images; i++) {
	moving = i + 1;
	target = i;
	selectWindow("cleaned_image_" + moving + ".tiff");
	//run("Brightness/Contrast...");
	setMinAndMax(0, 65535);
	run("Rigid Registration", "initialtransform=[] n=1 tolerance=0.1 level=5 stoplevel=1 materialcenterandbbox=[] showtransformed template=cleaned_image_" + target + ".tiff measure=Euclidean");
	//run("Brightness/Contrast...");
	setMinAndMax(0, 65535);
	saveAs("Tiff", out_dir + "/transformed" + moving + ".tif");
	run("Merge Channels...", "c1=cleaned_image_" + target + ".tiff c2=transformed" + moving + ".tif create keep");
	run("RGB Color", "slices");
	saveAs("Tiff", out_dir + "/superimposed_" + target + "_" + moving + ".tif");
	close();
	close("transform*");
	if (i > 0){
		close("cleaned_image_" + i - 1 + ".tiff");
	}
	close("Composite*");
	close("Matrix*");
}