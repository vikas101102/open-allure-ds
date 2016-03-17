
```
# codeTour.txt
#
# An Open Allure script demonstrating a voice over
# tour of Open Allure code
#
# The version of the code shown in the browser
# was prepared using pygments http://pygments.org/
#
#    pygmentize -O full,title="$1" -o $1.html $1
#
# where $1 is Python code such as openallure.py
#
# (c) 2011 John Graves

Now we will use Open Allure
to discuss Open Allure itself.

We'll just look at the one file 
openallure.py

Let's begin with
[file:///Users/johngraves/Documents/workspace/openallure/src/html/openallure.py.html the top of the code];

openallure.py starts with the standard imports.
Followed by some third party imports.
And then the other Open Allure modules are imported.

...

[file:///Users/johngraves/Documents/workspace/openallure/src/html/openallure.py.html#main next];

We skip down to the main function.
Here the PyGame screen is initialized.
And we get sort out which language to use from the configuration file.

...

The initialization continues until we reach the main event loop.

[file:///Users/johngraves/Documents/workspace/openallure/src/html/openallure.py.html#loop next];

Notice the first test here
if not openallure.ready

This block carries out all the steps to get a question ready for display.

[input];
```