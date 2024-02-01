from PIL import Image
import bitstring
import numpy as np
import argparse
import os


full_path = os.path.dirname(__file__)

parser = argparse.ArgumentParser(description="A tool for creating Gameboy tilesets and maps.")

parser.add_argument('-in', action='store',dest='input_file', 
                    help='The file to be turned into a tileset.')

parser.add_argument('-o', action='store', dest='output_name',
                    default='NEW_SET',
                    help='The name for the destination file(s).')

parser.add_argument('-mF', action='store', dest="output_filepath",
                     default=full_path+'/output_default',
                     help='Set a destination folder with a filepath.')

parser.add_argument('-DG', action='store', dest='dark_grey',
                    default=85,
                    help='Set the value to round Dark Grey to, between 0 and 255. Defaults to 85.')

parser.add_argument('-LG', action='store', dest='light_grey',
                    default=170,
                    help='Set the value to round Light Grey to, between 0 and 255. Defaults to 170.')

command_args = parser.parse_args()

real_filepath = command_args.output_filepath
Image_Chosen = command_args.input_file
output_name = command_args.output_name

D_GREY = int(command_args.dark_grey)
L_GREY = int(command_args.light_grey)
BLACK = 0
WHITE = 255

def main():
    base_image_alpha = np.array(Image.open(Image_Chosen))

    original_image_copy = base_image_alpha

    # make transparencies white if alpha exists
    if (base_image_alpha.ndim ==3):
        base_image_alpha[base_image_alpha[...,-1]==0] = [255,255,255,0]

        # turn back into PIL image and save
        Image.fromarray(base_image_alpha).save(Image_Chosen)

    # open the file
    converted_image_alpha = Image.open(Image_Chosen, 'r')

    # turn the image to greyscale
    greyscale_image = converted_image_alpha.convert('L')

    # start the pixel reader
    pix = greyscale_image.load()

    # change each pixel to the version rounded to the closest of the Gameboy colors, remove transparency
    for x in range (0, converted_image_alpha.size[0]):
        for y in range(0, converted_image_alpha.size[1]):
            pix[x,y] = Round_Greys(pix[x,y])
    
    # Convert the image to a tileset, the tileset to C, and finish outputting
    greyIm_PixHexVals, tileset_string = image_to_tileset(greyscale_image)

    tileset_to_c(greyIm_PixHexVals, tileset_string)
    
    Image.fromarray(original_image_copy).save(Image_Chosen)

def image_to_tileset(image):

    greyscale_image_pix_hex_values = []

    greyscale_image_pix_values = {}

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
                        greyscale_image_pix_values[z] = pix[x+(i*8),y+(j*8)]
                        z+=1
                    except IndexError:
                        print("\nIndex Error (OoR)")
                        return
        
    greyscale_image_pix_byte_value = Convert_Colors_To_2_Byte_Format(greyscale_image_pix_values)

    # turn the bits into a string so we can edit it easier
    byte_string_temp = ""
    for i in range(0, len(greyscale_image_pix_byte_value)):
            byte_string_temp += str(greyscale_image_pix_byte_value[i])
    
    
    # turn the bits into bytes
    print("***")
    for i in range(0, len(byte_string_temp), 8):
        byte_string_temp2 = ""

        for j in range(0, 8):
            byte_string_temp2 += byte_string_temp[i+j]

        convert_byte_to_hex = bitstring.BitArray(bin=byte_string_temp2)
        greyscale_image_pix_hex_values.append(convert_byte_to_hex)

    reduced_hex_array = FormatAndReduce(greyscale_image_pix_hex_values)

    # save results to string
    string_containing_tileset= ""

    for i in range(len(reduced_hex_array)):

        string_containing_tileset += "// Tile "+str(i+1)+"\n"
        string_containing_tileset += reduced_hex_array[i] + ','
        string_containing_tileset += "\n"

    string_containing_tileset = string_containing_tileset[:-1]

    return greyscale_image_pix_hex_values, string_containing_tileset

def Round_Greys(input):
    
    range_White_LightGrey = (WHITE - L_GREY)/2
    range_LightGrey_DarkGrey = (L_GREY - D_GREY)/2
    range_DarkGrey_Black = (D_GREY)/2

    if (input - range_DarkGrey_Black <= BLACK):
        return BLACK
    elif (input + range_White_LightGrey >= WHITE):
        return WHITE
    elif (input <= (D_GREY + range_LightGrey_DarkGrey) and input >= (D_GREY - range_DarkGrey_Black)):
        return D_GREY
    elif (input <= (L_GREY + range_White_LightGrey) and input >= (L_GREY - range_LightGrey_DarkGrey)):
        return L_GREY

def Convert_Colors_To_2_Byte_Format(gi_pv):

    greyscale_image_pix_byte_value = []

    default_2byte_format = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0]
    for i in range(0, len(gi_pv), 8):
        for j in range(0,8):
           
           convert_byte_to_hex = default_2byte_format

           if (gi_pv[i+j] == BLACK):
               convert_byte_to_hex[j] = 1
               convert_byte_to_hex[j+8] = 1

           if (gi_pv[i+j] == D_GREY):
               convert_byte_to_hex[j] = 0
               convert_byte_to_hex[j+8] = 1

           if (gi_pv[i+j] == L_GREY):
               convert_byte_to_hex[j] = 1
               convert_byte_to_hex[j+8] = 0

           if (gi_pv[i+j] == WHITE):
               convert_byte_to_hex[j] = 0
               convert_byte_to_hex[j+8] = 0

        # print(temp)
        greyscale_image_pix_byte_value += convert_byte_to_hex

    return greyscale_image_pix_byte_value

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

    # return the new array
    return new_array

def c_file_format(greyimage_pixHexValues, tileset_string, filename):

    # file header, credit to me <3
    header = "// GENERATED USING GBTILEMAKER BY GREEN_KNIGHT\n\n"

    # we're just making strings with the C code in them, simple enough
    set_unordered = "const unsigned char TileSet[] =\n{\n"+tileset_string+"\n};\n\n"

    # turn the string of tiles into individual tiles
    tileset_list = tileset_string.split("\n")

    # for c file readability we add comments to show tiles
    tilesetNoComment_list =[]
    for i in range(len(tileset_list)):
        if "//" not in tileset_list[i]:
            tilesetNoComment_list.append(tileset_list[i])

    tilemap_string = ""

    
    set_ordered = "const unsigned char TileMap[] =\n{\n"

    # this counting isn't technically needed
    # but it makes the output more readable
    count = 0

    # creating the tilemap by indexing the tiles (some are used more than once) 
    for i in range(0, len(greyimage_pixHexValues), 16):
        tile = ""
        for j in range(0, 16):
            tile += greyimage_pixHexValues[i+j]

        index_of = tilesetNoComment_list.index(tile)
        hex_index_of = hex(index_of)

        # format hex number to '0x00' (rather than '0x0)
        if index_of < 16:
            hex_index_of = str(hex_index_of)[:2]+"0"+str(hex_index_of)[2:]
        tilemap_string += hex_index_of+","

        # add a newline after each tile
        if count == 15:
            count = 0
            tilemap_string += '\n'
        else:
            count += 1
    
    # find the size of the tileset for header params
    total_tileset_size = len(tilesetNoComment_list)

    # remove redundant comma
    tilemap_string = tilemap_string[:-1]
    
    # close off the C code
    set_ordered += tilemap_string+"\n};"

    # open the header file
    header_file = open(real_filepath+'/'+filename+".h", "w")

    # get image size
    im = Image.open(Image_Chosen)
    w, h = im.size
    
    w = int(w/8)
    h = int(h/8)

    # set additional C snippets
    map_width = "#define TileMap_width " + str(w) +"\n"
    map_height = "#define TileMap_height " + str(h) +"\n\n"
    map_size = "#define TileSet_size " + str(int(total_tileset_size))+"\n\n"
    other_params = "extern const unsigned char TileSet[];\n\n\nextern const unsigned char TileMap[];"

    # write to file
    header_file.write(header + map_width + map_height + map_size + other_params)
    
    #return the C code back where it was being written
    return header + set_unordered + set_ordered

def tileset_to_c(greyimage_pixHexValues, tileset_string):
    file_name = command_args.output_name

    c_file = open(real_filepath+'/'+file_name+'.c', "w")
    c_file.write(c_file_format(greyimage_pixHexValues, tileset_string, file_name))

errorFlag_1 = False

if (L_GREY <= D_GREY):
    print ("Error: Light Grey less than Dark Grey")
    errorFlag_1 = True
if (L_GREY >= WHITE):
    print ("Error: Light Grey bigger than White")
    errorFlag_1 = True
if(D_GREY <= BLACK):
    print("Error: Dark Grey less than Black")
    errorFlag_1 = True
if(L_GREY <= BLACK):
    print("Error: Light Grey less than Black")
    errorFlag_1 = True
if(D_GREY >= WHITE):
    print("Error: Dark Grey bigger than White")
    errorFlag_1 = True
if(not errorFlag_1):
    main()