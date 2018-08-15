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
The `{{ .. }}` block is for special commands.

* `{{@nav x y z}}` adds the pages x, y and z to the nav bar. Don't put `index`
in here; that page is always present.
* `{{@title ...}}` sets the page title
* `{{@do ... }}` will run a Python statement 
* `{{..}}` (i.e. no `@` sign) will give the value of a Python expression

The following commands when prefixed by `f` will return their value converted
to a float, otherwise the underlying variable will be converted to an integer.

* `{{@[f]postinc var n}}` will increment variable `var` by `n`, returning the old value
* `{{@[f]preinc var n}}` will increment variable `var` by `n`, returning the new value
* `{{@[f]accum var n}}`  will increment variable `var` by `n`, returning  `n`

Note that all variable manipulation takes place in a namespace private to the 
page's run.
