import Cimpl
import binascii


def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))


def encrypt(img, string):
    i = 0
    length = len(string) - 1
    for pixel in img:
        x, y, col = pixel
        r, g, b = col

        #Get red component of the pixel in binary in a list
        pixel_red_binary = list(('{0:08b}'.format(r)))

        #Get green component of the pixel in binary in a list
        pixel_green_binary = list(('{0:08b}'.format(g)))

        #Get blue component of the pixel in binary in a list
        pixel_blue_binary = list(('{0:08b}'.format(b)))

        #Set the last digit of the red component to the corresponding string binary value
        if i <= length:
            pixel_red_binary[-1] = string[i]
            i += 1

        #Set the last digit of the green component to the corresponding string binary value
        if i <= length:
            pixel_green_binary[-1] = string[i]
            i += 1

        #Set the last digit of the blue component to the corresponding string binary value
        if i <= length:
            pixel_blue_binary[-1] = string[i]
            i += 1

        #Convert the altered pixel red component in binary from a list to a string
        new_red = ''.join(str(e) for e in pixel_red_binary)
        new_red = int(new_red, 2)

        #Convert the altered pixel green component in binary from a list to a string
        new_green = ''.join(str(e) for e in pixel_green_binary)
        new_green = int(new_green, 2)

        #Convert the altered pixel blue component in binary from a list to a string
        new_blue = ''.join(str(e) for e in pixel_blue_binary)
        new_blue = int(new_blue, 2)

        #Create and Set color
        new_color = Cimpl.create_color(new_red, new_green, new_blue)
        Cimpl.set_color(img, x, y, new_color)


#load image
image = Cimpl.load_image(Cimpl.choose_file())


#Convert user input string to binary
string = input("Input the text you would like to hide:")
string = "*****" + string + '|||||'
string_in_bin = text_to_bits(string)
string_in_bin = list(string_in_bin)


#calculate how many bits we can alter
image_width = Cimpl.get_width(image)
image_height = Cimpl.get_height(image)
open_bits = image_width*image_height*3


#repeat string to cover entire image
string_bin_length = len(string_in_bin)
possible_repeat = open_bits//string_bin_length
extended_string = string_in_bin * possible_repeat
encrypt(image, extended_string)
Cimpl.save_as(image, 'newpic.png')
print("done")