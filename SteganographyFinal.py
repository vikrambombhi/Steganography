import Cimpl
import binascii
import time


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


if __name__ == "__main__":
    main_loop = True

    while main_loop:
        print("To Encrypt text into a image enter 'E'.\nTo Decrypt a image enter 'D'.\nIf you would like to Quit enter 'Q'")
        command = input('Select:')

        if command == 'E' or command == 'e':
            print('You have selected to encrypt a image. A file browser has opened please select the image you would like to encrypt. The file browser may be underneath another window.')
            #load image
            image = Cimpl.load_image(Cimpl.choose_file())

            #Convert user input string to binary
            string = input("Input the text you would like to hide:")
            string = '*****' + string + '|||||'
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
            filename = input('What would you like to name the encrypted photo:') + '.png'
            Cimpl.save_as(image, filename)
            print("The image has been encrypted\n\nThis program will restart in 5 seconds\n\n")
            time.sleep(5)

        if command == 'D' or command == 'd':
            #set variables
            last_bit = []
            str1 = str()
            set_of_strings = []
            #load image
            print('Please slect the image you would like to decrypt. The file dialog may be underneath another window')
            image = Cimpl.load_image(Cimpl.choose_file())
            #start decryption process
            get_bin(image)
            list_to_string = ''.join(str(e) for e in last_bit)
            try:
                start = list_to_string.rindex('0010101000101010001010100010101000101010') + len('0010101000101010001010100010101000101010')
                end = list_to_string.rindex('0111110001111100011111000111110001111100', start)
                str1 = list_to_string[start:end]
            except ValueError:
                print('No text found. The image may have been altered beyond the capabilities of this program. You may try to crop and save a section of the image that you belive to be unaltered but this section must be large enough to contain the entire text to be a viable option')
            char = text_from_bits(str1)
            print('The encrypted text is:\n'+char+'\n\nThis program will restart in 30 seconds')
            time.sleep(30)

        if command == 'Q' or command == 'q':
            main_loop = False

        else:
            print("That is not a command")