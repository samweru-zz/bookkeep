Django Bookkeep
===

This is a bookkeeping project for inventory and retail systems that demonstarted 
double-entry bookkeeping. It is created in django python.


# Install
```python
pip install -r requirements.txt
```

# Setup
```
python manage.py makemigrations
python manage.py migrate
./bin/fixture.sh
```

# Usage
```
python book.py
Usage: book.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  cat:filter
  cat:last
  cat:new
  entry:last
  lpo:add       Add a number of units of a categorized item to a local...
  sch:last
  sch:new
  sch:push
  stock:filter
  stock:last
  trx:last
```

### LICENSE

MIT
