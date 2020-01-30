# Wireframe2Code

Wireframes are simple black and white layouts that outline the specific type, size, and placement of web page elements.
They are devoid of artistic choices like fonts, logos, colours, and the like.
Because they are easily adjustable, they are ideal for planning content placement, 
and for identifying and solving navigation and functionality problems early in the project.

When building applications, there’s a turning point where you have to start building the user interface
from your wireframe. Typically, this process is expensive, time-consuming, tedious, and repetitive.
But what if you could generate source code straight from your hand-drawn design mock-ups?

## Requirements

To run, you must have:

- Python 3 installed on your machine
- PIP 3 installed on your machine
- PIP dependencies installed on your machine using the following command:

```
pip install -r requirements.txt
```

## Usage

Call `driver.py` and at a minimum, supply the following required arguments:

- `-f` or `--filename`, followed by the path to the input image.
- `-c` or `--camera`, if wireframe sketch will be provided via camera input.
  This option requires a camera attached to your machine.
- `-d` or `--destination`, followed by the path to the output directory.
  This is where the generated HTML document will be stored, along with possible CSS and JS assets.

Only one of either `--filename` or `--camera` arguments can be provided. Otherwise, an exception will be thrown.

The following arguments may also be provided in addition to those above:

- `-i` or `--interactive` to toggle interactive mode.

    When `--camera` and `--interactive` are used together,
    wireframe symbols detected by the application from the camera will be highlighted;
    and generated HTML will be previewed live.
  
    When `--filename` and `--interactive` are used together, 
    the application will display the following sequence of windows:
  
    - the transformations applied to the image for better contour detection
    - the detected wireframe symbols in their bounding boxes
    - the generated HTML document in browser

## Usage examples

```
python driver.py -d path/to/output/directory -c -i
```

```
python driver.py -d path/to/output/directory -f path/to/sketch.jpg
```

## Input

Different images will require different processing techniques.
This application works well with wireframe sketches on paper; blank ink over white canvas.
For example:

<img src="https://i.imgur.com/I5jCKay.jpg" width=300 alt="Clean wireframe sketch"/>
