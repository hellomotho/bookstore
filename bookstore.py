# Importing necessary libraries
from easygui import *
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 
import easygui as gui
import sqlite3
import numpy as np
import json
import platform
import glob

def which_way():
    '''
    First function of program which gets executed when running the program. 
    This functions as a cross roads, either you start with a new .json database 
    file which you can import as user, or you can continue on an existing .db file.
    Login and Password gets defined in this function too and set as global variables
    
    '''
    
    global master_login
    global master_pass
    master_login = 'admin'
    master_pass = '1234'
    boolean = True
    
    msg = "Choose an option:"
    title = "Main Menu"
    choices = ["Continue on existing database","Load new database**"]
    fieldValues = choicebox(msg,title, choices)
# fieldValues variable is the user input which gets returned from the gui
    # conditional statement to guide user to the next interface based on input
    if fieldValues == "Load new database**":
        boolean = False
        login_window(boolean)
    
    elif fieldValues == "Continue on existing database":
        login_window(boolean)
def login_window(boolean):
    '''
    This function prompts the user to enter login and password, calls on
    the field_check_mpb() function to check for missing input fields and
    sets the stage to call on either login_permission(), db_permission() 
    or which_way() depending on user input.
Parameters: 
    
    boolean(bool)
    '''
    
    msg = "Enter login information"
    title = "Permission Required"
    fieldNames = ["User id","Password"]
    
    # calling on field_check_mpb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_mpb(msg, title, fieldNames)
    
    # If user input is not empty, slice list elements and save in variables
    if (fieldValues != None)and(boolean == True):
        login = fieldValues[0]
        password = fieldValues[1]
        login_permission(login, password)
    
    elif (fieldValues != None)and(boolean == False):
        login = fieldValues[0]
        password = fieldValues[1]
        db_permission(login, password)
        
    else:
        which_way()
def file_search():
    '''
    This function checks if a bookstore_db file already exists on the
    system, if so, then user can continue to user options menu. If no
    such file exists, user should be bounced back to the first window 
    and be forced to either choose to import a file or to exit. Because 
    if user gets to continue with no bookstore_db file, the program will
    yield an error once the file which does not exist get queried. 
    '''
    yes_no = ""
    # calling on platform library to determine system OS saving result in "system"
    uname = platform.uname()
    system = uname.system
    # matching 'system for similarity against "Windows" saving result in "score"
    score = fuzz.WRatio('Windows', system)
    
    if score > 70: # If OS = Windows look for '\bookstore_db' and if found set yes_no to 'yes'
        db_file = glob.glob('**\bookstore_db', recursive=True)
        if db_file == ['bookstore_db']:
            yes_no = 'yes'
    
    else: # If OS is not Windows look for 'bookstore_db' and if found set yes_no to 'yes'
        db_file = glob.glob('**/bookstore_db', recursive=True)
        if db_file == ['bookstore_db']:
            yes_no = 'yes'
    
    return yes_no
def login_permission(login, password):
    '''
    This function checks validity of login and password, as a means
    to add a layer of security so only permitted users can load a new database.
    
    Parameters: 
    
    login, password
    
    '''
        
    # Conditionals to determine if file exists, login and password entered is correct,
    # if so, restore_db() will be called, existing database file will be 
    # opened and main menu will appear, else warning & back to previous menu.
    if (file_search() == 'yes')and(login == master_login)and(password == master_pass):
        restore_db()
        
    else:
        msgbox('Incorrect login/password and/or file does not exist')
        which_way()
def db_permission(login, password):
    '''
    This function checks validity of login and password, as a means
    to add a layer of security so only permitted users can load a new database.
    
    Parameters: 
    
    login, password
    
    '''
    # Conditionals to determine if login and password entered is correct,
    # if so, load_db() will be called, new database will be opened and 
    # main menu will appear, else back to previous menu.
    if (login == master_login)and(password == master_pass):
        load_db()
        
    else:
        msgbox('Incorrect login/password')
        which_way()
def delete_permission():
    '''
    This function prompts the user to enter login and password, as a means
    to add a layer of security so only permitted users can format the database.
    
    '''
    
    msg = "Enter login information"
    title = "Permission Required"
    fieldNames = ["User id","Password"]
    
    # calling on field_check_mpb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_mpb(msg, title, fieldNames)
        
    # If user input is not empty, slice list elements and save in variables
    if fieldValues != None:
        login = fieldValues[0]
        password = fieldValues[1]
    
    # Conditionals to determine if login and password entered is correct,
    # if so, new database will be formatted and main menu will appear, else back
    # to previous menu.
    if (login == master_login)and(password == master_pass):
        delete_3()
        
    else:
        msgbox('Incorrect login/password')
def populate_db2(filename):
    '''
    If the user chooses to import new data from a .json file, this
    function dumps the contents into a new .db file and creates a table 
    named books ready for usage, granted the contents of the.json file 
    is correct.
    
    Parameters: 
    
    .json filename which user chose in the interface 
    
    '''
    
    # opening, saving and closing .json file and saving contents as data
    with open(filename, 'r+') as f:
        data = json.load(f)
    # setting db and cursor as global variables to be used troughout
    # the script without redefining every time.
    global db
    global cursor
    # Creating db file
    db = sqlite3.connect('bookstore_db')
    cursor = db.cursor()
    # Creating table named books with columns as seen below
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
        "id" INTEGER,
        "Title" TEXT,
        "Author" TEXT,
        "Qty" INTEGER)''')
    
    db.commit()
    
    # Parsing through .json file and dumping data into matching columns
    for child in data:
        cursor.execute('''INSERT OR REPLACE INTO books VALUES (?,?,?,?)''',
        (child['id'], child['Title'], child['Author'], child['Qty'],))
    db.commit()
    # Once the .db file is set, time to offer the user some options
    # which is produced in the functions below
    user_options()
def restore_db():
    '''
    If the user chooses to continue work on an existing .db file, this
    function does just that. It uses the restored .db file from the
    previous session which includes all updates made since the original 
    .json import.'
    
    '''
 
    # setting db and cursor as global variables to be used troughout
    # the script without redefining every time.
    global db
    global cursor
    # Connecting to the db file
    db = sqlite3.connect('bookstore_db')
    cursor = db.cursor()
    # Once the .db file is set, time to offer the user some options
    # which is produced in the functions below
    user_options()
def load_db():
    '''
    This funtion spawns a file-open window where the user should select 
    an appropriate .json file which will be imported into a new .db file
    The filename gets sliced from the file path in this function and it 
    then gets passed on to populate_db_2()
    '''
    
    # This variables below defines the parameters of the fileopenbox GUI
    # and the _file variable is where user input is stored
    msg = "Choose (.json) database file:"
    title = ".db_spawn"
    default = ''
    filetypes = ["*.json"]
    file_ = fileopenbox(msg,title, default, filetypes)
    
    # converting directory as string to list
    file_1 = []
    for i in file_:
        file_1.append(i)
    
    # reversing directory
    file_2 = file_1[::-1]
     
    # getting OS name and saving it in 'system' variable
    uname = platform.uname()
    system = uname.system
    
    # Initialize dash to /  ,if system OS is window, change dash to \ 
    dash = '/'
    score = fuzz.WRatio('Windows', system)
    if score > 70:
        dash = '\\' 
    
    # finding the index of the last '/' in the file directory to isolate
    # the.json file no matter its filename length
    index_ = file_2.index(dash)
    # transforming the index to negative
    index_1 = np.negative(index_)
    # Conditional statement to import the correct .json file
    
    # This conditional makes sure the right file gets imported by slicing
    # the directory after the last '/'  
    if file_ != None:
        
        global filename
        filename = file_[index_1:]
        
        #calling function to import .json data into new .db file
        populate_db2(filename)
    # else if user chooses to cancel importing process, then revert
    # back to previous menu     
    else:
        which_way()
def user_options():
    '''
    Once the user has the .db file set, this function then acts as the
    main menu, each with its own sub menus/enter fields except for the
    exit function, which terminates the process and closes the database
    This function also retrieves the meta data(column names) from the
    table and saves it as a global variable to be used in the search 
    functions.
    
    '''
    
    msg = "Choose an option:"
    title = "Menu - Book Manager"
    choices = ["Enter book", "Update book", "Delete book","Search book", "Exit"]
    fieldValues = choicebox(msg,title, choices)
    # sorting by primary key and returning all books from database
    cursor.execute('''SELECT DISTINCT * FROM books''')
    db.commit()
    # setting col_names variable as global to be used throughout the other
    # search functions. 
    global col_names 
    # Retrieving meta data from table(column names)
    col_names = [tuple[0] for tuple in cursor.description]
    # changing col_names from list to string and seperating with dashes for readability.
    col_names = '---------------'.join(col_names)
    # Setting user choice as global variable to be used in other 
    # functions as defined via user input in the main menu
    global user_choice
    user_choice = fieldValues
    main_menu()
def main_menu():
    '''
    This function consists of a loop and within it conditional statements
    which directs the user to sub menus[functions] of the main menu based on 
    user input. If the user presses cancel or exit instead of choosing one of 
    the other options the loop breaks, database will close and the window will 
    terminate. 
   
    '''
    
    while user_choice != 'Exit':
        if user_choice == 'Enter book':
            enter_book()
            user_options()
    
        elif user_choice == 'Update book':
            update_options()
            user_options()
        elif user_choice == 'Delete book':
            delete_options()
            user_options()
        elif user_choice == 'Search book':
            search_options()
            user_options()
        elif user_choice == ('Exit')or('None'):
            db.close()
        else:
            user_options()
def field_check_meb(msg, title, fieldNames):
    '''
    This function checks for missing user input values in the multienterbox
    and returns the user input as fieldValues variable
    
    Parameters:
    
    msg, title and fieldnames of the multi-enterbox GUI
    
    '''
    
    fieldValues = multenterbox(msg, title, fieldNames)
# Loop with conditionals to make sure that none of the user input 
    # fields are left blank
    while 1:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break # if no empty fields found, proceed with next codeblock
        # Saving user input as list in fieldValues variable
        fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
    
    return fieldValues
def field_check_mpb(msg, title, fieldNames):
    '''
    This function checks for missing user input values in the 
    multpassword-box and returns the user input as fieldValues variable
    
    Parameters:
    
    msg, title and fieldnames of the multpassword-box GUI
    
    '''
    
    fieldValues = multpasswordbox(msg, title, fieldNames)
# Loop with conditionals to make sure that none of the user input 
    # fields are left blank
    while 1:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break # if no empty fields found, proceed with next codeblock
        # Saving user input as list in fieldValues variable
        fieldValues = multpasswordbox(errmsg, title, fieldNames, fieldValues)
    
    return fieldValues
def enter_book():
    '''
    This function spawns a multi-enterbox interface where new book details
    can be entered which then gets added to the database.
    
    '''
    
    msg = "Enter book information:"
    title = "Enter new book"
    fieldNames = ["Book id:","Book title:","Book Author:","Book Quantity:"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
       
    # If user input is not empty, slice list elements and save in variables
    if fieldValues != None:
        id_new = fieldValues[0]
        title_new = fieldValues[1]
        author_new = fieldValues[2]
        qty_new = fieldValues[3]
            
        # Add user input(new book data) to database
        cursor.execute('''INSERT OR REPLACE INTO books(id,Title,Author,Qty) 
        VALUES(?,?,?,?)''', (id_new, title_new, author_new, qty_new))
        db.commit()
def update_options():
    '''
    Sub function of the main menu update option.
    Here we prompt the user for further input, which will determine if
    the entire book entry gets updated or if the quantity only gets updated
    
    '''
    
    msg = "Choose an option:"
    title = "Update Menu"
    choices = ["Update quantity","Update entire field"]
    fieldValues = choicebox(msg,title, choices)
# If user hits the cancel button, pass, else direct to next function
    # where user will be prompted to enter book update values.
    if fieldValues == None:
        pass
    elif fieldValues == "Update quantity":
        update_1()
    else:
        update_2()
def update_1():
    '''
    This function prompts the user to enter the book id which is to be updated 
    as well as the new book quantity, it then updates the .db file 
    accordingly. 
    
    '''
    
    msg = "Fill in the fields"
    title = "Quantity editor"
    fieldNames = ["Book id","Book Quantity"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list element and save in variable
    if fieldValues != None:
        book_id = fieldValues[0]
        qty_update = fieldValues[1]
        
        # Add user input(updated book data[quantity]) to database
        cursor.execute('''UPDATE books SET Qty =? WHERE id =?''', 
        (qty_update, book_id))
        db.commit()
def update_2():
    '''
    This function prompts the user to enter the book id which is to be updated 
    as well as the new book id, title, author and quantity, it then updates 
    the .db file accordingly. 
    
    '''
    
    msg = "Fill in the fields"
    title = "Quantity editor"
    fieldNames = ["Book id","New book id","Book Title","Book Author","Book Quantity"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list elements and save in variables
    if fieldValues != None:
        book_id = fieldValues[0]
        new_id = fieldValues[1]
        new_title = fieldValues[2]
        new_author = fieldValues[3]
        new_qty = fieldValues[4]
        
        # Add user input(updated book data) to database
        cursor.execute('''UPDATE books SET id =?,Title =?,Author =?,Qty =? 
        WHERE id =?''',(new_id, new_title, new_author, new_qty, book_id))
        #cursor.execute('''SELECT * FROM books ORDER BY id''')
        db.commit()
def delete_options():
    '''
    This functions serves as a sub menu of the main menu -> Delete book 
    option. It prompt the user via an interface with 3 options, delete
    book by id number,by author, or alterternatively the user has the option
    to format the database granted he has permission.
    
    '''
    
    msg = "Choose an option:"
    title = "Delete Menu"
    choices = ["Delete by id number","Delete all books of Author from database",
               "Format database***"]
    fieldValues = choicebox(msg,title, choices)
# Conditional statement which will call the appropriate function based
    # on user input/choice.
    if fieldValues == "Delete by id number":
        delete_1()
    elif fieldValues == "Delete all books of Author from database":
        delete_2()
    elif fieldValues == "Format database***":
        delete_permission()
def delete_1():
    '''
    This function is a sub function of the delete menu, this is where
    the removal of the database entry occurs based on user input[book id]
    
    '''
    
    msg = "What is the book id?"
    title = "Book Remover"
    fieldNames = ["Book id"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list element and save in variable
    if fieldValues != None:
        delete_id = fieldValues[0]
        
        # removing requested entry, defined by book id from database
        cursor.execute('''DELETE FROM books WHERE id =?''', (delete_id,))
        db.commit()
def delete_2():
    
    '''
    This function is a sub function of the delete menu, this is where
    the removal of the database entry occurs based on user input[book author]
    
    '''
    
    msg = "Who is the author of the book?"
    title = "Book Remover"
    fieldNames = ["Book Author"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list element and save in variable
    if fieldValues != None:
        delete_author = fieldValues[0]
        
        # removing requested entry, defined by book author from database
        cursor.execute('''DELETE FROM books WHERE Author =?''', (delete_author,))
        db.commit()
def delete_3():
    '''
    This functions formats the database if the user chooses to do so
'''
    
    cursor.execute('''DELETE FROM books''')
    db.commit()
def search_options():
    '''
    This is u sub function of the search book option from the main menu
    It prompts the user to chooce whether they would like to search a book
    by its id, title or author. Alternatively the user can choose to view
    all the books in the database or only the books which are low on stock
    
    '''
    
    msg = "Choose an option:"
    title = "Search Menu"
    choices = ["View all","Search by id number","Search by Title",
               "Search by Author","Low stock checker: { < 10 }"]
    fieldValues = choicebox(msg,title, choices)
    
    # Conditional statement which will call the appropriate function based
    # on user input/choice.
    if fieldValues == "View all":
        search_5()
    elif fieldValues == "Search by id number":
        search_1()
    elif fieldValues == "Search by Title":
        search_2()
    elif fieldValues == "Search by Author":
        search_3()
    elif fieldValues == "Low stock checker: { < 10 }":
        search_4()
def search_1():
    '''
    This function is a sub function of the search book menu, this is where
    the retrieval of the database entry occurs based on user input[book id]
    
    '''
    
    msg = "What is the book id?"
    title = "Book Search"
    fieldNames = ["Book id"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list element and save in variable
    if fieldValues != None:
        search_id = fieldValues[0]
        
        # Return database entry to user based on input[book id]
        cursor.execute('''SELECT DISTINCT id,Title,Author,Qty FROM books WHERE id =?''', 
        (search_id, ))
        # In order to display the row in an easily readable manner, we change the
        # list to a numpy array, reshape it and remove the brackets.
        books = cursor.fetchone()
        a = np.array(books, dtype = str)
        new = a.reshape(-1,4)
        new = str(new).replace('[','').replace(']','')
        new = str(new)
        # Displaying row retrieved from database in easygui textbox interface
        gui.codebox(msg='All Stock in database:',text=(col_names,'\n',new),
        title='Database')
def search_2():
    '''
    This function is a sub function of the search book menu, this is where
    the retrieval of the database entry occurs based on user input[book Title]
    
    '''
    
    msg = "What is the book Title?"
    title = "Book Search"
    fieldNames = ["Book Title"]
    
    # calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list element and save in variable
    if fieldValues != None:
        search_id2 = fieldValues[0]
    
        # Return database entry to user based on input[book Title]
        cursor.execute('''SELECT DISTINCT id,Title,Author,Qty FROM books WHERE Title =?''', 
        (search_id2, ))
        
        # Looping through database rows and saving all title matches in
        # books variable and change the list to a numpy array, reshape 
        # it and remove the brackets for readability.
        books = []
        for row in cursor:
            books += row
        a = np.array(books, dtype = str)
        new = a.reshape(-1,4)
        new = str(new).replace('[','').replace(']','')
        new = str(new)
        # Displaying row/s retrieved from database in easygui textbox interface
        gui.codebox(msg='Database Title match:',text=(col_names,'\n',new),
        title='Database')
def search_3():
    '''
    This function is a sub function of the search book menu, this is where
    the retrieval of the database entry occurs based on user input[book Author]
    
    '''
    
    msg = "Who is the Author of the book?"
    title = "Book Search"
    fieldNames = ["Book Author"]
# calling on field_check_meb() to check for missing user input and to
    # save user input as fieldValues variable
    fieldValues = field_check_meb(msg, title, fieldNames)
    
    # If user input is not empty, slice list element and save in variable
    if fieldValues != None:
        search_id3 = fieldValues[0]
    
        # Return database entry to user based on input[book Title]
        cursor.execute('''SELECT DISTINCT id,Title,Author,Qty FROM books WHERE Author =?''', 
        (search_id3, ))
        
        # Looping through database rows and saving all author matches in
        # books variable and change the list to a numpy array, reshape 
        # it and remove the brackets for readability.
        books = []
        for row in cursor:
            books += row
        a = np.array(books, dtype = str)
        new = a.reshape(-1,4)
        new = str(new).replace('[','').replace(']','')
        new = str(new)
        # Displaying row/s retrieved from database in easygui textbox interface
        gui.codebox(msg='Database Author Match:',text=(col_names,'\n',new),
        title='Database')
def search_4():
    '''
    This functions checks the database for any books that has a stock/quantity
    level of less than 10 and displays it to the user.
    
    ''' 
    
    # low_mark variable is the Quantity to be checked for against database quantities    
    low_mark = 10
    # Return database entry/s to user based on low_mark
    cursor.execute('''SELECT DISTINCT id,Title,Author,Qty FROM books WHERE Qty <?''', 
    (low_mark, ))
    # loop through database entries and and return all rows where quantity is <10
    low_stock = []                            
    for row in cursor:
        low_stock += row
    
    # change the list to a numpy array, reshape it and remove the brackets for readability.
    a = np.array(low_stock, dtype = str)
    new = a.reshape(-1,4)
    new = str(new).replace('[','').replace(']','')
    new = str(new)
    # Displaying row/s retrieved from database in easygui textbox interface
    gui.codebox(msg='Low Stock in database:',text=(col_names,'\n',new),
    title='Database')
def search_5():
    '''
    This function returns all the books on the database and displays it
    to the user
    '''
    
    # sorting by primary key and returning all books from database
    cursor.execute('''SELECT DISTINCT * FROM books ORDER BY id''')
    db.commit()
   
    # loop through database entries and return all rows with unique entries
    all_stock = []
    for row in cursor:
        all_stock += row
    
    # change the list to a numpy array, reshape it and remove the brackets for readability.    
    a = np.array(all_stock, dtype = str)
    new = a.reshape(-1,4)
    new = str(new).replace('[','').replace(']','')
    # Displaying row/s retrieved from database in easygui textbox interface
    gui.codebox(msg='All Stock in database:',text=(col_names,'\n',new),
    title='Database')
if __name__ == '__main__':
    which_way()
