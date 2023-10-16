# GB-TileSetMaker
A quick program to turn a given image into a hex tileset for GBDK usage.

<h1>Usage:</h1>
  I set this up to be used in the Linux command line, it probably doesn't work on Windows<br>
  but I don't think that's too hard of a change.<br><br>
  Commands:<br>python3 createSet.py -in [<i>FILE...</i>] [<i>OPTION...</i>] 
<h2>Options:</h2>
<b>-o [<i>FILE...</i>]</b><br>
Short for "out." The name of the file(s) to output to. You don't need to specify the extention. By default this is "NEW_SET"<br>
<b>-mF [<i>FILEPATH...]</i></b><br>
Short for "move folder." You can set the folder of output to <i>FILEPATH</i>. By default this is "/output_default"<br>
<b>-dt</b><br>
Short for "delete txt." A .txt file is always generated, but it isn't needed after the program finishes. Use this option to remove it.<br>
<b>-M</b><br>
Short for "Map." Use this option to generate a header file with the '.h' extention.

<h2>Notes:</h2>
<b>Unless you specify an output folder you will have to create the "/output_default" folder.</b><br>
<br>This tool works best with small images, because big ones are impractical for the Gameboy.<br>
I'm not too savvy with GitHub or really Python in general, but this tool works for me, so I'm happy.
