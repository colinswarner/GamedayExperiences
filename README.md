# Kings Experience Marketplace
#### Video Demo:  https://www.youtube.com/watch?v=BOhwpA1moTg
#### Description:
I work for the NBA's Sacramento Kings, so for my final project I created a web portal that would allow fans to purchase and return gameday experiences for upcoming games using credit that they have on account.
This is a real problem for us at the Kings becuase a company that previously provided a similar feature went out of business due to covid. My final project may actually be able to eventually fill in a gap that we have as a business.

1. LOGIN SCREEN: Allows existing users to login using their username and password that are stored in Users table. In our case, we would have the username be equal to the fan's email on file.
Existing users would be taken to the 'Upcoming' screen to view their upcoming experiences that have already been purchased.

2. REGISTER SCREEN: For fans that have not yet logged in, they would register using their email, firstname, lastname, and password. Passwords must be at least 8 characters. Default cash value being set at $200 for newly registered users. We have fans with existing credit values that we would need to import proactively.
New users would be directly taken to the 'buy screen', since they do not have any upcoming experienes to view.

3. BUY SCREEN: Displays at the top the current credit balance of the logged in user. Using two different for loops (one for table games and one for table experiences), I've listed each of the available gameday experiences, with a dropdown to select the game and quantity the fan would like to purchase.
Description and price of the experience are listed as well. Would love to add an image of each experience below the description in order to better advertise to the fans. Once the fan submits 'Buy Now', that experience is entered into the 'transactions' table. The amount spent is deducted from their current credit balance in 'Users' table.
The user should then be redirected to the upcoming experiences screen.

4. RETURN SCREEN: This screen allows fans the opportunity to return their previously purchased experiences if they or a part of their party can no longer make the game. Simply select from the drop down of upcoming experiences, type in the quanity returned, and hit 'Return'.
The amount returned will be added back to their credit balance, and there will be a line item added to the transactions table subtracting the price and and quanity. This allows for the upcoming experiences page to display the proper quanity currently upcoming.

#### FUTURE UPDATES:
1. Implement a lookup feature that populates existing balance of a fan rather than the $200 default.
2. Display images for each of the gameday experiences. need to figure out how to save image files in the database to add to for loop.
3. Allow for purchase of experiences using credit cards rather than just credit.
4. Receive design feedback from marketing team to see if they have any input.