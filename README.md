# Kaleeri - enslave your images!

http://kaleeri.herokuapp.com

## Students:

* Anssi Matti Helin
* Sampsa Laapotti
* Osmo Maksimainen

## Features

* Authentication - 200p
* Basic album functionalities - 400p
* Public link to photo albums - 50p
* Share albums - 80p
* Order albums - 100p
* Integrate with an image service API (Flickr) - 80p
* 3rd party login - 80p
* Use of Ajax - 100p
* *Extra:* ruoska.js, a simple cropping library

The project works mostly as a single-page app based on `hashchange` events due to certain cross-browser issues in the HTML5 History API.
Images are cropped using CSS background settings, which leads to some trouble with background alignment and size when cropping. Changing
this would either require a lot of wrapper code that calculates the container size and the cropped background size etc. or preferrably
enough disk space to actually support uploading images.

## Technologies used

* Django
* HTML5
* CSS3
* handlebars.js for templates
* ruoska.js, a self-made cropping library

## Code quality

In our opinion, the quality of the code in the project is fairly good. Some files, notably `navigate.js` in the frontend and
`gallery/views.py` in the backend should be split to smaller files for future maintainability. Test coverage for the backend is a neat
100% according to PyCharm's coverage runner when excluding `manage.py`. Frontend is unfortunately not tested, partially due to the lack
of testing frameworks fitting for this project.

The sore spot of code quality is the JavaScript that governs the single-page UI. Spending a couple of hours on refactoring it would have
made for significantly neater and more maintainable code, but having already gone far past the deadline we opted to leave it as-is,
as it is not absolutely horrible.

## Who did what

* Helin: Backend, frontend, code quality, deployment, ruoska.js
* Laapotti: Backend, frontend, payment integration
* Maksimainen: Frontend, UX

## Features not implemented

* Album removal, deemed irrelevant after missing the deadline by a long shot
* Presentation mode, a leftover from the previous plan that was never realized
* Comments on photos or albums, due to time constraints

## Known bugs

* The layout does not scale perfectly well on mobile devices
* Cropping images does not work entirely intuitively due to technical constraints

## Installation

Fairly standard Django installation procedure:
* Create a virtualenv
* Install the requirements from requirements.txt
* Set up the database either by installing PostgreSQL or changing the settings
* Run with Gunicorn or other software of choice
