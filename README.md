# flask-movie-website
This website is my own personal project, a bit of a passion project really! It took more time just to get the Linux environment set up from scratch on Arch Linux (without archinstall btw!) . Compiled most of the packages from source code. The website can search for movies using the OMDB API (although that's limited to 500 requests per day). There's just one problem[there are others too but...] - it can't seem to grab the total runtime for TV shows. Here's the important part: There are no backups for any data entered on the site, and it's not encrypted either. That means any information you provide could be lost and isn't exactly secure. So, avoid using any sensitive details when logging in or registering altogether. Since I built the server myself using Arch Linux, there might be some technical quirks for people who aren't familiar with the system. To be honest, this is more of a learning project for me than a fully-fledged application. Sure, it can search for movies, but the lack of TV show runtime, missing backups, and unencrypted storage make it unsuitable for serious movie tracking or storing any sensitive information. Maybe someday it'll be there, but for now, it's a fun project ! For development, I used a combination of Python and a web framework called Flask. The front-end is built with familiar tools like HTML5, CSS3, some bash prompts for zsh shell, with port forwarding.

Setting Up MySQL-Database:
'''
CREATE DATABASE flask_app; 
USE flask_app; 
CREATE TABLE user_info (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(255) UNIQUE,
password VARCHAR(255),
email VARCHAR(255),
user_id INT
); 
'''


