from PIL import Image
import bitstring
import numpy as np
import argparse
import os

# all the command line stuff
full_path = os.path.dirname(__file__)

parser = argparse.ArgumentParser(description="A tool for creating Gameboy tilesets and maps.")

parser.add_argument('-in', action='store',dest='input_file', 
                    help='The file to be turned into a tileset.')

parser.add_argument('-o', action='store', dest='output_name',
                    default='NEW_SET',
                    help='The name for the destination file(s).')

parser.add_argument('-mF', action='store', dest="output_filepath",
                     default=full_path+'/output_default',
                     help='Set a destination folder with a filepath relative to this one.')

parser.add_argument('-dt', action='store_true', dest='keep_txt',
                    default=False,
                    help='Delete the created .txt file upon completion.')

parser.add_argument('-M', action='store_true', dest='use_map',
                    default=False,
                    help='Include a tilemap and an H file with details.')

command_args = parser.parse_args()

real_filepath = command_args.output_filepath
Image_Chosen = command_args.input_file
output_name = command_args.output_name

#gotta love global variables
global color_array
global byte_array
global hex_array


def main():
    # learned that different images use different alpha settings
    # so we need to make sure all the transparent is white
    # load image and make into Numpy array
    rgba = np.array(Image.open(Image_Chosen))

    # make transparencies white
    rgba[rgba[...,-1]==0] = [255,255,255,0]

    # turn back into PIL image and save
    Image.fromarray(rgba).save(Image_Chosen)

    #open the file
    im = Image.open(Image_Chosen, 'r')

    #turn the image to greyscale
    grey_im = im.convert('L')

    #start the pixel reader
    pix = grey_im.load()

    #change each pixel to the version rounded to the closest of the Gameboy colors, remove transparency
    for x in range (0, im.size[0]):
        for y in range(0, im.size[1]):
            pix[x,y] = Round_Greys(pix[x,y])
    
    #convert to tileset
    image_to_tileset(grey_im)

    tileset_to_c()


def image_to_tileset(image):
    global color_array
    global byte_array
    global hex_array
    color_array = {}
    byte_array = []
    hex_array = []

    black = 0
    d_grey = 85
    l_grey = 170
    white = 255

    pix = image.load()

    length_tiles = round(image.size[0] / 8)
    height_tiles = round(image.size[1] / 8)

    # get the color value for each pixel
    z=0
    for j in range(0, height_tiles):
        for i in range(0, length_tiles):
            for y in range(0, 8):
                for x in range(0, 8):
                    try:
                        color_array[z] = pix[x+(i*8),y+(j*8)]
                        z+=1
                    except IndexError:
                        print("\nIndex Error (OoR)")
                        return


    # turn each color into the corresponding bits      
    default_2_byte = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0]
    for i in range(0, len(color_array), 8):
        for j in range(0,8):
           temp = default_2_byte
           if (color_array[i+j] == black):
               temp[j] = 1
               temp[j+8] = 1
           if (color_array[i+j] == d_grey):
               temp[j] = 0
               temp[j+8] = 1
           if (color_array[i+j] == l_grey):
               temp[j] = 1
               temp[j+8] = 0
           if (color_array[i+j] == white):
               temp[j] = 0
               temp[j+8] = 0
        # print(temp)
        byte_array += temp
        


    # turn the bits into a string so we can edit it easier
    bin_temp = ""
    for i in range(0, len(byte_array)):
            bin_temp += str(byte_array[i])
    
    
    # turn the bits into bytes
    print("***")
    for i in range(0, len(bin_temp), 8):
        temp2 = ""
        for j in range(0, 8):
            temp2 += bin_temp[i+j]
        
        # print(temp2, "\n")
        temp = bitstring.BitArray(bin=temp2)
        hex_array.append(temp)

    Rhex_array = FormatAndReduce(hex_array)

    # write result to file, row-values separated by commas
    file = open(real_filepath+'/'+command_args.output_name+'.txt', 'w')
    total_string= ""
    for i in range(len(Rhex_array)):
        # print(Rhex_array[i])
        total_string += Rhex_array[i] + ','
        total_string += "\n"
    total_string = total_string[:-1]
    file.write(total_string)

# 255, 255, 255 = 00 = white
# 170, 170, 170 = 01 = l_gray
# 85, 85, 85 = 10 = d_gray
# 0, 0, 0 = 11 = black


def Round_Greys(input):
    black = 0
    d_grey = 85
    l_grey = 170
    white = 255
    range = 42.5

    #simple rounding
    if (input - range <= black):
        return black
    elif (input + range >= white):
        return white
    elif (input <= (d_grey + range) and input >= (d_grey - range)):
        return d_grey
    elif (input <= (l_grey + range) and input >= (l_grey - range)):
        return l_grey


def FormatAndReduce(hex_array):
    # create a temporary dictionary, making sure the True Blank is first
    temp_dict = {
        "0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00" : 1
    }

    new_array = []

    # add each tile as a key in the dictionary
    # which removes the possible identical tiles
    for i in range(0, len(hex_array), 16):
        temp_string =""
        for j in range(0, 16):
            temp_string += str(hex_array[i+j]) + ","
        
        temp_string = temp_string[:-1]
        temp_dict[temp_string] = 1
    
    # add the keys to the new array
    for key in temp_dict:
        new_array.append(key)
    # print(new_array)

    # return the new array
    return new_array


def c_file_format(map_bool, tileset_txt, filename):
    global hex_array

    # file header, credit to me <3
    header = "// GENERATED USING GBTILEMAKER BY GREEN_KNIGHT\n\n"

    # we're just making strings with the C code in them, simple enough
    set_unordered = "const unsigned char TileSet[] =\n{\n"+tileset_txt+"\n};\n\n"

    # turn the string of tiles into individual tiles
    tileset_list = tileset_txt.split("\n")
    tilemap_string = ""

    # I'm using this for tileSETS as well as maps,
    # that means that I don't always care about a header file
    if not map_bool:
        return header + set_unordered
    else:
        set_ordered = "const unsigned char TileMap[] =\n{\n"

        # this counting isn't technically needed
        # but it makes the output more readable
        count = 0

        # so, originally I had planend to just make the .txt and be done with it
        # and it didn't have any duplicate tiles because that'd be a waste
        # but then I realized I needed to make a tilemap for splash screen stuff
        # so what this section does is correctly index the tiles for the map 
        for i in range(0, len(hex_array), 16):
            tile = ""
            for j in range(0, 16):
                tile += hex_array[i+j]

            # The hex_array is just in order from top/bottom, left/right
            # the tileset_list is in the same order, but without duplicate tiles
            # so we check each tile in the hex_array, find it in tileset_list
            # then turn it into the hex equivalent of that index
            # because that's what GBDK uses in its tilemaps
            index_of = tileset_list.index(tile)
            hex_index_of = hex(index_of)

            # the python hex casting or function or whatever it's called
            # if the number is less than 16 it'll output something like "0x0" or "0x1"
            # and I prefer having it be "0x00" or "0x01"
            # it makes things line up nicer
            if index_of < 16:
                hex_index_of = str(hex_index_of)[:2]+"0"+str(hex_index_of)[2:]
            tilemap_string += hex_index_of+","

            # add a newline after each tile
            if count == 15:
                count = 0
                tilemap_string += '\n'
            else:
                count += 1
        
        # It helps to know how big your tileset is, it gets written to the header
        total_tileset_size = len(tileset_list)

        # there'd be a comma at the end that we wouldn't want
        tilemap_string = tilemap_string[:-1]
        
        # close off the C code snippet here
        set_ordered += tilemap_string+"\n};"

        # open the header file
        header_file = open(real_filepath+'/'+filename+".h", "w")

        # we need to get the image size for that header 
        im = Image.open(Image_Chosen)
        w, h = im.size
        
        w = int(w/8)
        h = int(h/8)

        # set some more C snippets
        map_width = "#define TileMap_width " + str(w) +"\n"
        map_height = "#define TileMap_height " + str(h) +"\n\n"
        map_size = "#define TileSet_size " + str(int(total_tileset_size))+"\n\n"
        other_params = "extern const unsigned char TileSet[];\n\n\nextern const unsigned char TileMap[];"

        # write to file
        header_file.write(header + map_width + map_height + map_size + other_params)
        
        #return the C code back where it was being written
        return header + set_unordered + set_ordered


def tileset_to_c():
    file_name = command_args.output_name
    txt_file = open(real_filepath+'/'+file_name+'.txt', 'r')
    set_txt = txt_file.read()
    txt_file.close()

    map_bool = command_args.use_map

    c_file = open(real_filepath+'/'+file_name+'.c', "w")
    c_file.write(c_file_format(map_bool, set_txt, file_name))

main()

if not command_args.keep_txt:
    os.remove(command_args.output_name+'.txt')