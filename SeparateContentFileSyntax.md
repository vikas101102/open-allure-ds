# Separate Content File Syntax #

This page describes a basic structure for a multiple choice question/answer/response/action sequence.

# Details #

Each question in a sequence has the structure

```
Question

Answer <separator> Response 
Answer <separator> Response 
...
up to 6 answers
```

# Separator Syntax #

The separator controls what action to take when that answer is selected.

**;** indicates NO action. Stay on the current question and allow another choice.

**;;** indicates to advance to the NEXT question in the sequence.

**;;;** indicates to advance TWO questions in the sequence (skip the next question).

Each additional semicolon after the first advances another question in the sequence.

To avoid long strings of semicolons AND reversals, a syntax using digits is also supported.

**;1** indicates to advance to the NEXT question in the sequence.

**;2** indicates to advance TWO questions in the sequence (skip the next question).

**;+3** indicates to advance THREE questions.  Note the + sign is optional.

**;-1** indicates to return to the PRIOR question.

Open Allure keeps track of the order in which questions are exposed, but a -1 reversal is NOT relative to that order.  The "back"/"prior" voice commands and the left-arrow on the keyboard do use the question stack to backtrack, however.

**;`[`tag`]`** indicates to JUMP to a question which has been marked with a tag (a string in square brackets, such as `[Section Two]`).  See example script below.

# Link Syntax #

Answer-side URLs can be used to open a web browser to a specific page.

Response-side URLs can be used to link to another question sequence.

An Answer-side URL, entered in the script as

```
Question

[link Answer] <separator> Response 
Answer <separator> Response 
...
up to 6 answers
```

will display on the screen as

```
Question
[Answer]
Answer
...
```

so the brackets around [Answer](Answer.md) warn of the web-browser-opening behavior.

When [Answer](Answer.md) is selected, a web browser is launched and the link is opened.

A Response-side URL permits linking a question sequence to another question sequence in a different file or web page.

Entered in the script as

```
Question

Answer 1 ;[link] Response 
Answer 2 <separator> Response 
...
up to 6 answers
```

will display on the screen as

```
Question
Answer 1
Answer 2
...
```

When Answer 1 is selected, the new question sequence at link will be loaded and the first question of that sequence will be displayed.

# Examples of Content Files #

In this first example, the parts of the structure are labeled and "talk about" themselves.

```
This is the first question
in the sequence.
What choice do you want?

First Answer ; Do nothing. Stay on first question.
Second Answer with semicolon ;; Advance to second question using semicolon.
Third Answer with digit ;1 Advance to second question using digit.

This is the second question
in the sequence.
What choice do you want now?

First Answer with reverse ;-1 Return to first question.
Second Answer with no response. ;
Third Answer with advance to nothing. (This should quit.) ;;
```

In this second example, we use jumps in the sequence to make it flow along different paths.  You can see how this sequence plays in the video on [YouTube](http://www.youtube.com/watch?v=Zac1fyq5bjM).

```
Add words to make a well known saying:

Mary ;1 You will make Mary had a little lamb. Or something.
These ;3 You will make These are the times that try men's souls.
Once ;5 You will make Once Upon a Time.

Add more words:

had a little ;;
was a little ; Come on. Mary had a little lamb. Try again.
saw a little ; Come on. Mary had a little lamb. Try again.

Add more words:

lamb ;5 That's it.
cow ; Whose milk was white as snow? Try again.
problem ; Yes, there is something about Mary. Try again.


Add more words:

are the times ;;
are the things ; Come on. These are the times. Try again.
are the souls ; Come on. These are the times. Try again.

Add more words:

that try men's souls ;3 That's it.
that fry men's souls ; OK hot stuff, try again.
that dry men's souls ; I could use a drink about now myself. Try again.


Add more words:

upon ;;
under ; Once Upon a Time. Try again.
beside ; Once Upon a Time. Try again.

Add more words:

a time ;; That's it.
a midnight clear ; Once Upon a Time. Try again.
a midnight dreary ; Once Upon a Time. Try again.


So you see, the streams can reunite.

Quit now ;;
```

An example of an answer-side URL would be:

```
Question
[http://openallureds.org View Open Allure Code Respository] ; Response
```

Finally, to demonstrate response-side URLs, we have a pair of scripts on separate web pages which link to one another.

Script A is located at

http://openallureds.ning.com/profiles/blogs/test-script-a

Script B is located at

http://openallureds.ning.com/profiles/blogs/test-script-b

The Response-side links between them should be apparent:

Script A
```
This is a test question on page A
Answer 1 ; Response 1
Answer 2 ; Response 2
Answer 3 ;; Response 3

A second question
Answer 1 ; Response 1
Answer 2 ; Response 2
Answer 3 ; Response 3
Go to next page ;[test-script-b] Switching to B
```

Script B
```
This is a test question on page B
Answer 1 ; Response 1
Answer 2 ; Response 2
Answer 3 ; Response 3
Go to next page ;[test-script-a] Switching to A
```

Note how it is possible to include a relative path in the link.  An absolute path would also work:

Script B'
```
This is a test question on page B
Answer 1 ; Response 1
Answer 2 ; Response 2
Answer 3 ; Response 3
Go to next page ;[http://openallureds.ning.com/profiles/blogs/test-script-a] Switching to A
```

A link to a local .txt file would also work:

Script B''
```
This is a test question on page B
Answer 1 ; Response 1
Answer 2 ; Response 2
Answer 3 ; Response 3
Go to next page ;[local.txt] Switching to local file local.txt
```

## Tags ##

Here is a script which uses tags.  Tags make it much easier to insert a new question in the middle of a script as renumbering the relative positions of the questions is handled automatically:

```
[TagA]
First question

Answer 1 ;[TagD] Response 1
Answer 2 ;[TagC] Response 2
Answer 3 ; Response 3
Answer 4 ;[TagB] Response 4

[TagB]
Second question

Answer 1 ;[TagA] Response 1

[TagC]
Third question

Answer 1 ;[TagB] Response 1

[TagD]
Fourth question

Answer 1 ;[TagC] Response 1
```

# Other Mark Up Systems #

Compare to [GIFT](http://microformats.org/wiki/gift)