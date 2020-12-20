# slottr-sniper
Get the signup slots you want with Slottr

![Slottr screen shot](https://github.com/euan-forrester/slottr-sniper/raw/master/images/slottr-screen-shot.png "Slottr screen shot")

During the pandemic, our building used [Slottr](https://www.slottr.com) to manage a signup list for the swimming pool and gym. It quickly turned into a competition between the residents to secure the most coveted times, with many residents camping out on the Slottr page before the new signup slots were released every day or two.

Rather than having to be chained to a computer every day competing for spots, I wrote a script to do it for me.

### Config file

To run, copy `config/config.ini.example` to `config/config.ini` and then fill in the `dev` and `prod` sections. Consider making your own signup page in Slottr and using `dev` mode to test the script first.

- `slottr-url` = URL of the Slottr page you want to sign up on
- `slottr-post-url-type` = `1` or `2`. For some reason, Slottr uses a different URL to POST to when completing the signup for some sheets. See `slottr.py` for more details

- `signup-name` = Name you want to sign up with
- `signup-email` = Email address you want to sign up with
- `signup-phone` = Phone number you want to sign up with
- `signup-condo` = For our building complex, there were 2 extra questions: the condo unit number
- `signup-building-initial` = and the code for which building you were in
- `signup-notes` = Any notes you want to include in the Notes field for your signup

- `timezone-name` = Name of the local timezone you're in
- `time-slots-added-hour` = `0`-`23`. The hour of the time that new slots are due to be added to your signup page
- `time-slots-added-minute` = `0`-`59`. The minute of the time that new slots are due to be added to your signup page
- `minutes-early-to-begin` = How many minutes before the official scheduled time that the script should start looking for slots (the person managing our building's signup was always a few minutes early)
- `minutes-later-to-end` = How many minutes after the official scheduled time that the script should abort if it could not find a slot
- `seconds-between-attempts` = How many seconds between each attempt that the script makes

- `desired-year` = The year for the slot you'd like to sign up
- `desired-month` = `1`-`12` The month for the slot you'd like to sign up
- `desired-day` = `1`-`31` The day for the slot you'd like to sign up
- `desired-hour` = `0`-`23` The hour for the slot you'd like to sign up

### Running the script

To run in `dev` mode:
```
./book-pool.py
```

To run in `prod` mode:
```
ENVIRONMENT=prod ./book-pool.py
```

### Command line arguments

- `-h`: Display help info
- `-d`: Output DEBUG level logging (default is INFO)
- `-c <path/to/file>`: Specify config file location (default is `config/config.ini`). Useful if you want to have > 1 instances running simultaneously looking for different dates if > 1 slots are due to open at the same time
