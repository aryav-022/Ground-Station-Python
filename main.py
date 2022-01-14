from tkinter import *
from tkinter.messagebox import showinfo
from threading import Timer, Thread
import cv2
from datetime import datetime
from time import sleep

# System Variables
start = False
stage = 0
cansat_released = False
activate_buzzer = False
camera = False
start_time = None
data = []

# Other Variables
vid = None

# Defining Origin Points for Graph and other custom variables
o_x = 60
o_y = 540

# Thread Variables
t = 0
camera_thread = None

# Initializing Function


def START():
    global start
    global stage
    global start_time
    global data
    start = not start

    if start:  # Start
        console_text.config(state=NORMAL)
        console_text.insert(END, '''System Initialized
>> ''')
        console_text.config(state=DISABLED)
        stage = 0
        root.title("Ground Station - Busy...")
        root.update()
        sleep(0.5)
        root.title("Ground Station")
        console_text.config(state=NORMAL)
        console_text.insert(END, '''System Calibrated
>> ''')
        console_text.config(state=DISABLED)
        root.title("Ground Station - Busy...")
        root.update()
        sleep(1)
        root.title("Ground Station")
        console_text.config(state=NORMAL)
        console_text.insert(END, '''CX on command received
>> ''')
        console_text.config(state=DISABLED)
        root.title("Ground Station - Busy...")
        root.update()
        sleep(1)
        root.title("Ground Station")
        console_text.config(state=NORMAL)
        console_text.insert(END, '''ST command received
>> ''')
        console_text.config(state=DISABLED)
        start_time = datetime.now()
        start_text.set("Abort")
        data = [start, stage, cansat_released, activate_buzzer,
                camera, start_time, altitude.get(), spd.get()]
        console_text.config(state=NORMAL)
        console_text.insert(END, f'''Date Collected: {data}
>> ''')
        console_text.config(state=DISABLED)

        save()  # This saves console information to a text file
        meter()  # Repeating Function

    else:  # Abort
        console_text.config(state=NORMAL)
        console_text.insert(END, '''Mission Aborted
>> Data Saved to SD card
>> ''')
        console_text.config(state=DISABLED)
        save()
        start_text.set("Start")
        t.cancel()

    if stage_text.get() != f"Stage {stage}":
        stage_text.set(f"Stage {stage}")


# Saves Console Information in a text file
def save():
    with open("data.txt", "w") as file:
        lines = []
        for line in console_text.get("1.0", END).split('\n'):
            lines.append(line + '\n')
        file.writelines(lines)


# Camera Function - Switchs on Camera
def camera_on():
    global camera
    global vid
    camera = True
    vid = cv2.VideoCapture(0)
    while(camera):
        ret, frame = vid.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    vid.release()
    cv2.destroyAllWindows()


# Main Repeating Function - Controls GUI's Meters
def meter():
    global stage
    global o_x
    global o_y
    global cansat_released
    global t
    global camera_thread
    global data
    global activate_buzzer
    global camera
    global vid

    try:
        t = Timer(0.1, meter)
        t.start()
        alt_value = altitude.get()
        f_x = o_x + 1

        if alt_value < 0:  # Landing Stage
            t.cancel()  # Landed
            return

        elif alt_value in range(0, 5) and (not cansat_released):  # Stage 0
            stage = 0
            if stage_text.get() != f"Stage {stage}":
                stage_text.set(f"Stage {stage}")
            
            f_y = o_y - 2

        elif alt_value in range(5, 725) and (not cansat_released):  # Stage 1
            if stage == 0:
                console_text.config(state=NORMAL)
                console_text.insert(END, '''Rocket Rising
>> ''')
                data = [start, stage, cansat_released, activate_buzzer,
                        camera, start_time, altitude.get(), spd.get()]
                console_text.config(state=NORMAL)
                console_text.insert(END, f'''Date Collected: {data}
>> ''')
                console_text.config(state=DISABLED)
                save()

            stage = 1
            if stage_text.get() != f"Stage {stage}":
                stage_text.set(f"Stage {stage}")
            
            f_y = o_y - 2

        elif alt_value > 725 and (not cansat_released):  # Stage 2
            if stage == 1:
                console_text.config(state=NORMAL)
                console_text.insert(END, f'''Cansat Released
>> ''')
                console_text.config(state=DISABLED)

            stage = 2
            if stage_text.get() != f"Stage {stage}":
                stage_text.set(f"Stage {stage}")

            cansat_released = True
            f_y = o_y + 2

        elif alt_value >= 500 and cansat_released:  # Stage 3
            stage = 3
            if stage_text.get() != f"Stage {stage}":
                stage_text.set(f"Stage {stage}")

            if alt_value < 725 and not(camera):
                console_text.config(state=NORMAL)
                console_text.insert(END, '''Camera Swithed On
>> Press q to escape Camera
>> ''')
                console_text.config(state=DISABLED)
                camera_thread = Thread(target=camera_on)
                camera_thread.start()
                data = [start, stage, cansat_released, activate_buzzer,
                        camera, start_time, altitude.get(), spd.get()]
                console_text.config(state=NORMAL)
                console_text.insert(END, f'''Date Collected: {data}
>> ''')
                console_text.config(state=DISABLED)
                save()
                
            f_y = o_y + 2

        elif alt_value >= 400 and cansat_released:  # Stage 4A
            if stage == 3:
                console_text.config(state=NORMAL)
                console_text.insert(END, f'''Payload 1 Released
>> Received PX1 command
>> PX1 command sent to Payload 1
>> Capturing the release of Payload 1
>> Capturing the descent of Payload 1
>> ''')
                console_text.config(state=DISABLED)

            stage = "4A"
            if stage_text.get() != f"Stage {stage}":
                stage_text.set("Stage " + stage)

            f_y = o_y + 2

        elif alt_value >= 5 and cansat_released:  # Stage 4B
            if stage == "4A":
                console_text.config(state=NORMAL)
                console_text.insert(END, f'''Payload 2 Released
>> Received PX2 command
>> PX1 command sent to Payload 2
>> Capturing the release of Payload 2
>> Capturing the descent of Payload 2
>> ''')
                console_text.config(state=DISABLED)

            stage = "4B"
            if stage_text.get() != f"Stage {stage}":
                stage_text.set("Stage " + stage)

            f_y = o_y + 2

        elif alt_value in range(0, 5) and cansat_released:  # Stage 5
            if stage == "4B":
                camera = False
                activate_buzzer = True
                console_text.config(state=NORMAL)
                console_text.insert(END, f'''Buzzer Activated
>> Camera Turned Off
>> CX off command received
>> Telemetry Turned off
>> Container Recovered
>> Misson Successful
>> ''')
                console_text.config(state=DISABLED)

            stage = 5
            if stage_text.get() != f"Stage {stage}":
                stage_text.set(f"Stage {stage}")

            f_y = o_y + 2

        graph_canvas.create_line(o_x, o_y, f_x, f_y)
        o_x, o_y = f_x, f_y

        altitude.set((540 - f_y)*2)
        spd.set(int(f_x / 3))

    except:  # ERROR Handling
        t.cancel()
        return


if __name__ == '__main__':
    root = Tk()  # Main Window
    root.geometry(
        f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.title("Ground Station")
    root.wm_iconbitmap("satellite-dish.ico")
    root.config(background="#f1f1f1")
    root.focus_set()  # setting focus on main window

    # Instructions
    showinfo("Before You Start", '''Read Carefully
1. This is just an ilustration
2. Altitude will increase by 10 each second
3. Graph is not for scale
4. Other Data associated are randomly generated
5. You must maximize your window for best experience
6. Click start button after closing this tab by pressing ok''')

    # Designing Frame 2
    frame2 = Frame(root, bg="#ddd")
    frame2.pack(side=RIGHT, anchor=NE)
    graph_canvas = Canvas(frame2, height=550, width=500,
                          bg="#ddd", relief=FLAT)
    graph_canvas.pack(anchor=NE)

    # Creating Graph
    # Creating X-axis
    graph_canvas.create_line(60, 540, 490, 540)
    graph_canvas.create_line(490, 540, 480, 530)
    graph_canvas.create_line(490, 540, 480, 550)

    # Creating Y-axis
    graph_canvas.create_line(60, 540, 60, 10)
    graph_canvas.create_line(60, 10, 50, 20)
    graph_canvas.create_line(60, 10, 70, 20)

    # Creating Pointors on X-axis
    internal_frame1 = Frame(frame2, padx=28)
    internal_frame1.pack(side=BOTTOM, anchor=SE, fill=X)
    Label(internal_frame1, text="Stages", bg="#ddd",
          font="Lucida 12").pack(side=BOTTOM, pady=5)
    Label(internal_frame1, text="0").pack(side=LEFT, padx=30)
    Label(internal_frame1, text="1").pack(side=LEFT, padx=30)
    Label(internal_frame1, text="2").pack(side=LEFT, padx=30)
    Label(internal_frame1, text="3").pack(side=LEFT, padx=30)
    Label(internal_frame1, text="4").pack(side=LEFT, padx=30)
    Label(internal_frame1, text="5").pack(side=LEFT, padx=30)

    # Creating Pointors on Y-axis
    internal_frame2 = Frame(frame2)
    internal_frame2.place(anchor=NW, height=600)
    Label(internal_frame2, text="Height",
          font="Lucida 12", bg="#ddd").pack(pady=15)
    Label(internal_frame2, text="750m").pack(pady=5)
    Label(internal_frame2, text="700m").pack(pady=5)
    Label(internal_frame2, text="650m").pack(pady=5)
    Label(internal_frame2, text="600m").pack(pady=5)
    Label(internal_frame2, text="550m").pack(pady=5)
    Label(internal_frame2, text="500m").pack(pady=5)
    Label(internal_frame2, text="450m").pack(pady=5)
    Label(internal_frame2, text="400m").pack(pady=5)
    Label(internal_frame2, text="350m").pack(pady=5)
    Label(internal_frame2, text="300m").pack(pady=5)
    Label(internal_frame2, text="250m").pack(pady=5)
    Label(internal_frame2, text="200m").pack(pady=5)
    Label(internal_frame2, text="150m").pack(pady=5)
    Label(internal_frame2, text="100m").pack(pady=5)
    Label(internal_frame2, text="50m").pack(pady=5)

    # Creating Meters
    frame1 = Frame(root, bg="white", height=500, padx=50, pady=100)
    frame1.pack(anchor=NW, fill=X)

    # Creating Altimeter
    internal_frame3 = Frame(frame1, bg="white")
    internal_frame3.pack(side=LEFT, padx=100)
    altitude = IntVar()
    altimeter_reading = Label(
        internal_frame3, textvariable=altitude, font="crash 40", fg="#0099ff", bg="white")
    altimeter_reading.pack()
    Label(internal_frame3, text="meters", fg="#aaa1a1",
          bg="white", pady=6, font="crash 15").pack(side=BOTTOM)

    # Creating Speedometer
    internal_frame4 = Frame(frame1, bg="white")
    internal_frame4.pack(side=LEFT, padx=100)
    spd = IntVar()
    speedometer_reading = Label(
        internal_frame4, textvariable=spd, font="crash 40", fg="red", bg="white")
    speedometer_reading.pack()
    Label(internal_frame4, text="miles per second", fg="#aaa1a1",
          bg="white", pady=6, font="crash 15").pack(side=BOTTOM)

    # Designing Frame 3
    frame3 = Frame(root, bg="white", padx=150)
    frame3.pack(fill=X)

    # Creating Stage Meter
    stage_text = StringVar()
    Label(frame3, textvariable=stage_text, font="crash 20",
          fg="green", bg="white").pack(side=LEFT, padx=70)

    # Creating Start Button
    start_text = StringVar()
    start_text.set("Start")
    Button(frame3, textvariable=start_text, bg="red", fg="white", font="Lucida 20",
           padx=10, pady=10, cursor="hand2", command=START).pack(side=LEFT, padx=70)

    # Creating Indicator
    console_text = Text(root, borderwidth=1, relief=SUNKEN,
                        font="Lucida 16 bold", padx=20, pady=20, bg="#7a8870")
    console_text.pack(side=BOTTOM, fill=BOTH)
    console_text.insert(END, ">> ")
    console_text.config(state=DISABLED)

    root.mainloop()
