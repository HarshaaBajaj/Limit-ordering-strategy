
## Script to create simple order and trade book
    # Two classes :  Label and Order
    # Five functions :
            # get_inputs              :: Utility function to take input
            # view_labels             :: View all existing labels
            # create_new_label        :: Create new label
            # label_operation_choices :: Present all available operational choices
            # load_existing           :: Load an existing label
##


# Basic libraries
import random as r                      # for random number generation
import pandas as pd                     # for dataframe operations
import time                             # to pause after each label operation
from datetime import datetime           # to record the time
from collections import OrderedDict     # to sort and maintain buying and selling records

# Class for Label and it's methods
class Label:
    """
      Each label will have,
        # label_name           (string)            : unique name of the label
        # min_price, max_price (int)               : minimum and maximum price allowed by the label
        # min_quant, max_quant (int)               : minimum and maximum quantity allowed by the label
        # buy, sell            (Ordered dictionary): outstanding buy and sell orders
        # trade_book           (Dataframe)         : registers the trades
    """
    def __init__(self, name, price, quantity): # assigning values and adding label to dictionary of all labels
        self.label_name = name.lower()
        [self.min_price, self.max_price] = price
        [self.min_quant, self.max_quant] = quantity
        self.buy = OrderedDict()
        self.sell = OrderedDict()
        self.trade_book = pd.DataFrame(
            columns=('Trade_ID', 'Trade_time', 'Trade_quantity', 'Trade_price', 'Buyer_ID', 'Seller_ID'))
        all_labels[name.lower()] = self

    def new_order(self):
        # Each time a label wants to record an order this function creates and processes the order
        # basic order details
        t_id = get_inputs(msg='Please enter the trader_id (non-zero positive int) or press enter for generating a random ID', min=1, max=1000)
        o_p = get_inputs(msg='Please enter the order rate (non-zero positive int) or press enter for the default rate',defa=50, min=self.min_price, max=self.max_price)
        o_q = get_inputs(msg='Please enter the order quantity (non-zero positive int) or press enter for the default quantity',defa=10, min=self.min_quant, max=self.max_quant)
        ty = get_inputs(msg='Please make a binary choice for the type of order (0:buy, 1:sell) or press enter for default buy',defa=0)

        o = Order(t_id, o_p, o_q, ty, len(self.buy) + len(self.sell))
        print 'Order created successfully\n',o.__dict__
        o.process_order(self)

    def view(self, kind): #function to view buy,sell and trade book of the label
        if len(getattr(self, kind)) == 0:
            print "Sorry! No records found\n"
        else:
            print kind, ' records\n'
            if kind == 'trade_book':
                print(self.trade_book)
            else:
                print(pd.DataFrame(map(lambda v: v.__dict__, getattr(self, kind).values())))

class Order(Label):
    """
       Each order will have,
           # trader_id   (int)   : Trader's unique ID, if not specified a random int [1,1000] is generated
           # price       (int)   : Order price, default : 50
           # order_quant (int)   : Order quantity, default : 10
           # order_type  (bool)  : 0 = buy, 1 = sell, default : 0 = buy

           # order_id    (int)   : ID assigned to order based on number of orders
           # order_time  (time)  : System timestamp when the order is received
    """

    def __init__(self, tra_id, or_p, or_q, typ, oid):
        [self.order_id, self.trader_id, self.price, self.quantity, self.type] = [oid + 1, tra_id, or_p, or_q, typ]
        self.order_time = str(datetime.now())

    def add(self, label_details):  # add order to buy / sell if trade can't be executed and sort based on price
        ty = 'buy' if self.type == 0 else 'sell'
        print 'Adding order into\n', ty
        getattr(label_details, ty)[self.order_id] = self
        temp = OrderedDict((k, v) for k, v in sorted(getattr(label_details, ty).items(), key=lambda x: x[1].price))
        setattr(label_details, ty, temp)

    def trade(self, label_details):  # execute the trade since the price constraint is met
        against = 'sell' if self.type == 0 else 'buy'
        curr = list(getattr(label_details, against).values())[0]
        print 'Initializing trade against\n', curr.__dict__
        if self.quantity == curr.quantity:  # if quantities of both parties match
            self.add_trading_event(label_details, curr) # add trade
            getattr(label_details, against).pop(curr.order_id) # update the respective dictionary
        elif self.quantity < curr.quantity:  # is required quantity is more than available
            self.add_trading_event(label_details, curr) # add trade
            curr.quantity -= self.quantity # subtract traded quantity from available quantity
            getattr(label_details, against).update({curr.order_id: curr}) #update with remaining quantity
        else:  # is required quantity is less than available
            self.add_trading_event(label_details, curr) #add trade
            self.quantity -= curr.quantity #update for remaining quantity needed
            getattr(label_details, against).pop(curr.order_id) #remove traded quantity from queue
            self.process_order(label_details) #call process_order again to check if any other order in queue can be traded

    def add_trading_event(self, label, party): #record trade in the book
        if self.type == 0:  # buy
            [trade_buyer_id, trade_seller_id,trade_price] = [self.trader_id, party.trader_id,party.price]
        else:
            [trade_buyer_id, trade_seller_id,trade_price] = [party.trader_id, self.trader_id,self.price]

        trade_id = len(label.trade_book) + 1
        trade_quantity = min(self.quantity,party.quantity)
        label.trade_book.loc[trade_id] = [trade_id, str(datetime.now()), trade_quantity,trade_price, trade_buyer_id,trade_seller_id]
        print 'Trade successful\n', label.trade_book.loc[trade_id]

    def process_order(self, label_info): #process the orders
        print 'Processing the order'
        if self.type == 0:  # buy
            if (len(label_info.sell) == 0) or (
                list(label_info.sell.values())[0].price > self.price):
                self.add(label_info)
            else:
                self.trade(label_info)  # trade only when there exists order in the sell queue with price <= current buying order price
        else:  # sell
            if (len(label_info.buy) == 0) or (list(label_info.buy.values())[0].price < self.price):
                self.add(label_info)
            else:
                self.trade(label_info) # trade only when there exists order in the buy queue with price >= current selling order price

def get_inputs(msg, defa=None, min=0, max=1):
    """
        To get input from user,
            msg  (string): Text to be prompted for input
            defa (int): default value
            min  (int): minimum acceptable value
            max  (int): maximum accepable value
    """
    while True: # repeat unless acceptable input is received from the user
        defa = r.randint(min,max) if defa==None else defa #if default is not specified, generate ranom number [min,max] (for trader_id)
        try:
            var = int(raw_input(msg) or defa) #get input
            if var not in range(min, max + 1): #if not in acceptable range
                print 'Not in range', min, max
                continue #ask for new input
            else:
                return var
        except ValueError:
            print 'Variable takes integer values only\n'
            continue

def view_labels(): #view all available labels with buy,sell and trade count
    if len(all_labels) == 0:
        print "Sorry! No labels found\n"
    else:
        print 'Labels sorted alphabetically\n'
        print(pd.DataFrame(
            map(lambda x: (x[0], len(x[1].buy), len(x[1].sell), len(x[1].trade_book)), sorted(all_labels.items())),
            columns=['Name', 'Buy_count', 'Sell_count', 'Trade_count']))

def create_new_label(): #create new label
    print 'Number of labels in the system: ', len(all_labels)
    name = raw_input('Enter name of the label')

    while (name.lower() in all_labels.keys()): #as long as label with same name exists
        print 'Label with same name exists!'
        op = get_inputs(msg="1: View existing label(s)\n2: Enter new name\n", defa=2, min=1, max=2)
        if op == 1:
            load_existing(name) #load label
            return
        else:
            name = raw_input(' Please enter the new name') #get new name

    min_p = get_inputs(msg='Please enter the minimum price limit (non-zero positive int) or press enter for the default rate',min=1, max=50)
    max_p = get_inputs(msg='Please enter the maximum price limit (non-zero positive int) or press enter for the default rate',min=min_p, max=100000)

    min_q = get_inputs(msg='Please enter the minimum quantity limit (non-zero positive int) or press enter for the default rate',min=1, max=10)
    max_q = get_inputs(msg='Please enter the maximum quantity limit (non-zero positive int) or press enter for the default rate', min=min_q, max=10000)

    l = Label(name, [min_p, max_p], [min_q, max_q])

    cre_op = get_inputs(msg="1: Continue to label operation choices\n2: Return to previous menu\n", defa=1, min=1, max=2)
    if cre_op == 1: #choices of what to do next
        label_operation_choices(l) #perform label operations
        return
    else:
        return #back to previous menu

def label_operation_choices(label): #get choice of label operation
    operation_choices = {1: label.new_order, 2: lambda: label.view('buy'), 3: lambda: label.view('sell'), 4: lambda: label.view('trade_book')}
    while True:
        lab_op = get_inputs(msg="Please make a selection of the label operation to perform\n"
                                "1: Create new order\n"
                                "2: View buyer stats \n"
                                "3: View seller stats \n"
                                "4: View trade book \n"
                                "5: Exit\n", defa=4, min=1, max=5)
        if lab_op == 5:
            return #go back to previous menu
        else:
            operation_choices[lab_op]() #perform operation
            time.sleep(6) # wait to print options again

def load_existing(n=None): #load existing label info
    if len(all_labels) == 0:
        print "Sorry! No labels recorded yet"
        return
    if n == None:
        n = raw_input('Please enter the name of the label to be loaded')
    curr = all_labels.get(n)
    if curr == None:
        print 'Label not found, please check the name and try again'
        return
    else:
        label_operation_choices(curr) #load and go to operations
        return

if __name__ == '__main__':
    all_labels = {}
    print 'Welcome!\n'
    choices = {1: create_new_label, 2: view_labels, 3: load_existing} #intial choices
    while True:
        op = get_inputs(msg="Please make a selection \n"
                   "1: Create new label \n"
                   "2: View label stats \n"
                   "3: Load Existing label \n"
                   "4: Exit \n", defa=2, min=1, max=4)
        if op == 4:
            ch = get_inputs(msg="1: Confirm exit \n"
                                 "2: Return to previous menu \n", defa=2, min=1,max=2)
            if ch == 1: #confirm before quitting
                exit()
        else:
            choices[op]() # perform respective action
