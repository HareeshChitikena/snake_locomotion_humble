import matplotlib.pyplot as plt
import argparse


parser = argparse.ArgumentParser()


parser.add_argument("filename", help="name of the file")


args = parser.parse_args()


filename = args.filename

data_file = open('logs/'+ filename + '.txt', "r")
data_lines = data_file.readlines()


time = []
acceleration = []
position_setpoint = []
position_setpoint_error = []
velocity_setpoint = []
velocity_setpoint_error = []


for line in data_lines[1:]:
    line = line.strip().split(",")
    time.append(float(line[0]))
    acceleration.append(float(line[1]))
    position_setpoint.append(float(line[2]))
    position_setpoint_error.append(float(line[3]))
    velocity_setpoint.append(float(line[4]))
    velocity_setpoint_error.append(float(line[5]))


fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

ax1.plot(time, position_setpoint, label="position_setpoint")
ax1.plot(time, position_setpoint_error, label="position_setpoint_error")
ax1.set_ylabel("Position Data")
ax1.legend()


ax2.plot(time, velocity_setpoint, label="velocity_setpoint")
ax2.plot(time, velocity_setpoint_error, label="velocity_setpoint_error")
ax2.set_ylabel("Velocity Data")
ax2.set_xlabel("Time")
ax2.legend()


ax2_2 = ax2.twinx()
ax2_2.plot(time, acceleration, label="acceleration", color='C4')
ax2_2.set_ylabel("Acceleration Data")
ax2_2.legend()

plt.show() 
