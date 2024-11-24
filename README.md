# Project Poertfolio 4 - Educonnect-sl

### Link to Deployed Site: [WAEC Prep Arena](https://educonnect-sl-5ffcb9da3e93.herokuapp.com/home/)

## Bugs

## Fixed Bugs
| **Bug** | **Identified Issues** | **Fix**|
| ------- | --------------------- | ------ |
| Users were unable to successfully log in from the signup page of the home page. Upon submitting valid credentials, users were redirected to the main home page instead of being logged in and redirected to thier designated view. | The form on the home page's signup section was incorrently pointing to the accounts.login URL instead of the correct accounts:login_view URL. This caused the log in attempt to fail and redirect users to the main login page. | Upon the form's action attrebuted in the home page template: Changed the URL from: {% url 'account:login' %} to: {% url 'account:login_view' %}. This ensures that the form correctly directs login requests to the appropiate login handler(CustomLoginView) for processing. |
| Form data disappearing after user cliked 'Edit Enteries' and returned to the school registration page. | The SchoolRegistrationForm was not initialized with the previously entered data stored in the session. The school_data stored in the session was not beign retrived during a GET request to pre-populate the form. | Updated the school_registration view to retrieve the school_dat from the session and pass it to the SchoolRegistrationForm using the initial argument. This ensures that the form fields were pre-populated with the users's previously entered data when revisiting the registration page. |
| User abale to log in after account deletion | Ther user.delete() method was not beign called due to missing parentheses (user.delete was used instead of user.delete()). As a result, the associacted UserProfile was not deleted causing RelatedObjectDoseNotExist error. | Ensured the user.delete() was called correctly to delete the account. Modified the delete_account logic to delete the UserProfile explicitly before deleting the user. Cleaned the orphaned profiles from the database to avoid related object errors. |


## Credits

* The user profile development was lernt and adapted from  [Code Schafer](https://youtu.be/CQ90L5jfldw?si=g2kEZ--_iqBuHn1B)
* Fonts: Sourced and imported from [Google Fonts](https://fonts.google.com/).
* Icons: Sourced from [Font Awesome](https://fontawesome.com/).
* JavaScript Code for Font Awesome Kit: Imported from [Font Awesome](https://fontawesome.com/).

* ChatGPT: Utilized to generate  Terms and conditions doucument, edit the content of the README document, debugging, and serve as a reference and learning guide for the project.
* Website Inspiration and Design: Based on the Love Maths Walkthrough Project fr

## Acknowledgements
I would like to express my gratitude to my mentor, Akshat Gar, and my cohort facilitator, Kay Welfare, for their invaluable guidance and support. I also appreciate the honest feedback and direction provided by my classmates.

## Statement
This project and the README document not complete and is missing some important contents



