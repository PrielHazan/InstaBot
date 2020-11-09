from selenium import webdriver
from time import sleep
import time
import random
from people_I_want_to_follow import people_i_want_to_follow
import pygame
import os
import sys
import asyncio

base_dir = getattr(sys, '_MEIPASS', os.getcwd())
def Path(relative_path):
    return os.path.join(base_dir, 'media', relative_path)


class InstaBot:
    def __init__(self, username, pw):
        self.driver = webdriver.Chrome(executable_path=Path('chromedriver.exe'))
        self.username = username
        self.driver.get("https://instagram.com")
        sleep(2)
        self.driver.find_element_by_xpath("//input[@name=\"username\"]")\
            .send_keys(username)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]")\
            .send_keys(pw)
        self.driver.find_element_by_xpath('//button[@type="submit"]')\
            .click()
        sleep(4)
        self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div/div/div/button")\
            .click()
        sleep(2)
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[3]/button[2]")\
            .click()
        sleep(2)

    def get_unfollowers(self):
        self.driver.find_element_by_xpath("//a[contains(@href,'/{}')]".format(self.username))\
            .click()
        sleep(2)
        self.driver.find_element_by_xpath("//a[contains(@href,'/followers')]")\
            .click()
        followers = self._get_names()
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[1]/div/div[2]/button")\
            .click()
        self.driver.find_element_by_xpath("//a[contains(@href,'/following')]")\
            .click()
        following = self._get_names()
        not_following_back = [user for user in following if user not in followers]
        print('Users dont follow you back: ', not_following_back)
        unfollow = input('Do you want to unfollow someone? (y/n)')
        if unfollow == 'n':
            print('Exit program')
            exit()
        elif unfollow == 'y':
            for name in not_following_back:
                action = input(f"Do you want to unfollow {name}? (y/n/exit)")
                if action == 'exit':
                    exit()
                elif action == 'y':
                    self.follow_or_unfollow_user(name, Action='unfollow')
                    #return to follow list
                    sleep(2)
        else:
            print('Invalid input, exit program')
            exit()

    def follow_or_unfollow_user(self, name, Action='follow'):
        if Action == 'unfollow':
            self.driver.find_element_by_xpath('//span[@aria-label="Following"]')\
                .click()
            sleep(2)
            self.driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[1]')\
                .click()
            sleep(2)
        else:
            followButton = self.driver.find_element_by_css_selector('button')
            sleep(2)
            if (followButton.text == 'Follow'):
                followButton.click()
                time.sleep(2)
            elif followButton.text == '':
                self.driver.find_element_by_xpath("//button[@type='button']")\
                    .click()
                sleep(2)
            else:
                print(f"You are already following {name}, or he follows you")
                print(followButton.text)

    def follow_people_who_follow_him(self, name=None, scrollTimes=3):
        self.driver.get("https://www.instagram.com/" + name + "/")
        self.driver.find_element_by_xpath("//a[contains(@href,'/followers')]")\
            .click()
        users_to_follow = self._get_names(scrollTimes=scrollTimes)
        for user in users_to_follow:
            self.driver.get('https://www.instagram.com/' + user + '/')
            self.follow_or_unfollow_user(user)
            sleep(2)


    def unfollow_everyone_except_list(self, people_i_want_to_follow):
        self.driver.find_element_by_xpath("//a[contains(@href,'/{}')]".format(self.username))\
            .click()
        sleep(2)
        self.driver.find_element_by_xpath("//a[contains(@href,'/following')]")\
            .click()
        sleep(2)
        following = self._get_names()
        sleep(2)
        unfollow_list = [user for user in following if user not in people_i_want_to_follow]
        sleep(2)
        for user in unfollow_list:
            self.driver.get('https://www.instagram.com/' + user + '/')
            sleep(2)
            self.follow_or_unfollow_user(user, Action='unfollow')
            sleep(2)






    def _get_names(self, scrollTimes='UntilEnd'):
        sleep(2)
        scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]")
        last_ht, ht = 0, 1
        if scrollTimes == 'UntilEnd':
            while last_ht != ht:
                last_ht = ht
                sleep(2)
                ht = self.driver.execute_script("""
                    arguments[0].scrollTo(0, arguments[0].scrollHeight);
                    return arguments[0].scrollHeight;
                    """, scroll_box)
        else:
            for times in range(scrollTimes):
                sleep(2)
                self.driver.execute_script("""
                    arguments[0].scrollTo(0, arguments[0].scrollHeight);
                    return arguments[0].scrollHeight;
                    """, scroll_box)

        links = scroll_box.find_elements_by_tag_name('a')
        names = [name.text for name in links if name.text != '']
        return names

    def like_hashtag_or_url_photos(self, hashtag=None, url=None, comments=None):
        driver = self.driver
        if url == None:
            driver.get("https://www.instagram.com/explore/tags/" + hashtag + "/")
        else:
            driver.get(url)
        time.sleep(2)

        # gathering photos
        pic_hrefs = []
        for i in range(1, 9):
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                # get tags
                hrefs_in_view = driver.find_elements_by_tag_name('a')
                # finding relevant hrefs
                hrefs_in_view = [elem.get_attribute('href') for elem in hrefs_in_view
                                 if '.com/p/' in elem.get_attribute('href')]
                # building list of unique photos
                [pic_hrefs.append(href) for href in hrefs_in_view if href not in pic_hrefs]
                # print("Check: pic href length " + str(len(pic_hrefs)))
            except Exception:
                continue

        # Liking photos
        for pic_href in pic_hrefs:
            driver.get(pic_href)
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 300);")
            try:
                driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/section[1]/span[1]/button')\
                        .click()
                if comments != None:
                    commentArea = driver.find_element_by_class_name('Ypffh')
                    commentArea.click()
                    commentArea = driver.find_element_by_class_name('Ypffh')
                    commentArea.click()
                    commentArea.send_keys(random.choice(comments))
                    driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/section[3]/div/form/button')\
                        .click()
                    time.sleep(8)
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(2)


# optional creating interface
# pygame.init()


# black = (0,0,0)
# white = (255,255,255)
# red = (255,0,0)
# Window_Width = 1000
# Window_Height = 500
# win = pygame.display.set_mode((Window_Width,Window_Height))
# pygame.display.set_caption("InstaBot")




# clock = pygame.time.Clock()

# Logo = pygame.image.load(Path('InstaBotLogo.png'))

# BackGround = pygame.image.load(Path('InstabotBG.jpg'))

# # music = pygame.mixer.music.load(Path(base_dir, 'music.wav'))

# # pygame.mixer.music.play(-1)



# button_press_delay = 0


# def text_objects(text, font):
#     textSurface = font.render(text, True, black)
#     return textSurface, textSurface.get_rect()

# def button(name, x, y, width, height, color, hoverColor, action=None):
#     global button_press_delay
#     mouse = pygame.mouse.get_pos()
#     click = pygame.mouse.get_pressed()
#     if x + width > mouse[0] > x and y+height > mouse[1] > y:
#         pygame.draw.rect(win, hoverColor, (x, y, width, height))

#         if click[0] == 1 and action != None and button_press_delay == 0:
#             print(f'Button name {name} clicked')
#             button_press_delay = 10
#             action()
#     else:
#         pygame.draw.rect(win, color, (x, y, width, height))

#     smallText = pygame.font.Font(Path("comicsans.ttf"), 20)
#     textSurf, textRect = text_objects(name, smallText)
#     textRect.center = ( (x + (width/2)), (y + (height/2)) )
#     win.blit(textSurf, textRect)

# def Main_Loop():
#     global button_press_delay
#     button_press_delay = 0
#     run = True

#     while run:
#         clock.tick(30)

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 sys.exit()

#             pos = pygame.mouse.get_pos()




#         def redrawGameWindow():
#             global button_press_delay
#             win.blit(BackGround, (0,0))
#             win.blit(Logo, (0,0))

#             button('Go back',850,10,100,50,(200, 0, 0),(200, 220, 20),get_unfollowers)

#             pygame.display.update()
#         redrawGameWindow()


# async def get_unfollowers():
#     my_bot = await InstaBot('prielhazan', 'priel2424')

# Main_Loop()



# actions
my_bot = InstaBot('username', 'passwords') #insert username and password
# my_bot.get_unfollowers()
# # comments = ['nice', 'looks good', 'wow']
# comments ["איזה יופי", 'מדהים']
# hashtag = 'game'
# my_bot.like_hashtag_or_url_photos(hashtag=hashtag, comments=comments)
# my_bot.follow_people_who_follow_him(name='omer_hazan', scrollTimes=10)
# my_bot.unfollow_everyone_except_list(people_i_want_to_follow)
