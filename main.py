import wnck
import time

import pyscreenshot as ImageGrab
import cv2
import numpy as np
import logging

import pyautogui
import random

import ConfigParser

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)-5s] %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger('kancolle-auto')

window = None

def get_window(name):
    name = name.lower()
    screen = wnck.screen_get_default()
    screen.force_update()

    target = None
    for w in screen.get_windows():
        if name in w.get_name().lower():
            target = w
            break

    return target

def activate_window(window):
    import gtk
    now = gtk.gdk.x11_get_server_time(gtk.gdk.get_default_root_window())
    window.activate(now)

    time.sleep(3) # waiting window activated

def load_template(template_path):
    logger.info("loading template %s",  template_path)
    template = cv2.imread(template_path, 0)
    w, h = template.shape[::-1]
    return template, w, h

def load_template_2(template_path):
    logger.info("loading template %s",  template_path)
    template = cv2.imread(template_path, 0)
    return template

def get_size(template):
    return template.shape[::-1]

def match(window, template, threshold):
    # capture window
    x, y, w, h = window.get_client_window_geometry()
    im = ImageGrab.grab(bbox=(x, y, x+w, y+h), backend='scrot')
    im = np.array(im.convert('RGB'))
    # to grayscale image array
    cv_img = im.astype(np.uint8)
    cv_gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    # find template in window
    res = cv2.matchTemplate(cv_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    logger.info('template matching result: %s', max_val)

    if max_val >= threshold:
        return (x + max_loc[0],  y + max_loc[1])
    else:
        return None

def match_2(window, template, threshold):
    # capture window
    x, y, w, h = window.get_client_window_geometry()
    im = ImageGrab.grab(bbox=(x, y, x+w, y+h), backend='scrot')
    im = np.array(im.convert('RGB'))
    # to grayscale image array
    cv_img = im.astype(np.uint8)
    cv_gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    # find template in window
    res = cv2.matchTemplate(cv_gray, template, cv2.TM_CCOEFF_NORMED)
    locs = np.where(res >= threshold)
    # get template size
    t_w, t_h = get_size(template)
    # put midpoint of found template in list
    founds = [] 
    for l in zip(*locs[::-1]):
        found = (x + l[0] + int(t_w/2),  y + l[1] + int(t_h/2))
        founds.append(found) 

    return founds

def normal_rand(mean, size):
    if size == 0:
        return mean

    half_size = int(size/2)
    sigma = int(half_size/4) # diveded by 4 for make sure all value in size (devided by 3 with 99.7%)

    value = np.random.normal(mean, sigma)
    return int(value)

def gauss_rand(mean, size):
    if size == 0:
        return mean

    half_size = int(size/2)
    sigma = int(half_size/4) # diveded by 4 for make sure all value in size (devided by 3 with 99.7%)

    value = np.random.normal(mean, sigma)
    return int(value)

def is_exists(template_path, sleep_time=2, threshold=0.80):
    logger.info('find %s', template_path)
    template = load_template_2(template_path)
    result = match_2(window, template, threshold=threshold)
    return len(result) != 0

def find(template_path, threshold=0.80):
    logger.info('find all of %s', template_path)
    template = load_template_2(template_path)
    result = match_2(window, template, threshold)
    return None if len(result) == 0 else result[0]

def find_all(template_path, threshold=0.80):
    logger.info('find all of %s', template_path)
    template = load_template_2(template_path)
    result = match_2(window, template, threshold)
    return result

def click(target, sleep_time=2, offset=(0,0), threshold=0.80, fake=False):

    if isinstance(target, tuple):
        x, y = target
    else:
        template = load_template_2(target)
        founds = match_2(window, template, threshold)

        if not founds:
            raise Exception('Not found %s' % target)

        x, y = founds[0]
        w, h = get_size(template)
        x = gauss_rand(x, w) if offset == (0,0) else x
        y = gauss_rand(y, h) if offset == (0,0) else y

    x += offset[0] + random.randrange(-5, 5)
    y += offset[1] + random.randrange(-5, 5)

    logger.info('click (%s,%s)', x, y)
    
    if fake:
        pyautogui.moveTo(x, y, duration=0.2, tween=pyautogui.easeInOutQuad)
    else:
        pyautogui.click(x, y, duration=0.2, tween=pyautogui.easeInOutQuad)

    time.sleep(sleep_time)

def click_if_exists(template_path, sleep_time=2, offset=None, threshold=0.80):
    try:
        click(template_path, sleep_time=sleep_time, offset=offset, threshold=threshold)
        return True
    except:
        logger.info("not found %s, but it's ok", template_path)
        time.sleep(sleep_time)
        return False

def goaway():
    x, y = pyautogui.size()
    pyautogui.moveTo(x, y, duration=0.2, tween=pyautogui.easeInOutQuad)

def wait(template_paths, timeout=10, threshold=0.80):

    logger.info('waiting %s', template_paths)
    if type(template_paths) is not list:
        template_paths = [template_paths]

    templates = []
    for path in template_paths:
        t, _, _ = load_template(path)
        templates.append(t)

    count = 0
    while count < timeout:
        for index, template in enumerate(templates):
            result = match(window, template, threshold)
            if result is not None:
                return index
        count += 1
        time.sleep(1)

    return -1

#def is_exists(template_path):
#    loc = pyautogui.locateOnScreen(template_path)
#    return loc != None

def levelup():
    # before combat
    
    click('operation.png')
    click('sortie.png')
    click('world_3.png')
    click('kis_island.png')
    click('confirm.png')
    click('start_sortie.png')
    wait('compass.png')
    click('compass.png')
    wait("formation.png")
    click('formation.png', offset=(-130,-30))
    # after combat
    templates = ['next.png', 'leave_combat.png']
    found = wait(templates, timeout=120)
    click(templates[found])
    if found == 1:
        wait('next.png')
        click('next.png')

    wait('next.png')
    click('next.png')
    templates = ['get_new.png', 'retreat.png']
    found = wait(templates)
    click(templates[found])
    if found == 0:
        wait('retreat.png')
        click('retreat.png')
 
def repair():
    click('docking.png')
    dockers = find_all('docker.png', threshold=0.95)
    logger.info('docker is left %s', len(dockers))

    # repair fleet 1
    for docker in dockers:
        click(docker)
        result = find_all('1.png')
        for pos in result:
            click(pos)
            click('start_repair.png')
            if not is_exists('yes_or_no.png'):
                click(docker)
            else:
                click('yes_or_no.png', offset=(100,0))
                break

        click(docker)

    # docker 2
    #click('dockers.png', offset=(-210,-30), fake=True)
    '''
    for dockers in docker

    result = find_all('1.png')
    for pos in result:
        click(pos)
        click('start_repair.png')
        if not is_exists('yes.png'):
            click(pos)
        else:
            click('yes.png')

    for pos in result:
    for damage in ['heavy_damage.png','moderate_damage.png', 'minor_damage.png']:
        found = click_if_exists(damage)
        if not found:
            continue
        click('start_repair.png')
        click('yes.png')
    '''
    click('goback.png')
    goaway()

def resupply(check_list=[1,2,3,4]):
    click('resupply.png', sleep_time=3)
    for i in check_list:
        click('resupply_%s.png' % i)
        click_if_exists('select_bar.png', offset=(0,-150))

    click('goback.png')
    goaway()

def check_expedition_back():

    is_back = False

    while True:
        result = wait('expedition_back.png', timeout=5)
        if result == -1:
            break

        is_back = True
        click('expedition_back.png')
        wait('next.png')
        click('next.png')
        wait('next.png')
        click('next.png')

    return is_back

def expedition(nums):

    click('operation.png')    
    click('expedition.png')

    for i in xrange(3):
        fleet_num = i + 2
        expedition_num = nums[i]
        world_num = expedition_num / 8 + 1
        click('expedition/world_%s.png' % world_num, sleep_time=3)
        click('expedition/expedition_%s.png' % expedition_num, threshold=0.90)
        if is_exists('stop_expedition.png'):
            continue
        click('confirm.png')
        if fleet_num != 2:
            click('resupply_%s.png' % fleet_num )
        click('start_expedition.png')
        wait('stop_expedition.png')
        time.sleep(5)

    click('goback.png')

def check_quest():
    click('quest.png')
    click('oyodo.png')
    click('quest_tags.png', offset=(0,-50))
    while True:
        done = find('done.png')
        if done is None:
            break
        click(done)
        while True:
            close = find('close.png')
            if close is None:
                break
            click(close)

    click('leave_quest.png')

def check_combat_ready():
    click('resupply.png', sleep_time=3)
    click_if_exists('select_bar.png', offset=(0,-150))
    is_repairing = is_exists('repairing.png')

    click('goback.png')
    goaway()
    return not is_repairing
    
if __name__ == '__main__':
    
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    expedution_nums = [int(config.get('expedition', str(x))) for x in range(2,4+1)]

    wait_base = int(config.get('wait_time', 'base'))
    wait_offset = int(config.get('wait_time', 'offset'))

    window = get_window('poi')
    activate_window(window)

    while True:
        #click_if_exists('goback.png')
        goaway()
        check_expedition_back()

        check_quest()
        check_expedition_back()
        is_ready = check_combat_ready()
        logger.info('ready to combat: %s', is_ready)
        check_expedition_back()

        if is_ready:
            levelup()
            check_expedition_back()
            repair()
            check_expedition_back()

        while True:
            resupply()
            is_back = check_expedition_back()
            if not is_back:
                break

        expedition(expedution_nums)
        wait_time = wait_base + random.randrange(wait_offset)
        logger.info('wait %s seconds...', wait_time)
        time.sleep(wait_time)
