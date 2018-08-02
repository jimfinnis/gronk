This is a simple Tornado webserver which loads pages from the current
directory formatted in Markdown. I use it myself for ad-hoc wiki-like
things, but it serves as a pretty minimal example of a Tornado application.

The URL is stripped down to the final elements, `.md` is appended, and
it tries to load a Markdown file of that name from the current directory.
If that fails, you get a 404. Otherwise it will load the data, convert
from markdown to HTML, and feed it to the `main.html` template.
