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
        pixel_blue_binary = list(('{0:08b}'.format(blue)))
        last_bit.append(pixel_blue_binary[-1])

last_bit = []
image = Cimpl.load_image(Cimpl.choose_file())
get_bin(image)
str1 = str()
list_to_string = ''.join(str(e) for e in last_bit)
text = text_from_bits(list_to_string)
text = text.split("*|*|*|*|*")
text = set(text)

#remove any null bytes
text = list(text)
hex = '\x00'
for element in text:
    if hex in element:
        text.remove(element)

#join and print hidden message
str1 = ''.join(text)
print(str1)
