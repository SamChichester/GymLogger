# Gym Logger Project

## Table of Contents
- [Description](#description)
- [Technologies Used](#technologies-used)
- [Demo & Features](#demo--features)
- [Reflection](#reflection)
- [Contact](#contact)
- [License](#license)


## Description
I came up with the idea for this project at the gym;
I wanted a way to log how much weight I was lifting on each exercise, to track
my progression over time. \
\
I originally created this project as a solution to that problem, and eventually
I decided to add a social media component as well.

## Technologies Used
- **Languages:** Python
- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Flask
- **Database:** SQLite

## Demo & Features
### Demo
[![Project Demo](https://img.youtube.com/vi/NWkKS9CEC-I/0.jpg)](https://www.youtube.com/watch?v=NWkKS9CEC-I)
### Features
- [User Authentication System](#user-authentication-system)
- [Weight Logging](#weight-logging)
- [Exercise Editing](#exercise-editing)
- [Preferences Menu](#preferences-menu)
- [Friend Code System](#friend-code-system)
- [Activity Feed](#activity-feed)

#### User Authentication System
Users can be registered and logged in/out via a flask_login authentication system.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722555617/Screenshot_13_y6hppg.png)
#### Weight Logging
Users can create exercises on their profile with an initial weight and rep count.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722556022/Screenshot_17_octc5g.png)
#### Exercise Editing
Users can edit exercise names, add new weight/rep counts, and update previous weight/rep counts.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722555980/Screenshot_16_rhrtyj.png)
New weight/rep counts are displayed as a progression on the user's profile.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722566942/Screenshot_21_ag0wwa.png)
#### Preferences Menu
Users can adjust preferences including desired weight unit, date format, and profile privacy.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722556136/Screenshot_18_z2iynq.png)
#### Friend Code System
Users are assigned a friend code upon creating an account. Inputting a valid code in the add friend menu will create a 
friend request to the user with that friend code. Users can accept and deny friend requests, and two users that are 
friends can unfriend each other via their profile.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722556245/Screenshot_19_pcy8wn.png)
#### Activity Feed
The home page of a logged user will show an activity feed of their own recently logged progressions and their friends'
recently logged progressions.
![Project Screenshot](https://res.cloudinary.com/dvsvlcbec/image/upload/v1722566025/Screenshot_20_kjc611.png)

## Reflection
### What did I learn?
- Flask and its many extensions
- Bootstrap

### What were some challenges?
This was one of my first experiences building my own web app, so figuring out all of the intricacies for the first time
was definitely a challenge.

### How would I take this project further?
Adding more gym-related features, notably a workout timer, calorie counter, etc.

## Contact
LinkedIn - [Sam Chichester](https://www.linkedin.com/in/sam-chichester-48367123b/)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
