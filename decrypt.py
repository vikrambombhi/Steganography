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


def get_bin(img):
    for pixel in img:
        x, y, col = pixel
        red, green, blue = col

        #Get each component of the pixel in binary in a list
        pixel_red_binary = list(('{0:08b}'.format(red)))
        last_bit.append(pixel_red_binary[-1])

        #Get each component of the pixel in binary in a list
        pixel_green_binary = list(('{0:08b}'.format(green)))
        last_bit.append(pixel_green_binary[-1])

        #Get each component of the pixel in binary in a list
        pixel_blue_binary = list(('{0:08b}'.format(blue)))
        last_bit.append(pixel_blue_binary[-1])

#set variables
last_bit = []
str1 = str()
set_of_strings = []
#load image
image = Cimpl.load_image(Cimpl.choose_file())
#start decryption process
get_bin(image)
cut_off = len(last_bit)//8
last_bit = last_bit[:((cut_off*8)+1)]
num_of_characters = (Cimpl.get_height(image)*Cimpl.get_width(image)*3)//8
for i in range(num_of_characters-1):
    i = i*8
    set_of_strings.append(last_bit[0+i:8+i])
count = 0
#print(len(set_of_strings))
end = '*|*|*|*|*'
for set in set_of_strings:
    count += 1
    char = ''.join(str(e) for e in set)
    char = text_from_bits(char)
    str1 += char
    if str1 != end and str1.find(end) != -1:
        break

str1.strip('*|*|*|*|*')
print(str1)
