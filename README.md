Django Bookkeep (Inventory)
===

This is a bookkeeping (proof-of-concept) project for inventory and retail systems that demonstarted 
double-entry bookkeeping. It is created in django python sqlite3 and works on commandline only.


# Install
```
pip install -r requirements.txt
```

# Setup
```
python manage.py makemigrations
python manage.py migrate
```

## Seeder

You'll be required to seed the database with a period, use command `period:create` without arguments
to create a default period or define one. You can use the command `db:base` to seed the database
without transactions or command `db:all` to seed with ready transactions.

```
Usage: seed.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  db:all
  db:base
  period:create   Define period start and end date.
  purchase:order
  sales:order
```

# Tests
```
python runtests.py
```

# Usage
```
Usage: book.py [OPTIONS] COMMAND [ARGS]...                                        
                                                                                  
Options:                                                                          
  --help  Show this message and exit.                                             
                                                                                  
Commands:                                                                         
  cat:filter                                                                      
  cat:last                                                                        
  cat:new                                                                         
  entry:last                                                                      
  entry:rev     Reverse a transaction entry                                       
  lpo:add       Add a number of units of a categorized item to a local...         
  lpo:pay                                                                         
  order:last                                                                      
  period:last   Last period should be the active period otherwise someone...      
  sale:add      Add to sales order.                                               
  sale:disc     Apply sales discount                                              
  sale:rec                                                                        
  sch:last                                                                        
  sch:new                                                                         
  sch:push                                                                        
  stock:filter                                                                    
  stock:last                                                                      
  trx:last                                                                                           
```

## Contribution

This project purposely leaves out the implementation of the accounting formula 
**Asset = Liabilities + Capital** and **Income = Revenue - Expenses** because it is mainly a proof of concept, it builds up and leaves off just exactly below that threshold. 
This area is where you generate financial statements and summaries. Please feel free to fork 
and implement this tiny remaining area.

### LICENSE

MIT