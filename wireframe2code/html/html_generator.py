import webbrowser

from wireframe2code.html.output_generator import output


def __get_code(body: str) -> str:
    return """<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="bootstrap.min.css">
    <link rel="stylesheet" href="gradient.css">

    <title>Generated HTML Page</title>
  </head>
  <body>
    <div class="gradient-bg"></div>
    <main role="main" class="container mt-5 text-center">
      {}
    </main>

    <script src="bootstrap.min.js"></script>
  </body>
</html>
    """.format(body)


if __name__ == "__main__":
    code = __get_code("<h1>Hakdog!</h1>")
    file_path = output(code, "../output")
    webbrowser.open("file://{}".format(file_path))
