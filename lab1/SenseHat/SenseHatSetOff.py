from sense_hat import SenseHat

is_off = [0, 0, 0]
is_red = [255, 0, 0]
is_yellow = [255, 215, 0]
is_green = [0, 255, 0]
is_black = [0, 0, 80]

RED_ROW = 0
YELLOW_ROW = 1
GREEN_ROW = 2

CAR_COLUMN = 0
PED_COLUMN = 1

class SenseHatSetOff:

    def __init__(self):
        self.sense = SenseHat()
        self.switch_off()

    def switch_off(self):
        self.sense.set_pixels([is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off,
                               is_off, is_off, is_off, is_off, is_off, is_off, is_off, is_off])

    def set_red(self, tlt):
        column = CAR_COLUMN
        if tlt == "ped":
            column = PED_COLUMN
        else:
            self.sense.set_pixel(column,YELLOW_ROW, is_off)

        self.sense.set_pixel(column,RED_ROW, is_red)
        self.sense.set_pixel(column,GREEN_ROW, is_off)

    def set_green(self, tlt):
        column = 0
        if tlt == "ped":
            column = 1
        else:
            self.sense.set_pixel(column,YELLOW_ROW, is_off)

        self.sense.set_pixel(column,RED_ROW, is_off)
        self.sense.set_pixel(column,GREEN_ROW, is_green)

    def set_yellow(self):
        self.sense.set_pixel(CAR_COLUMN,RED_ROW, is_off)
        self.sense.set_pixel(CAR_COLUMN,YELLOW_ROW, is_yellow)
        self.sense.set_pixel(CAR_COLUMN,GREEN_ROW, is_off)

    def set_red_yellow(self):
        self.sense.set_pixel(CAR_COLUMN,RED_ROW, is_red)
        self.sense.set_pixel(CAR_COLUMN,YELLOW_ROW, is_yellow)
        self.sense.set_pixel(CAR_COLUMN,GREEN_ROW, is_off)


    def set_off(self, tlt):
        self.sense.set_pixel(CAR_COLUMN,RED_ROW, is_red)
        self.sense.set_pixel(CAR_COLUMN,YELLOW_ROW, is_yellow)
        self.sense.set_pixel(CAR_COLUMN,GREEN_ROW, is_off)
        self.sense.set_pixel(PED_COLUMN,RED_ROW, is_red)
        self.sense.set_pixel(PED_COLUMN,GREEN_ROW, is_off)


SenseHatSetOff()
