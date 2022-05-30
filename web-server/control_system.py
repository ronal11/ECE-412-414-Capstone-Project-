import eventlet, math
import stepper_module as s
import servo_module as ser
import RPi.GPIO as GPIO
from get_distance import measure_distance

class ControlSystem(object):
    def __init__(self, frame_width):
        # Rotation parameters
        self.x_cord        = 0
        self.deg_range_p   = 180
        self.deg_range_n   = -180
        self.deg_blind     = 10
        self.deg_per_step  = 3.6
        self.last_step_cw  = self.deg_range_p - self.deg_per_step
        self.last_step_ccw = self.deg_range_n + self.deg_per_step
        self.deg_limit_p   = self.deg_range_p - 1
        self.deg_limit_n   = self.deg_range_n + 1

        # Frame parameters
        self.frame_width   = frame_width
        self.center_frame  = (self.frame_width / 2) - 1
        self.camera_fov    = 62.2
        self.alpha         = self.camera_fov / 2

        # constants used for calculating angle to track
        self.a = self.frame_width / 2
        self.tracking_thresh = 30 # 30 pixels translates to a 1.61 degree error in aim

        # gpio pins
        self.step_pin     = 3
        self.direc_pin    = 5
        self.servo_pin    = 7
        self.button_pin   = 37
        self.solenoid_pin = 33

        # Other parameters
        self.delay = .009
        self.verbose_sweep = True
        self.verbose_track = True
        self.started       = True
        self.cw            = True
        self.solenoid_open = False
        self.Pest          = False
        self.start         = True

        # Hardware initialization
        self.initialize_motors()
        self.initialize_gpio()
        eventlet.sleep(5)

    def initialize_gpio(self):
        """Initializes all Raspberry Pi GPIO pins

        Returns:
            Nothing
        """
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(solenoid_pin, GPIO.OUT)
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(button_pin, GPIO.FALLING)
        GPIO.output(solenoid_pin, GPIO.LOW)

    def initialize_motors(self):
        """Initializes all motor devices (stepper and servo)

        Returns:
            Nothing
        """
        self.motor = s.stepper(self.step_pin, self.direc_pin)
        self.servo = ser.servo(self.servo_pin, 50, "servo1")

    def initial_start_position(self):
        """This function sets servo and motor to an initial position, returns start variable as false,
           should only run at the start once

        Returns:
            start, a boolean value as false
        """
        if self.start:
            self.motor.rotate_stepper(180, 'ccw', self.delay, self.verbose)
            self.servo.set_angle(130)
            self.start = False
        return self.start

    def set_x_cord(self, x_cord):
        """Updates the x rotational coordinate

        Args:
            x_cord: Rotational x-coordinate

        Returns:
            Nothing
        """
        self.x_cord = x_cord

    def get_x_cord(self):
        """Updates the x rotational coordinate

        Returns:
            x_cord: Current rotational x-coordinate
        """
        return self.x_cord

    def get_distance(self):
        """This function measures distance using ultrasonic sensor

        Returns:
            Distance measured in meters
        """

        while True:
            d = measure_distance() # measure distance

            if d < 0 or d > 400: # sensor max range is 400
                d = measure_distance()
            else:
                break
        return d / 100 # Returns a distance in meters

    def servo_angle_needed(self, center_degree):
        """This function calculates an angle to rotate the servo given a distance measured from a pest,
           in order for stream of water to ideally hit pest

        Returns:
            An angle to rotate servo
        """

        # consant params for equation
        v0 = 2  # velocity of water needs to be estimated
        v0_2 = pow(v0, 2)
        g = 9.8

        d = self.get_distance()  # get a distance

        print("distance measured: ", d)
        C = g * d
        angle = 0.5 * math.degrees(math.asin(C / v0_2))  # might not work

        needed_angle = center_degree + angle  # potencial bug
        return needed_angle

    def return_to_init_pos(self):
        """This function returns platform back to starting intial position, when a button is pressed

        Returns:
            Nothing
        """

        if self.motor.relative_pos < 0:  # if position is to the left
            eventlet.sleep(1)
            temp = abs(self.motor.relative_pos)
            print(temp)
            self.motor.rotate_stepper(temp, 'cw', self.delay, self.verbose)  # rotate back to center according to current position
            print("back to initial from ccw")
            quit()
        elif self.motor.relative_pos > 0:  # if position is to the right
            eventlet.sleep(1)
            temp = abs(self.motor.relative_pos)
            print(temp)
            self.motor.rotate_stepper(temp, 'ccw', self.delay, self.verbose)  # rotate back to center according to current position
            print("back to initial from cc")
            quit()

    def motor_sweep(self):
        """This function sweeps the platform 180 degree's back and forth, it is the passive movement of the system
           (N.B. the stepper operates with a 2:1 gear ratio, so directions are reversed for stepper and main platform)

        Returns:
            Current direction of sweeping motion (bool)
        """

        if self.cw:  # if stepper motor is currently rotating clockwise (platform is rotating ccw)
            if self.motor.relative_pos > self.last_step_cw:  # used to detect when an increment of 3.6 will bring platform over allowed range
                print(self.motor.relative_pos)
                degree = self.deg_range_p - self.motor.relative_pos  # calulate needed angle to bring to extrenum
                print('greater than 176.4, degrees needed: ', degree)
                self.motor.rotate_stepper(degree, 'cw', self.delay, self.verbose)  # rotate to extrenum, in the case of the stepper (180 degrees clockwise)

            curr = self.motor.relative_pos

            if curr > self.deg_limit_p:  # if current position is greater than 179
                self.cw = False  # start rotating stepper motor in ccw direction
            else:
                self.motor.rotate_stepper(self.deg_per_step, 'cw', self.delay, self.verbose)  # else, rotate cw in 3.6 increments

        else:  # if stepper is rotating ccw
            if self.motor.relative_pos < self.last_step_ccw:
                print(self.motor.relative_pos)  # process same as above
                degree = self.deg_range_p - abs(self.motor.relative_pos)
                print('less than -176.4', degree)
                self.motor.rotate_stepper(degree, 'ccw', self.delay, self.verbose)

            curr = self.motor.relative_pos

            if curr < self.deg_limit_n:
                self.cw = True
            else:
                self.motor.rotate_stepper(self.deg_per_step, 'ccw', self.delay, self.verbose)
        return self.cw

    def track_pest(self, x_cord_detected):
        """This function takes cordinates and motor object, calculates cordinates and degree to rotate stepper appropriately

        Args:
            x_cord_detected: Cordinate received from CV used to calculate angle to rotate stepper

        Returns:
            Nothing
        """

        x_cord_detected = x_cord_detected - self.center_frame  # calculate x cordinate, will produce a negative or pos, which corresponds to the left or right of center cord respectivley
        print("x_cord_detected = ", x_cord_detected)
        abs_x_cord = abs(x_cord_detected)  # get abs value of x cordinate, will be used to see if x cord is over threshold

        k = abs_x_cord * math.tan(math.radians(self.alpha))  # calculation for equation to track

        if abs_x_cord < self.tracking_thresh:  # if x-cord is less than threshold, don't move in hopes of preventing jittering in stepper motor
            print("below tracking threshold")
            eventlet.sleep(1)
        elif x_cord_detected > 0:  # if x-cord is > 0 move to platform to the right (big gear), this means moving stepper motor to the left(Small gear)
            dir = 'cw'
            angle_2_rotate = 2 * (math.degrees(math.atan(k / self.a)))  # calculate angle (N.B. multiplied by two because of 2:1 gear ratio)

            calc = self.motor.relative_pos + angle_2_rotate  # calculate new position that will result
            print("calc is: ", calc)

            if calc > self.deg_range_p:  # if new position results in stepper motor going out of range (-180 deg small gear == 90 deg big gear)
                print("angle required over {0}".format(self.deg_range_p))
                if angle_2_rotate > self.deg_blind:
                    temp = angle_2_rotate - self.deg_blind
                    angle_2_rotate = self.deg_range_p - temp
                    print("changed directions to CCW")
                    dir = 'ccw'
                else:
                    angle_2_rotate = self.deg_range_p - self.motor.relative_pos  # calculate new angle to bring stepper motor to max range in hopes to still deter pest

            print("rotate {0}: {1} deg: ".format(dir, angle_2_rotate / 2))
            self.motor.rotate_stepper(angle_2_rotate, dir, self.delay, self.verbose)  # rotate stepper CCW, translates to rotating platform to the right by angle_2_rotate/2 (2:1 ratio)
            eventlet.sleep(1)
        elif x_cord_detected < 0:  # if x-cord is < 0 move to platform to the left (big gear), this means moving stepper motor to the right(Small gear)
            dir = 'ccw'
            angle_2_rotate = 2 * (
                math.degrees(math.atan(k / a)))  # calculate angle (N.B. multiplied by two because of 2:1 gear ratio)

            calc = self.motor.relative_pos - angle_2_rotate  # calculate new position that will result
            print("calc is: ", calc)

            if calc < self.deg_range_n:  # if new position results in stepper motor going out of range (180 deg small gear == -90 deg big gear)
                print("angle required over {0}".format(self.deg_range_n))
                if angle_2_rotate > self.deg_blind:
                    temp = angle_2_rotate - self.deg_blind
                    angle_2_rotate = self.deg_range_p - temp
                    print("changed directions to CW")
                    dir = 'cw'
                else:
                    angle_2_rotate = self.deg_range_p + self.motor.relative_pos  # calculate new angle to bring stepper motor to max range in hopes to still deter pest

            print("rotate {0}: {1} deg: ".format(dir, angle_2_rotate / 2))
            self.motor.rotate_stepper(angle_2_rotate, dir, self.delay, self.verbose)  # rotate stepper CW, translates to rotating platform to the left by angle_2_rotate/2 (2:1 ratio)
            eventlet.sleep(1)