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


def func(img, string1):
    for (x, y, col), strr in zip(img, string1):
        red, green, blue = col

        #Get blue component of the pixel in binary in a list
        pixel_blue_binary = list(('{0:08b}'.format(blue)))

        #Set the last digit of the component to the corresponding string binary value
        pixel_blue_binary[-1] = strr

        #Convert the altered pixel component in binary from a list to a string
        new_blue = ''.join(str(e) for e in pixel_blue_binary)

        #convert the each componets new data from binary to int
        new_blue = int(new_blue, 2)
        new_color = Cimpl.create_color(red, green, new_blue)
        Cimpl.set_color(img, x, y, new_color)



#Convert user input string to binary
string = input("Input the text you would like to hide:")
string = "*|*|*|*|*" + string + "*|*|*|*|*"
string_in_bin = text_to_bits(string)
string_in_bin = list(string_in_bin)



#load image
image = Cimpl.load_image(Cimpl.choose_file())

#calculate how many bits we can alter
image_width = Cimpl.get_width(image)
image_height = Cimpl.get_height(image)
open_bits = image_width*image_height


#repeat string to cover entire image
string_bin_length = len(string_in_bin)
possible_repeat = open_bits//string_bin_length
extended_string = string_in_bin * possible_repeat

func(image, extended_string)
Cimpl.save_as(image, 'newpic.png')
print("done")