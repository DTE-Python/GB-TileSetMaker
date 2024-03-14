# GB-TileSetMaker
A quick program to turn a given image into a hex tileset for GBDK usage.

<h1>Usage (Terminal):</h1>
  I set this up to be used in the Linux command line, it probably doesn't work on Windows<br>
  but I don't think that's too hard of a change. Uses the .py file.<br><br>
  Commands:<br>python3 createSet.py -in [<i>FILE...</i>] [<i>OPTION...</i>] 
<h2>Options:</h2>
<b>-o [<i>FILE...</i>]</b><br>
Short for "out." The name of the file(s) to output to. You don't need to specify the extention. By default this is "NEW_SET"<br>
<b>-mF [<i>FILEPATH...]</i></b><br>
Short for "move folder." You can set the folder of output to <i>FILEPATH</i>. By default this is "/output_default"<br>
<b>-DG [<i>INT...</i>]</b><br>
Short for "Dark Grey." Set a custom value for your dark grey colors, between 0 and 255. Defaults to 85. Must be lower than the light grey value.<br>
<b>-LG [<i>INT...</i>]</b><br>
Short for "Light Grey." Set a custom value for your light grey colors, between 0 and 255. Defaults to 170. Must be higher than the dark grey value. <br>
<h1>Usage (LibreSprite):</h1>
  Put the .js file into LibreSprite's Scripts folder. Run it on the desired image in LibreSprite.<br>
  Output, unless something is different, will be in the main LibreSprite folder. Files would be named "RENAME_THIS_FILE.c" and "RENAME_THIS_HEADER.h";<br>
  this is because if you run the plugin again it will overwrite the files with those names.
<h2>Notes:</h2>
<b>(Terminal) Unless you specify an output folder you will have to create the "/output_default" folder.</b><br>
<br>This tool works best with small images, because big ones are impractical for the Gameboy.<br>
I'm not too savvy with GitHub or really Python/JavaScript in general, but this tool works for me, so I'm happy.

<h3>Planned:</h3>
LibreSprite plugin working(?). GIMP not currently planned. Animation support being looked into. Going to make sure it works on Windows.
