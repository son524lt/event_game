import pygame, sys, random, serial, os
import importlib.resources as resources
def load_sound(sound_filename):
    return os.path.join(sys._MEIPASS, 'sound', sound_filename)
# Load image function
def load_image(image_filename):
    return os.path.join(sys._MEIPASS, 'assets', image_filename).convert()

def load_image(image_filename):
	with resources.open_binary('assets', image_filename) as image_file:
		return io.BytesIO(image_file.read())

def draw_floor():
	screen.blit(floor_surface,(floor_x_pos,900))
	screen.blit(floor_surface,(floor_x_pos + 576,900))
	screen.blit(floor_surface,(floor_x_pos + 1247,900))

def create_pipe():
	random_pipe_pos = random.choice(pipe_height)
	bottom_pipe = pipe_surface.get_rect(midtop = (1200,random_pipe_pos))
	top_pipe = pipe_surface.get_rect(midbottom = (1200,random_pipe_pos - 300))
	# bottom_pipe = pipe_surface.get_rect(midtop = (700,random_pipe_pos))
	# top_pipe = pipe_surface.get_rect(midbottom = (700,random_pipe_pos - 300))
	return bottom_pipe,top_pipe

def move_pipes(pipes):
	for pipe in pipes:
		pipe.centerx -= 5
	visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
	return visible_pipes

def draw_pipes(pipes):
	for pipe in pipes:
		if pipe.bottom >= 1024:
			screen.blit(pipe_surface,pipe)
		else:
			flip_pipe = pygame.transform.flip(pipe_surface,False,True)
			screen.blit(flip_pipe,pipe)

def check_collision(pipes):
	global can_score
	for pipe in pipes:
		if bird_rect.colliderect(pipe):
			death_sound.play()
			can_score = True
			return False

	if bird_rect.top <= -100 or bird_rect.bottom >= 900:
		can_score = True
		return False

	return True

def rotate_bird(bird):
	new_bird = pygame.transform.rotozoom(bird,-bird_movement * 3,1)
	return new_bird

def bird_animation():
	new_bird = bird_frames[bird_index]
	new_bird_rect = new_bird.get_rect(center = (100,bird_rect.centery))
	return new_bird,new_bird_rect

def score_display(game_state):
	if game_state == 'main_game':
		score_surface = game_font.render(str(int(score)),True,(255,255,255))
		# score_rect = score_surface.get_rect(center = (288,100))
		score_rect = score_surface.get_rect(center = (512,100))
		screen.blit(score_surface,score_rect)
	if game_state == 'game_over':
		score_surface = game_font.render(f'Score: {int(score)}' ,True,(255,255,255))
		score_rect = score_surface.get_rect(center = (512,100))
		# score_rect = score_surface.get_rect(center = (288,100))
		screen.blit(score_surface,score_rect)

		high_score_surface = game_font.render(f'High score: {int(high_score)}',True,(255,255,255))
		# high_score_rect = high_score_surface.get_rect(center = (288,850))
		high_score_rect = high_score_surface.get_rect(center = (512,850))
		screen.blit(high_score_surface,high_score_rect)

def update_score(score, high_score):
	if score > high_score:
		high_score = score
	return high_score

def pipe_score_check():
	global score, can_score 
	
	if pipe_list:
		for pipe in pipe_list:
			if 95 < pipe.centerx < 105 and can_score:
				score += 1
				score_sound.play()
				can_score = False
			if pipe.centerx < 0:
				can_score = True

#pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 2, buffer = 1024)
pygame.init()
screen = pygame.display.set_mode((1024,1024))
# screen = pygame.display.set_mode((576,1024))
clock = pygame.time.Clock()
game_font = pygame.font.Font(os.path.join(sys._MEIPASS, 'font', '04B_19.ttf'),40)

# Game Variables
gravity = 0.2
bird_movement = 0
game_active = True
score = 0
high_score = 0
can_score = True
# bg_surface = pygame.image.load(load_image('uet1.png')).convert()
bg_surface = pygame.image.load(load_image('background-day.png')).convert()
bg_surface = pygame.transform.scale2x(bg_surface)

floor_surface = pygame.image.load(load_image('base.png')).convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0

bird_downflap = pygame.transform.scale2x(pygame.image.load(load_image('bluebird-downflap.png')).convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load(load_image('bluebird-midflap.png')).convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load(load_image('bluebird-upflap.png')).convert_alpha())
bird_frames = [bird_downflap,bird_midflap,bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (100,512))

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP,200)

# bird_surface = pygame.image.load(load_image('bluebird-midflap.png')).convert_alpha()
# bird_surface = pygame.transform.scale2x(bird_surface)
# bird_rect = bird_surface.get_rect(center = (100,512))

pipe_surface = pygame.image.load(load_image('pipe-green.png'))
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE,1200)
pipe_height = [400,600,800]

game_over_surface = pygame.transform.scale2x(pygame.image.load(load_image('message.png')).convert_alpha())
game_over_rect = game_over_surface.get_rect(center = (512,512))
# game_over_rect = game_over_surface.get_rect(center = (288,512))

flap_sound = pygame.mixer.Sound(load_sound('sfx_wing.wav'))
death_sound = pygame.mixer.Sound(load_sound('sfx_hit.wav'))
score_sound = pygame.mixer.Sound(load_sound('sfx_point.wav'))
score_sound_countdown = 100
SCOREEVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SCOREEVENT,100)

port = "COM10"
baudrate = 250000
ser = serial.Serial(port, baudrate, timeout=1)
pygame.display.set_caption('FlappyBird')
while True:
	if ser.in_waiting > 0:
		data = ser.read().decode('utf-8')
		if (data == 'u' or data == 'd' or data == 'r' or data == 'l') and game_active:
			bird_movement = 0
			bird_movement -= 10
			flap_sound.play()
		if (data == 'u' or data == 'd' or data == 'r' or data == 'l') and game_active == False:
			game_active = True
			pipe_list.clear()
			bird_rect.center = (100,300)
			bird_movement = 0
			score = 0
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		# if event.type == pygame.KEYDOWN:
		# 	if event.key == pygame.K_SPACE and game_active:
		# 		bird_movement = 0
		# 		bird_movement -= 12
		# 		flap_sound.play()
		# 	if event.key == pygame.K_SPACE and game_active == False:
		# 		game_active = True
		# 		pipe_list.clear()
		# 		bird_rect.center = (100,512)
		# 		bird_movement = 0
		# 		score = 0

		if event.type == SPAWNPIPE:
			pipe_list.extend(create_pipe())

		if event.type == BIRDFLAP:
			if bird_index < 2:
				bird_index += 1
			else:
				bird_index = 0

			bird_surface,bird_rect = bird_animation()

	screen.blit(bg_surface,(0,0))

	if game_active:
		# Bird
		bird_movement += gravity
		rotated_bird = rotate_bird(bird_surface)
		bird_rect.centery += bird_movement
		screen.blit(rotated_bird,bird_rect)
		game_active = check_collision(pipe_list)

		# Pipes
		pipe_list = move_pipes(pipe_list)
		draw_pipes(pipe_list)
		
		# Score
		pipe_score_check()
		score_display('main_game')
	else:
		screen.blit(game_over_surface,game_over_rect)
		high_score = update_score(score,high_score)
		score_display('game_over')


	# Floor
	floor_x_pos -= 1
	draw_floor()
	if floor_x_pos <= -576:
		floor_x_pos = 0
	

	pygame.display.update()
	clock.tick(120)
