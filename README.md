# Limit-ordering-strategy
Create and maintain base level trade and order books on the limit ordering strategy



****** Basic Order and Trade Book ******

A book to keep record of the limit orders (exchanges based on price).

__________________________
Components :

--> Label :: A label is an entity within which units can be bought/sold.
             
--> Order :: There can be two types of orders,
		1. Buy order
	A buy order is from a buyer specifying the maxmium bid price and the quantity wanting to be purchased
		2. Sell order
	A sell order is from a seller specifying the minimum selling price and the quantity wanting to sell

__________________________
Description :

++ A user can create any number of labels with unique names each associated with an outstanding buying queue, selling queue and a trade book.
++ A trade is executed when the respective price constraint is satisfied. 

__________________________
Working :

++ The user is presented with options to create/load/view labels.

++ After having a label to work with, the user can view the buying/selling queues, the trade book, or add orders to the label.

++ For each new buy order if the existing seller price is less/equal to the buying order price, record a trade between the parties and update the trade book, else add this order to the buying queue

++ For each new sell order if the existing buyer price is greater/equal to the seller order price, record a trade between the parties and update the trade book, else add this order to the selling queue		

__________________________
Notes :

++ Buying and selling queues are sorted based on prices.
++ Current implementation does not support inter-label trades.

