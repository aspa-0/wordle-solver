from collections import Counter
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

url = 'https://www.nytimes.com/games/wordle/index.html'

driver = webdriver.Firefox(seleniumwire_options={'disable_encoding': True})
driver.get(url)
time.sleep(3)

play_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div[2]/button[2]')
play_button.click()
time.sleep(3)

close_how_to_play_button = driver.find_element(By.CLASS_NAME, "Modal-module_closeIcon__TcEKb")
close_how_to_play_button.click()
time.sleep(2)

settings_button = driver.find_element(By.CSS_SELECTOR, '#settings-button > svg:nth-child(1)')
settings_button.click()
time.sleep(2)

hard_mode = driver.find_element(By.CSS_SELECTOR, '#Hard\\ Mode > button:nth-child(1) > span:nth-child(1)')
hard_mode.click()

close_settings = driver.find_element(By.CSS_SELECTOR, '.Modal-module_closeIcon__TcEKb > svg:nth-child(1) > path:nth-child(1)')
close_settings.click()
time.sleep(2)

action = ActionChains(driver)

with open('wordle-solver/answers.txt', 'r') as f:
    possible_words = f.read()

possible_words = possible_words.replace('"', '').split(',')

def calculate_letter_frequencies(words):
    """Get frequency of each letter"""
    letter_count = Counter()
    for word in words:
        letter_count.update(word)
    return letter_count

def score_words(word, letter_frequencies):
    """give score to each word based on letter frequencies"""
    return sum(letter_frequencies[char] for char in set(word))

def guess_word(guess, attempts):
    action.send_keys(guess).perform()
    action.send_keys(Keys.ENTER).perform()
    time.sleep(5)
    
    grid = driver.find_element(By.CSS_SELECTOR, ".Board-module_board__jeoPS")
    count = 1
    feedback_list = ''
    row_number = 'Row ' + str(attempts)

    for div in grid.find_elements(By.TAG_NAME, "div"):
        if count == 6:
            break
        if div.accessible_name == (row_number):
            for row_div in div.find_elements(By.TAG_NAME, "div"):
                accessible_name = row_div.accessible_name

                if accessible_name.startswith(str(count)):
                    count += 1
                    if 'absent' in accessible_name:
                        feedback_list += 'B'
                    elif 'present' in accessible_name:
                        feedback_list += 'Y'
                    elif 'correct' in accessible_name:
                        feedback_list += 'G'

    return feedback_list

def filter_words(possible_words, guess, feedback):
    filtered_words = []
    
    for word in possible_words:
        match = True
        for i in range(len(guess)):
            if feedback[i] == 'G' and word[i] != guess[i]:
                match = False
                break
            elif feedback[i] == 'Y' and (guess[i] not in word or word[i] == guess[i]):
                match = False
                break
            elif feedback[i] == 'B' and guess[i] in word:
                match = False
                break
        if match:
            filtered_words.append(word)

    return filtered_words


def solve_wordle(possible_words):
    """solve wordle what else do you expect"""
    letter_frequencies = calculate_letter_frequencies(possible_words)
    attempts = 1
    current_words = possible_words[:]
    used_guessable_words = False
    # if you want to use a specific first word you can change it from plate to any other. 
    # If not make first_word = False to use the default word from the algorithm
    first_word = True

    while len(current_words) > 0:
        scored_words = [(word, score_words(word, letter_frequencies)) for word in current_words]

        scored_words.sort(key=lambda x: x[1], reverse=True)
        if first_word:
            guess = 'plate'
            first_word = False
        else:
            guess = scored_words[0][0]
        print(f'Guess #{attempts}: {guess}')

        feedback = guess_word(guess, attempts)

        if feedback == '' or feedback == 'GGGGG':
            try:
                action.send_keys(Keys.ESCAPE).perform()
                time.sleep(2)
                action.send_keys(Keys.ESCAPE).perform()
                time.sleep(2)

                stats_button = driver.find_element(By.CSS_SELECTOR, '#stats-button > svg:nth-child(1)')
                stats_button.click()
                time.sleep(2)

                share_button = driver.find_element(By.CSS_SELECTOR, '.Footer-module_shareButton__cHprS')
                share_button.click()
                time.sleep(2)
                
                print(f'Word found: {guess} in {attempts} attempts.')
                print('Congratulations! Wordle results copied to clipboard.')
                return guess
            except Exception:
                print('Error occured while getting feedback.')
                return None

        print(f'Feedback received: {feedback}')
        print()
        
        current_words = filter_words(current_words, guess, feedback)
        attempts += 1

        if len(current_words) <= 0 and not used_guessable_words:
            possible_words = None
            used_guessable_words = True

            with open('wordle/guessable.txt', 'r') as f:
                possible_words = f.read()

            possible_words = possible_words.replace('"', '').split(',')

            current_words = filter_words(possible_words, guess, feedback)
    
    print('No valid words found :(')
    return None


solve_wordle(possible_words)
driver.quit()