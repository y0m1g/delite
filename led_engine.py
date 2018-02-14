import time
import neopixel
import colour

LED_COUNT_TOTAL = 120
LED_LINES	    = 2
LED_COUNT       = LED_COUNT_TOTAL / LED_LINES
LED_GPIO        = 18
LED_FREQ_HZ     = 800000
LED_DMA         = 10
LED_BRIGHTNESS  = 255
LED_INVERT      = False
LED_CHANNEL     = 0
LED_STRIP       = neopixel.ws.WS2811_STRIP_GRB

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return neopixel.Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return neopixel.Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return neopixel.Color(0, pos * 3, 255 - pos * 3)

class LedEngine(object):

	def __init__(self):
		self.strip = neopixel.Adafruit_NeoPixel(LED_COUNT_TOTAL, LED_GPIO, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
		self.strip.begin()
		
	def setPixel(self, pos, color):
		self.strip.setPixelColor(pos, color)
		self.strip.setPixelColor(LED_COUNT_TOTAL-pos-1, color)

	def setAllPixels(self, color):
		for i in range(LED_COUNT_TOTAL):
			self.strip.setPixelColor(i, color)
		self.strip.show()
		
	def setColor(self, r, g, b):
		self.setAllPixels(neopixel.Color(r, g, b))
		
	def turnOn(self):
		self.setColor(255, 255, 255)

	def turnOff(self):
		self.setColor(0, 0, 0)
		
	def setBrightness(self, brightness):
		self.strip.setBrightness(brightness)
		self.strip.show()
	
	def getBrightness(self):
		return self.strip.getBrightness()
			
	def _ramping_gradient(self, color_center, color_end, ratio, minutes):
		self.setBrightness(0)
		self.gradient(color_center, color_end, ratio)
		wait_ms = minutes * 60 * 1000 / 255.0
		for bright in range(0, 256, 1):
			self.setBrightness(bright)
			time.sleep(wait_ms/1000.0)
			
	def sunset(self, minutes=10):
		self._ramping_gradient("red", "darkorange", 0.6, minutes)
			
	def sunrise(self, minutes=10):
		self._ramping_gradient("blue", "yellow", 0.6, minutes)
				
	def gradient(self, color_center="red", color_grad="yellow", ratio=1.0):
		center = int(float(ratio)*LED_COUNT)
		grad_1 = grad_2 = []
		if center > 0:
			grad_1 = list(colour.Color(color_grad).range_to(colour.Color(color_center), center))
		if center < LED_COUNT:
			grad_2 = list(colour.Color(color_center).range_to(colour.Color(color_grad), LED_COUNT-center))
		colors = grad_1 + grad_2
		for i in range(LED_COUNT):
			r, g, b = colors[i].get_rgb()
			self.setPixel(i, neopixel.Color(int(255.0*r), int(255.0*g), int(255.0*b)))
		self.strip.show()
		
	def gradMove(self, color_center="red", color_grad="yellow", iterations=5, wait_ms=10):
		pixels_range = range(LED_COUNT)
		for n in range(iterations):
			for i in pixels_range:
				ratio = (float(i)+1) / LED_COUNT
				self.gradient(color_center, color_grad, ratio)
				time.sleep(wait_ms/1000.0)
			for i in reversed(pixels_range):
				ratio = (float(i)+1) / LED_COUNT
				self.gradient(color_center, color_grad, ratio)
				time.sleep(wait_ms/1000.0)
	
	def glow(self, iterations=5, wait_ms=5):
		bright_range = range(0, 256, 1)
		for n in range(iterations):
			for i in reversed(bright_range):
				self.setBrightness(i)
				time.sleep(wait_ms/1000.0)
			for i in bright_range:
				self.setBrightness(i)
				time.sleep(wait_ms/1000.0)
						
	def colorWipe(self, color, wait_ms=50):
		"""Wipe color across display a pixel at a time."""
		for i in range(LED_COUNT):
			self.setPixel(i, color)
			self.strip.show()
			time.sleep(wait_ms/1000.0)
		
	def rainbowCycle(self, iterations=5, wait_ms=20):
		"""Draw rainbow that uniformly distributes itself across all pixels."""
		for j in range(256*iterations):
			for i in range(LED_COUNT):
				self.setPixel(i, wheel((int(i * 256 / LED_COUNT) + j) & 255))
			self.strip.show()
			time.sleep(wait_ms/1000.0)