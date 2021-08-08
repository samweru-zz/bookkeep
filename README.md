Django Bookkeep (Inventory)
===

This is a bookkeeping (proof-of-concept) project for inventory and retail systems that demonstarted 
double-entry bookkeeping. It is created in django python sqlite3 and works on commandline only.


# Install
```python
pip install -r requirements.txt
```

# Setup
```
python manage.py makemigrations
python manage.py migrate
```

#DB Seeder
```
python seeder.py seed:all
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
  order:last                                                                
  sale:add      Add to sales order                                          
  sale:disc     Apply sales discount                                        
  sch:last                                                                  
  sch:new                                                                   
  sch:push                                                                  
  stock:filter                                                              
  stock:last                                                                
  trx:last                                                                  
```

### LICENSE

MIT