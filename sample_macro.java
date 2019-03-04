for (i = 10; i < 31; i++) {
	moving = i + 1;
	target = i;
	selectWindow("cleaned_image_" + moving + ".tiff");
	run("Rigid Registration", "initialtransform=[] n=1 tolerance=0.1 level=5 stoplevel=1 materialcenterandbbox=[] showtransformed template=cleaned_image_" + target + ".tiff measure=Euclidean");
	saveAs("Tiff", "/Users/thomaschristinck/Desktop/Registration/Pipeline/Deformations/transformed" + moving + ".tif");
	run("Merge Channels...", "c1=cleaned_image_" + target + ".tiff c2=cleaned_image_" + moving + ".tiff create keep");
	run("RGB Color", "slices");
	saveAs("Tiff", "/Users/thomaschristinck/Desktop/Registration/Pipeline/Deformations/superimposed_" + target + "_" + moving + ".tiff");
	close();
	close("transform*");
	if (i > 10){
		close("cleaned_image_" + i - 1 + ".tiff");
	}
	close("Composite*");
	close("Matrix*");
}