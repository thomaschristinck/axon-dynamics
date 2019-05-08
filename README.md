# Axon Dynamics

### Setting up Python and a Python Environment

1. You need to have python3 on your computer. You can check by entering ```python3``` in the terminal - you should see the python version you're using displayed and a >>> command prompt. If you see something like "COMMAND NOT FOUND", you'll have to install python3. I'm pretty sure Macs come with python 2.7, so you might have to install python3 - I think the Hitchikers Guide to 
Python (Installation Guide) for [mac](https://docs.python-guide.org/starting/install3/osx/) or [linux](https://docs.python-guide.org/starting/install3/linux/) are good. 

2. Python uses a lot of different packages, so it's important to have a package manager, like "pip". If you followed the python3 installation above, you already have pip. If you don't have pip installed, you'll get a "COMMAND NOT FOUND" error when you type "pip" into the terminal and
press "ENTER". Check [here](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py) for information 
on installing pip.

3. Now, you want to set up a virtual environment to manage you packages. [This](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) tutorial walks through installing venv (which is pretty straightforward if you have pip installed). To create a virtual environment, enter ```virtualenv --python=python3 venv_name``` in the terminal. Then, enter ```source venv_name/bin/activate``` to activate your virtual environment. Here "venv_name" is whatever you choose to name your virtual environment (like "py35" or "pyaxon-dynamics"). 

4. You can install the required packages by navigating to this folder 
(enter ```cd /pathway/to/axon-dynamics-code``` in the terminal), and entering ```pip3 install -r 
requirements.txt```


### Usage

1. Clone this repository by entering ```git clone https://github.com/thomaschristinck/axon-dynamics.git``` in the terminal (on mac/linux machine) in a directory of your chosing. Or download zip [here](https://github.com/thomaschristinck/axon-dynamics).

2. Set up a directory with the images you want to analyze. Type ```mkdir /directory/inputs``` where "directory" is some directory that you're going to do the processing in, and "inputs" is the folder where you should put your input .tiff images. Similarly, create a folder for preprocessed outputs ```mkdir /directory/outputs```

3. Now that you have everything set up, preprocess the images as ```python3 preprocess.py -i /path/to/folder/with/tiffimages -o /path/to/folder/for/outputs```. See the file "preprocess.py" for more info on this step. Running this file should take no more than a few minutes.

4. Next, co-register all the processed images from 3 (above) with FIJI. To do this, you want to select all the images in your "outputs" folder and drag them to FIJI to open them. In the FIJI menu, navigate to ```Plugins > Macros > Startup Macros...```. Copy and paste the contents of the ```sample_macro.java``` file into this window, and modify the "out_dir" and "nb_images" variables at the top of the .ijm file. Then click "RUN". This will take quite a while for FIJI to do, around 4 minutes per image. You might want to play around with the registration on Line 16 of the FIJI macro (e.g. change the tolerance to make the registration run faster, or the stop level).

5. Now, you should have a bunch of coregistered images called "superimposed_x_y.tiff" in the folder specified by the "out_dir" variable in step 4. We want to analyze the growth/loss between these registered images. This is why the registration step in 4 is important. Analyze the images by entering ```python3 analyze.py -i /path/to/folder/with/superimposed/images/from4 -o /path/to/folder/for/analysis```. See the file "analyze.py" for more info on this step. Running this file should take a minute or two. 

The analysis folder you specify in step 5 should have a "Plots" folder and a "Results" folder. I find whether or not the plots are coherent depends on what the images look like. The results generally make more sense. I like to visualize the results by opening growth and loss images (e.g. "growth1.tiff and loss1.tiff") as well as the corresponding preprocessed image from step 3 (e.g. "cleaned_image_1.tiff"). In the FIJI menu, navigate to ```Image > Color > Merge Channels...``` and select "loss1.tiff" as red, "growth1.tiff" as green, and "cleaned_image_1.tiff" as blue.
