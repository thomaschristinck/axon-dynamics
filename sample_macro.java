for (i = 0; i < 31; i++) {
	moving = i + 1;
	target = i;
	selectWindow("cleaned_image_" + moving + ".tiff");
	//run("Brightness/Contrast...");
	setMinAndMax(0, 65535);
	run("Rigid Registration", "initialtransform=[] n=1 tolerance=0.1 level=5 stoplevel=1 materialcenterandbbox=[] showtransformed template=cleaned_image_" + target + ".tiff measure=Euclidean");
	//run("Brightness/Contrast...");
	setMinAndMax(0, 65535);
	saveAs("Tiff", "/Users/thomaschristinck/Desktop/Registration/Pipeline/Deformations/transformed" + moving + ".tif");
	run("Merge Channels...", "c1=cleaned_image_" + target + ".tiff c2=transformed" + moving + ".tif create keep");
	run("RGB Color", "slices");
	saveAs("Tiff", "/Users/thomaschristinck/Desktop/Registration/Pipeline/Deformations/superimposed_" + target + "_" + moving + ".tif");
	close();
	close("transform*");
	if (i > 0){
		close("cleaned_image_" + i - 1 + ".tiff");
	}
	close("Composite*");
	close("Matrix*");
}