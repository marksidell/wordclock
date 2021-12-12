## Setting up the SD Card

These are the minimal steps necessary to get the Pi to the point where
you can ssh to it running headless.

1. Use the Raspberry Pi Imager (on Windows) to write the image to an
SD card.

2. Mount the SD card on your Linux laptop.

4. Enable ssh:
   ```
   touch /media/sidell/boot/ssh
   cp /s/wordclock/wpa_supplicant.conf /media/sidell/boot
   ```

3. Copy the authorized_keys file:
   ```
   mkdir /media/sidell/rootfs/home/pi/.ssh
   cp /s/wordclock/code/authorized_keys /media/sidell/rootfs/home/pi/.ssh
   chown 1000:1000 -R /media/sidell/rootfs/home/pi/.ssh
   chmod 700 /media/sidell/rootfs/home/pi/.ssh
   ```

## Installing the Baseline Software

1. Unmount the SD card, put it in the pi.

2. Find the pi's IP address from dhcp and connect:
   ```
   ssh pi@<ip>
   sudo -s
   ```

3. Enable I2C and disable the GUI console.

   1. Run `raspi-config`.
   2. Select *Interface Options*.
   3. Enable I2C.
   4. Select *System Options*
   5. Select *Boot / Auto Login*
   6. Select *Console Autologin*. Don't bother rebooting now.
   4. Save and exit.

4. Create a file to enable ssh key forwarding when root, for logging
   into github:
   ```
   visudo /etc/sudoers.d/ssh_agent_forwarding
   ```

   Add this line and save the file:
   ```
   Defaults env_keep += "SSH_AUTH_SOCK"
   ```

5. Log out and back in, to enable ssh agent forwarding.

6. Install git:
   ```
   apt-get update
   apt-get -y install git
   ```

7. Clone the repo:
   ```
   git clone git@github.com:marksidell/wordclock.git
   ```

8. Do basic setup:
   ```
   cd wordclock/code
   make setup
   make config_sshd
   ```

9. Change the pi passwd.

10. Shutdown the pi. Remove the SD card and use Win32 Disk Imager to snapshot it to `baseline.img`.

## Installing and Configuring the Software

4. Install AWS credentials: Edit `/root/.aws/credentials` and paste the credentials
   for this particular clock.

16. Install the software, where `<xx>` is the two-letter config name for this clock.
    ```
    # This step is probably not necessary
    rm /vars/wordclock/params.json

	 cd /home/pi/wordclock/code
    make CONFIG=<xx>
    ```

## Building the Clock

1. Cut back panel. 0.5 inch MDF, 16 x 16 inches.
2. Cut 2 braces. 0.5 inch MDF, 16.5 x 2 inches.
3. Using straight edge aligned with back panel corners, find center. Then use square
to draw orthognal lines through the center. These are used to align various items
attached to the panel.

4. Mill the back panel. Place it on the MDF sacrificial base with the notch that allows
it to overhang the mill's front edge. Blue-tape the panel to the base in the corners.
Use small clamps to squeeze the front corners together while the glue sets.

5. Using the corner jig, route three back panel rounded corners. Omit the lower-right
corner, viewed from the rear of the panel.

6. Mill the brackets.

7. Glue standoffs to the brackets.

7. Mill the bottom acrylic band, using the acrylic/MDF jig.

8. Cut and tin the short power cable. 10". Attach the powerpole connector.
Solder the cable to the bottom PCB.

9. Cut the three-wire PCB jumper cable. 110 mm. Solder it to the PCB.

10. Glue the top and bottom PCBs to the back panel. Use four drops of medium-vicosity superglue,
at points where there are no PCB through-holes. Secure with four small clamps.

10. Secure the three-wire jumper cable to the bottom PCB with a dab of hot glue.

10. Cut the four-wire level converter jumper cable. 155 mm. Solder it to the level converter.

11. Cut the two-wire pushbutton jumper cable. 110 mm. Solder it to the pushbutton,
with heat shrink strain relief.

12. Solder 9x2 right-angle header to the pi. Header on TOP of pi.

13. Screw 5mm/2 standoffs to the pi, and 5mm/3 standoffs to the accelerometer, and magnetometer.
    Standoffs face UP.

13. Solder a qwiic cable to the light sensor. 90 mm (Use half of a 200 qwiic cable. Save
the other half!)

14. Screw 10mm standoffs to the acrylic electronics panel.

14. Mount the pi and sensors to the acrylic plate. Hook everything up and test.
    See [Electronics Alignment](https://photos.app.goo.gl/rrW4gMBJYJBW6XC3A).

15. Calibrate the compass:
    ```
    systemctl stop wc
    rm /var/wordclock/compass.json
    calibrate
    ```

    While `calibrate` is running, rotate the electronics assembly through all orientations.

16. Cut the face neopixel strips. Lay them out in the correct up/down pattern.
and tape them to an MDF board. Leftmost
strip is *up*.

17. Tin the neopixels. Bottom: all three, top: center only. Test for shorts.

18. Tin the top and bottom PCBs.

19. Hot glue the neopixel strips to the back panel. Use the center line for alignment.

20. Solder the strips to the PCBs. Use the hold-down jig.
Check all connections for shorts and for connectivity to the strips.

21. Hook up the pi and run `tneo --all` to test the face neopixels.

22. Solder wires to the border PCB and then solder the PCB to the neopixel strip.
The PCB sits on top of the neopixels, facing down. The wires leave the *front* of the PCB.
See [Border PCB](https://photos.app.goo.gl/wNSTMZ44nTu5heG16).

23. With the back panel clamped *face up*, glue on the border neopixels. Medium viscosity.
See [Attaching border pixels](https://photos.app.goo.gl/Qw9Kop7GaBzFSAUHA).

24. Solder the border pixel wires to the bottom strip.
See [Border pixel wiring](https://photos.app.goo.gl/Ag3d7LAccuLykpyG8).

25. Hook up the electronics and test all pixels.

17. Mount the brackets. See [Mounting brackets](https://photos.app.goo.gl/3VDmyGYpLevs3Q7WA).

    1. Angle the back panel on the multifunction table so that holes
       are close enough to clamp the bracket jig.

    2. Mark a center line on the top bracket.

    3. Mark a line 101 mm from the left edge of the bottom bracket.

    4. Draw lines along the edges of the brackets and Xs at the slot
       positions to indicate where to apply glue

    5. Nail the brackets to the back panel.

18. Drill holes for the screw eyes and mount the eyes. 1/16" drill.
Use blue tape on bit to mark 7/16" depth.

19. Attach the picture wire, with heat shrink in place.

20. Shrink the heat shrink.

21. Attach felt pads.

22. Mark hole positions on the side band drilling jig.

23. Drill holes in side bands. Place blue tape on left side of each band.

21. Glue the electronics to the back panel.

24. Attach powerpole connector to the power supply, a few inches from the
supply to minimize power loss. White stripes are red/plus.

24. Attach powerpole connectors to the white power cable.

25. Mill the light sensor well:

    1. Attach the sensor well jig to the milling machine.

    2. Tape blue tape to over the sensor hole and in the corner where the mill alignment probe sits.

    3. Clamp the face to the jig.

    4. Mill the well.

25. Using a blue tape border, paint the light sensor mask. 3" wide, 1.25" from face edge.

26. hot-glue the light sensor to the face, with spots of glue on the bottom and side edges.

27. If the sensor is proud of the face, apply electrical tape to the sides.

28. Afix 3" gaffer's tape to the back panel under the picture hook wire. Use MDF
straight edge and utility knife to cut clean edges.

29. Glue the acrylic band to the face.

    1. Clamp band alignment jigs to the table, using face and under-face for alignment.
       Position the panel so that you can clamp the brackets down while cementing the
       bands. See [Band Clamping](https://photos.app.goo.gl/cj5uuTcT4vic3L4Q9).

    2. Screw side acrylic bands to back panel brackets.

    3. Use the fourth band to align the corner.

    4. Place the back panel on the face and cement the first side band.

    5. Rotate and cement the other side.

    6. Cement the top and bottom bands.
       See [Top and Bottom Clamping](https://photos.app.goo.gl/YPZUVhCXy1rSnqiJ6).

30. Attach and connect the pushbutton.

25. Cut sides for shipping case:

    - 2 23.25"
    - 3 19"
    - 8 1" for standoffs

26. Screw the case together. Bottom try area is 2".

27. Cut cardboard sides.

28. Glue and staple back to frame.

29. Attach "OPEN THIS/OTHER SIDE" labels.

30. Place the clock face down in the case, on top of a layer of bubble wrap.

31. Tape standoffs: One at the end of each bracket, and one in each corner.

32. Cover the clock with another sheet of bubble wrap.

33. Tape the cover onto the case.

34. Tape the manual envelope and ziploc bag containing a picture hook to the case cover.

35. Ship it!
