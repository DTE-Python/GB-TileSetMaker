console.log("Script Running")

const col = app.pixelColor;
const img = app.activeImage;

const BLACK = 0
const WHITE = 255
const L_GREY = 170
const D_GREY = 85

pixel_list = []

color_list = []
/* 
    Too many for loops for my liking
    Iterate through each pixel in tile-based (8x8 square) order
    and add them to the list
*/
for (var j = 0; j < Math.round(img.height /8); j++){

    for (var i = 0; i < Math.round(img.width/8); i++){

        for (var y = 0; y < 8; y++){
           
            for(var x = 0; x<8; x++){
                
                try {
                    temp = img.getPixel(x+(i*8),y+(j*8))

                    // To Do: create a temporary greyscale image, similar to Python version
                    if (col.rgbaR(temp) + col.rgbaG(temp) + col.rgbaB(temp) != 3 * col.rgbaR(temp)){
                        throw new Error("Invalid Color(s)")
                    }
                    if (!color_list.includes(col.rgbaR(temp))){
                     
                        color_list.push(col.rgbaR(temp))
                    }
                    pixel_list.push(col.rgbaR(temp))
                    
                } catch (error) {
                    console.log("error")
                }
                
            }
            
        }
        
    }
    
}

/*
    To Do: Round every color to one of the four allowed colors,
        eliminating these errors
*/
if(color_list.length != 4){
    throw new Error("Invalid Amount of Colors")
}
if (color_list.includes(0) || color_list.includes(85) || color_list.includes(170) || color_list.includes(255)){
    throw new Error("Invalid Color Values")
}

// an array of every row of pixels, stored in the binary 2 bytes
bytes_bin_list = Pix_To_2_Byte(pixel_list)

// a long string of 1s and 0s
byte_string_temp = ""
for (var i = 0; i < bytes_bin_list.length; i++){
    byte_string_temp += String(bytes_bin_list[i]).replace(/,/g, "")
}

// turn the binary numbers into hex, and format them to be recognizable in the C code
image_hex_values = []
for (var i = 0; i < byte_string_temp.length; i += 8){
    byte_string_temp2 = ""
    for (var j = 0; j < 8; j++){
        byte_string_temp2 += byte_string_temp[i+j]
    }

    convert_byte_to_hex = "0x" + (parseInt(byte_string_temp2, 2).toString(16).length == 2 ? parseInt(byte_string_temp2, 2).toString(16) : "0" + parseInt(byte_string_temp2, 2).toString(16))

    image_hex_values.push(convert_byte_to_hex)
}

reduced_hex_array = FormatAndReduce(image_hex_values)

// Puts every 8 bytes into the proper tile format, and removes duplicates
function FormatAndReduce(array){
    new_array = ["0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00"]
    
    for (var i =0; i < array.length; i+=16){
        temp_string =""
        for (var j =0; j < 16; j++){
            temp_string += array[i+j] + ","
        }
        temp_string = temp_string.substring(0, temp_string.length -1)

        if (new_array.includes(temp_string) == false){
            new_array.push(temp_string)
        }
    }
    return new_array
}

// Converts every row of pixels into the appropriate format
function Pix_To_2_Byte(list){
    pix_byte_value = []

    default_2byte_format = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0]
    for (var i = 0; i < list.length; i+= 8){
        for (var j = 0; j < 8; j++){
           
           convert_bit_to_byte = default_2byte_format

           if (list[i+j] == BLACK){
               convert_bit_to_byte[j] = 1
               convert_bit_to_byte[j+8] = 1
           }
           if (list[i+j] == D_GREY){
               convert_bit_to_byte[j] = 0
               convert_bit_to_byte[j+8] = 1
           }
           if (list[i+j] == L_GREY){
               convert_bit_to_byte[j] = 1
               convert_bit_to_byte[j+8] = 0
           }
           if (list[i+j] == WHITE){
               convert_bit_to_byte[j] = 0
               convert_bit_to_byte[j+8] = 0
           }
        }

        pix_byte_value += convert_bit_to_byte
    }

    return pix_byte_value
}

// Format the tiles with some fluff to make it readable
string_containing_tileset= ""
for (var i = 0; i < reduced_hex_array.length; i++){ 

    string_containing_tileset += "// Tile "+(i).toString()+"\n"
    string_containing_tileset += reduced_hex_array[i] + ','
    string_containing_tileset += "\n"
}
string_containing_tileset = string_containing_tileset.substring(0, string_containing_tileset.length -1)


// create and save the header file, create the tilemap
function c_formatting(greyimage_pixHexValues, tileset_string){
    tileset_string = tileset_string.substring(0, tileset_string.length -1)

    header = "// GENERATED USING GBTILEMAKER BY GREEN_KNIGHT\n\n"

    set_unordered = "const unsigned char TileSet[] =\n{\n"+tileset_string+"\n};\n\n"

    tileset_list = tileset_string.split("\n")

    tilesetNoComment_list = []
    for (var i = 0; i < tileset_list.length; i++){
        if (tileset_list[i].includes("//") == false){
            tilesetNoComment_list.push(tileset_list[i])
        }
    }

    tilemap_string = ""

    set_ordered = "const unsigned char TileMap[] =\n{\n"

    count = 0

    for (var i = 0; i < greyimage_pixHexValues.length; i +=16){
        tile = ""
        for (var j = 0; j < 16; j++){
            tile += greyimage_pixHexValues[i+j] + ','
        }
        
        index_of = tilesetNoComment_list.indexOf(tile)
        if (tilesetNoComment_list.indexOf(tile) == -1){
        	index_of = tilesetNoComment_list.length -1
        }
        
        hex_index_of = "0x" + (index_of < 16 ? "0" : "") +  index_of.toString(16)

        tilemap_string += hex_index_of+","

        if (count == 15){
            count = 0
            tilemap_string += "\n"
        }
        else{
            count +=1
        }
    }

    total_tileset_size = tilesetNoComment_list.length
    
    tilemap_string = tilemap_string.substring(0, tilemap_string.length -1)

    set_ordered += tilemap_string+"\n};"

    w = Math.trunc(img.width / 8)
    h = Math.trunc(img.height / 8)

    map_width = "#define TileMap_width " + w.toString() +"\n"
    map_height = "#define TileMap_height " + h.toString() +"\n\n"
    map_size = "#define TileSet_size " + total_tileset_size.toString()+"\n\n"
    other_params = "extern const unsigned char TileSet[];\n\n\nextern const unsigned char TileMap[];"

    SaveFile((header + map_width + map_height + map_size + other_params), 'h', "RENAME_THIS_HEADER")

    return header + set_unordered + set_ordered;
}


// Libresprite file manipulation
function SaveFile(value, extension, name){
    storage.set(value, extension, name);
    storage.save(extension,name);
    storage.unload(extension,name);
}

// saving results
SaveFile(c_formatting(image_hex_values, string_containing_tileset), 'c', "RENAME_THIS_FILE")