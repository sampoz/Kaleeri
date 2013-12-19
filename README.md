group-36-2013
=============

##Project plan
####Topic: Picture gallery
####Group members: Anssi Matti Helin, Sampsa Laapotti, Osmo Maksimainen
####Deadline: 14.2.2014 midnight
##General
Let’s start drafting the project plan in this document. I pasted the functional requirements below and the provided questions as the basis of the project plan below. Feel free to edit and improve this as you see fit when you have the time, use the IRC to consult others if you’re uncertain about something.

##Functional requirements 

* Authentication (mandatory, 100-200 points)
This should include login, logout and register to the service
By default, only owner of an album should be able to view or edit his or her albums
Use django.auth

* Basic album functionalities (mandatory, 250-500 points)
Create albums (one user can have multiple albums)
Add pages to albums and select the layout of the newly created page - a predefined set of page-layouts is enough. There should be layout options with different numbers of images/captions on the page.
Modify existing albums (add and remove pages, change images and captions)

* Public link to photo albums (max 70 points)
Owners of an albums should be able to share a public links to their albums. This can be done by copy-and-pasting the URL from the service.
These links should not require login to your service and should also be difficult to guess.
Public links should not allow editing of albums

* Share albums (max 80 points)
Allow users to easily post a public link to a photo album to Twitter, Google+, or other similar services.
Order albums (mandatory, 50-200 points)
Allow users to create orders from albums and to use our internal payment service to pay orders before accepting them. See http://payments.webcourse.niksula.hut.fi/ to find more about the payments service. Optionally order handling etc.
Integrate with an image service API (max 100 points)
Use the Flickr API or some other image service API to allow users to search images when adding images to pages.
3rd party login (max 100 points)
Allow OpenID, Gmail or Facebook login to your system. Hint: Think what information you get from third party login services and if some extra information is also needed. This is the only feature where you are supposed to use third party Django apps in your service.

* Use of Ajax (max 100 points)
Use Ajax somewhere where it is meaningful in your application. For example, to browse an album so that a whole page is not loaded when a user "flips a page". Or the user can swap images via drag and drop and the change is sent to server in the background.

In the grading of previously listed features, correctness, coding style, usability, documentation, and your own tests will all be considered. It will be possible to get full points even if not all areas are good. A tentative grade limit to pass the project (i.e. grade 1) is 800 points and 1200 points to get the best grade (i.e. 3). Because this is the second time we are using this grading scheme, the exact grade limits will be decided after all the projects have been delivered. However, points needed to pass or to get the best grader won't raise from what is mentioned here.  

##The project plan

Our authentication scheme will include login, logout, and registration to the service. By default only the owner will have the rights to view or edit his own album. The owner can then share rights to view or edit to other users or make the album public or visible to his friends.
These basic features should be easy to implement using django.auth.

###Basic album functionality
The album will consist of pages that can have an arbitrary, but reasonable, amount of images and text per page, with the page size being selectable from several presets such as A4 and A5.
The images and texts may overlap and their order of stacking will be naturally stored so the look is consistent.
Images are fetched via their URLs, and the user may choose to crop them as they wish. The whole image is fetched regardless of the crop settings, as opposed to fetching a cropped version of the image. This is done in order to use as little space as possible to store the images.

###Public links
The owners of albums will be able to share public links to their albums. The public links will not require logging in, and will not allow editing the albums. This feature will be implemented using URL hashes that are hard to guess.
    
###Share album
The albums will have share buttons for Facebook, Twitter and Google+ using their corresponding APIs.

###Order albums
Our photo album will allow users to create orders from albums and to use our internal payment service to pay the orders before accepting them. The implementation will make use of the mock payment system provided by the course.
    
###Integrate with an image service API
The service will allow users to search for images using Flickr and check out the best images from Imgur by showing them a thumbnail view of the choice of images.

###Third party login
The service will allow OAuth login using Facebook and Twitter accounts. This feature will be implemented using an external library as permitted by the course staff. One such library is for example the Django OAuth consumer -library.

###AJAX for album browsing
When browsing an album, a user’s browser will have the next pages preloaded, but will not automatically download pages until necessary.
Are there some extra features not listed in the project description what you plan to implement?

###Responsive design
We plan to create the service using responsive design, so that the service looks good also in lower resolution, such as on netbooks, older tablets and smartphones.

###Image cropping
The user will be able to crop photos freely. The cropping is done on the client side, and thus the actual source images will not be edited. The crop information will be transferred to the server, which will modify the appearance of the image. This basically means using more of the client’s bandwidth in exchange for using practically no disk space on the server.

###Presentation mode
The user has an option to include simple transition effects and background music from SoundCloud, and the presentation mode will use the fullscreen mode present in modern browsers.
We consider this as an extra feature that will be implemented if we have sufficient time.

###Photo commenting/discussion 
We will be using Disqus to implement commenting/discussion of photos.
We consider this as an extra feature that will be implemented if we have sufficient time.

###Preliminary timetable
We plan to have all of the basic required functionalities: authentication, basic album functionalities, public links, album sharing, album ordering, API integration, 3rd party login, and AJAX, implemented by Friday 15.02.2013. This leaves us with two weeks of time for testing and implementing the extra features (namely the presentation mode and commenting) described above.

* Preliminary implementation order
* Basic authentication
* Basic album functionality, AJAX
* Creation using fixed layout
* Viewing, including AJAX
* Creating and editing using a layout editor
* Image cropping functionality
* Public links and social media sharing
* Third party login
* External image service API integration
* Album ordering using the payment system API
* Presentation mode
* Photo commenting/discussion

###List of models
This list of models only includes the models that we will have to implement. In other words models for comments, third party login, etc. are excluded as they require no separate model implementation by us.

####Basic authentication
Django’s internal django.auth extended to contain relevant fields for the service, such as third-party login information etc.
Basic album functionality
####Album
Contains the album name, owner, public URL hash, an one-to-many list of Pages, their order, the background music and timing information for the presentation mode etc.
####Page
Contains the layout information of each page, and an one-to-many list of Images
####Image
Contains the image URL, cropping information and other relevant information.
####Album ordering
Order
Contains information about an order of an album

###List of views
####Front page view 
Contains a description of the service as well as the fields required for login
####Authentication
####Login view (Django’s internal)
####Register view (Django’s internal)
####Profile view
####Basic album view
The default view of an album, which includes the basic information such as the number of pictures, heading of the album, and a real life like photo album view of the pictures.
####Album editing view
The view where a user can edit an album. Includes deleting, adding, changing the position and cropping of the pictures etc.
####Album list view
The view showing the list of albums a user has access to.
####Presentation view
The presentation mode might require its own Django view.
