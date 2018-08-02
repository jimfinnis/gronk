@title Markdown as used in Gronk

# Markdown
A quick guide to the markdown we support here.

## Headings and emphasis
* Headings are done by multiple # at the start of a line.
* Emphasis is done using `*this*` for *italics* and `**this**` for **bold**, or _this_
* Horizontal lines are done with `---` on a line

---

## Code
* Inline code is done with backticks.
* Code blocks are done with 8 space indents (not 4, weirdly)


        here's a code block.

## Links
WikiLinks are supported, so `[[index]]` will work (a so-called "WikiLink"): [[index]].
WikiLinks won't work with full URLS, just page names.

Alternatively, you can use  `[text](pagename or URL)`, so `[return to index](/index)` should work: [return to index](/index).
Note the slash at the start of the URL, that's important.


## Lists
Bulleted lists start with a `*`, with a number of spaces before it for
indenting. Numbered lists (annoyingly) start with their numbers. So

    * this is a 
    * list with
        * a sublist in it
        
will render as

* this is a 
* list with
    * a sublist in it

and

    1. hello
    2. there
        3. foo
        4. bar
        
will render as

1. Hello
2. Here
    3. Foo
    4. Bar



## Special stuff
Any lines in the files which start with `@` are special commands to 
Gronk. These are currently:

* `@nav x y z` adds the pages x, y and z to the nav bar. Don't put `index`
in here; that page is always present.
* `@title ...` sets the page title

