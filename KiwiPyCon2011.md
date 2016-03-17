
```
[path=http://dl.dropbox.com/u/12838403/20110822/pycon2011/]
[questions=off]
img0.png
What if the talks given at Kiwi Pie Con two thousand eleven could be easily watched by Python developers around the globe? Not as video, but as slideshows with computer generated voice over like this talk.

img1.png
In two thousand nine, I gave a short presentation on voice interaction at the first Kiwi Pie Con in Christchurch. I think maybe six people were in the room that day. But I posted the slides on slide share dot net and recorded and uploaded my voice, indicating through the slide casting interface when to advance each slide. In this way, anyone, anywhere could see and hear my talk at any time.

img2.png
Two years later, my talk has been viewed nearly three thousand times. Other talks I have posted have been watched hundreds of times. Now I cannot imagine giving a talk without putting it in a format for on-demand, on-line viewing.

img3.png
At first, it seems much easier to produce a screen cast than a slide cast. But as this handbook on screencasting points out, you need to worry about sound quality quite a bit.

img4.png
Screen casting can be very effective. Salman Khan created two thousand four hundred educational You Tube videos and they have been watched over seventy million times.

img5.png
Video also has drawbacks. The content of a video file is not searchable using Google. The video does not have structure the way a book or on-line text has structure, with a table of contents, sections and an index. And video files are huge and hard to distribute. All these problems with video may soon be solved, but meanwhile we have something else going on that is worth noting. 

img6.png
The wiki format, particularly Wikipedia, turns out to be extra ordinarily good at conveying bits of information. Because a wiki is mostly just text, it is searchable using Google. It is highly structured with lots of internal links. And it is relatively low bandwidth, including a mobile version which actually works for people with limited data plans.

img7.png
The quantity of infomation in the English language Wikipedia is huge. If printed, it would fill over fifteen hundred volumes. Our ability to find specific things in this huge collection is critical. 

img8.png
Searchable reference materials suggest searchable presentations should be useful as well. To make a presentation searchable, the words of the presentation must be exposed as text. So the talk must be written out. But we want to be able to hear a talk, not read it. So the text needs to be rendered into speech via text-to-speech.

img9.png
This line of reasoning results in a work flow which starts with a standard presentation plus a script for the voice over. From this we generate individual slide images and pre-recorded audio, generated using the script and the text-to-speech engine rather than making a recording with a microphone. This ensures consistent recording levels, perfect fidelity and no background noise. Finally, we wrap the slide images and corresponding audio files together on web pages for viewing.

img10.png
Because the slide images and associated audio files are not streaming from the server, the playback of the presentation can have an annoying network latency. One way around that is to zip all the files together, download them all at once, unzip them and play them locally. But this suggests an even better solution would be to play everything directly from a zip file. 

img11.png
The Open Document Presentation file format is a zip file. So to follow this path, we need to extend the Open Office slide show engine. We need the ability to play the script using the local text-to-speech engine. This solution delivers the presentation functionality we want, but misses out on a key element which made Wikipedia such a success: collaboration.

img12.png
If we go back to the work flow and put the script on the web instead of audio files, we dramatically reduce the bandwidth needed to distribute the presentation. The script can then also be collaboratively modified in place, just like a Wikipedia article. Slide images could also be modified or replaced on-line. Here, we need a custom player on the client to plays scripts from the wiki pages.

img13.png
Both approaches to distribution have been implemented in the Wiki-to-Speech system. On Android phones, the application has ZIP-to-Speech. The listing on the right shows how the zip file contains a presentation in the form of one script file and a set of slide image files.

img14.png
For playing the script from a wiki page, this application takes the U R L of the wiki page, parses the script and then makes a call to the local text-to-speech engine to generate the voice over for each slide on the fly.

img15.png
To find out more and download the code and compiled applications, please visit Wiki-to-Speech dot org.
```