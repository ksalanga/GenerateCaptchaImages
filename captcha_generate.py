from os import listdir
from selenium import webdriver
import sys
import csv
import re


def nat_sort(lis):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(lis, key=alphanum_key)


# Create new Selenium firefox driver
def start_driver():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True
    return webdriver.Firefox(options=firefox_options)


def store_chars_in_dict(solution, number_of_alphanumerics, count, dict_of_chars):
    for char in solution:
        try:  # If value exists in the dictionary add to the count
            dict_of_chars[char][1] += 1
        except KeyError:  # If value does not exist in the dictionary
            dict_of_chars[char] = [False, 1]

        # increase the counter once we reach our target value
        if (dict_of_chars[char][0] is False) and (dict_of_chars[char][1] >= int(number_of_alphanumerics)):
            print('Finished ' + char + ' with number ' + str(dict_of_chars[char][1]))
            dict_of_chars[char][0] = True
            count += 1

    # print(solution + ')\n')
    print(dict_of_chars)
    return count  # updates count if any new alphanumeric has reached our target value


def collect_images(site, file_directory, number_of_alphanumerics, dict_of_chars):
    driver = start_driver()
    driver.get(site)

    number_of_alphanums_filled = 0
    # starting off with no images
    image_number = -1  # counter for the current image

    # first instance of opening website does not require a refresh
    latest_image_string = get_latest_image_string(image_number, file_directory)
    word_start = latest_image_string.index(')') + 1
    sol = latest_image_string[word_start: word_start + 5]
    number_of_alphanums_filled = store_chars_in_dict(sol, number_of_alphanumerics,
                                                     number_of_alphanums_filled, dict_of_chars)
    image_number += 1  # Created 0th image

    # Collect Images until we have N or more of each Alphanumeric
    while number_of_alphanums_filled <= 62:
        driver.refresh()
        latest_image_string = get_latest_image_string(image_number, file_directory)
        word_start = latest_image_string.index(')') + 1
        sol = latest_image_string[word_start: word_start + 5]
        # print('IMAGE NUMBER ' + str(image_number) + ')')
        number_of_alphanums_filled = store_chars_in_dict(sol, number_of_alphanumerics,
                                                         number_of_alphanums_filled, dict_of_chars)
        image_number += 1

    driver.close()
    return image_number


def get_latest_image_string(image_count, file_directory):
    # The reason it is + 3 is because we account for the "images before the new one" which is image_count minus 1
    # and the text file which is another minus 1, so add that to counteract for +2, once the new image pops up
    # that is another + 1 so + 3.

    # Second part of the or handles if a new image arrives and it goes after the solution.txt
    while len(listdir(file_directory)) != (image_count + 3) \
            or listdir(file_directory)[len(listdir(file_directory)) - 1] != "solution.txt":
        continue

    # print('Last file:' + listdir(file_directory)[len(listdir(file_directory)) - 1])
    # print('image count + 1' + str((image_count + 1)))
    latest_image_str = nat_sort(listdir(file_directory))[image_count + 1]

    print('LATEST IMAGE STRING :' + latest_image_str)

    return latest_image_str


def sort_dict(dict_of_chars):
    list_of_alphabet_tuples = [(key, value[1]) for key, value in dict_of_chars.items() if str(key).isalpha()]
    list_of_number_tuples = [(key, value[1]) for key, value in dict_of_chars.items() if str(key).isnumeric()]
    list_of_alphabet_tuples.sort()
    list_of_number_tuples.sort()
    list_of_alphabet_tuples.extend(list_of_number_tuples)
    return dict(list_of_alphabet_tuples)


def store_alphanumerics(dict_of_chars, n):
    csv_file = open('alphaNumericCount.csv', 'wt')
    writer = csv.writer(csv_file)

    for key in dict_of_chars:
        csv_row = [key, dict_of_chars[key]]
        writer.writerow(csv_row)

    writer.writerow([n])
    csv_file.close()


# execute program here
if __name__ == "__main__":
    if len(sys.argv) == 1 or len(sys.argv) == 4:
        if len(sys.argv) == 1:
            website = 'http://127.0.0.1:81/drupal/'  # A default drupal site
            directory = ''  # directory where the current script resides
            number_of_each_alphanumeric = 100
        else:
            website = sys.argv[1]
            directory = sys.argv[2]
            number_of_each_alphanumeric = sys.argv[3]
        dict_of_alphanumerics = {}

        print('Collecting images of alphanumeric sample size: ' + str(number_of_each_alphanumeric))

        # Once the Image Collection is complete, it will return the total number of images
        number_of_images = collect_images(website, directory, number_of_each_alphanumeric, dict_of_alphanumerics)

        # Sort the dictionary of alphanumerics
        sorted_dict_of_alphanumerics = sort_dict(dict_of_alphanumerics)

        # Store dict into a CSV
        store_alphanumerics(sorted_dict_of_alphanumerics, number_of_images)

        print('Finished!')
    else:
        print('Arguments: [site] [directory] [n] (DO NOT INCLUDE BRACKETS)\n'
              'Where:\n'
              '[site] = Drupal url so that the bot can constantly refresh for new Captchas\n'
              '[directory] = directory where PHP script will be generating images\n'
              '[n] = number of each alphanumeric you want collected (will be >= n by end of script)\n'
              'OR\n'
              'no arguments at all'
              '(defaults will be standard drupal site w/ port and current directory where python script is and n=100)'
              '**DEFAULT NO ARGS MOST LIKELY WILL NOT WORK SINCE BITNAMI HAS DIFFERENT DRUPAL SITE PORTS FOR URL**')
