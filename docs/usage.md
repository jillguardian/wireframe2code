# Application usage

Call `driver.py` and at a minimum, supply the following required arguments:

- `-f` or `--filename`, followed by the path to the input image.
- `-c` or `--camera`, if wireframe sketch will be provided via camera input.
  This option requires a camera attached to your machine.

    <img src="https://i.imgur.com/VrElOsP.gif" height=300 alt="Live wireframe detection"/>

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

## Example commands

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

## Output

The generated HTML file will be named `index.html`. It is expected to look like, and have the following content:

<img src="https://i.imgur.com/6LcApfK.png" height=300 alt="Output HTML preview"/>

```
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="bootstrap.min.css">
    <link rel="stylesheet" href="style.css">
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
    <style>
        .wrapper {
            grid-template-columns: repeat(4, auto);
            grid-template-rows: repeat(4, auto);
        }
    </style>
</head>

<body>
    <div class="gradient-bg"></div>
    <main role="main" class="container mt-5 text-center">
        <div class="wrapper">

            <div class="block" style="grid-column: 2 span;grid-row: 2 span;"></div>
            <div class="block" style=""></div>
            <div class="block" style="grid-row: 4 span;"></div>
            <div class="block" style=""></div>
            <div class="block" style=""></div>
            <div class="block" style="grid-column: 2 span;"></div>
            <div class="block" style="grid-column: 3 span;"></div>

        </div>
    </main>
    <script src="bootstrap.min.js"></script>

</body>

</html>
```