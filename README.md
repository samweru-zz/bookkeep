Django Bookkeep (Inventory & Merchandising)
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
  db:all          Seed database with sample transactions
  db:base         Seed database without sample transactions
  period:actvt    Activate a different period
  period:create   Define period start and end date.
  purchase:order  Seed database with sample purchase order transactions
  sales:order     Seed database with sample sales order transactions
```

## Tests

```
python runtests.py
```

# Usage

```
python book.py
```

## Explanation

This concept works by interfacing sales and purchase transaction of inventory and retail 
to bookkeeping functionality. This accounting methodology utilizes perpetual approach 
as opposed to periodic approach of inventory.

It is implemented by scheduling transactions before submitting them to accounting. 
Transactions are scheduled pending until the user is satisfied to push `sch:push` 
them to accounting. Prior to this push, one must create a schedule `sch:new` in 
which one may add items they hope to purchase via `lpo:add` or items that are being sold 
`sale:add` commands.

Once preferred scheduled transaction is pushed, the transaction can be viewed via `trx:last`
command and details of bookkeeping can be viewed via the `entry:last` command. To record payments
for purchases command `lpo:pay` and to record sales receipts command `sale:rec` are used. In order 
to fulfill a sales return one has to use `sale:ret` command to undo order by number of units then
push the resulting schedule `sch:push` into transactions. Transaction details command are viewable
via `trx:id` which is conviniently applicable.

### Note

It is **important** to note that a period must be defined first `period:create` via the `seed.py`
utility. Defining a new period will deactivate any perious periods and those transaction will
no longer be visible. It is **important** to also finalize all transactions, orders and schedules before closing a period.

```
Usage: book.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  cat:filter    Catalogue filter items
  cat:last      View X number of last catalogues
  cat:new       Create new catalogue item
  entry:last    View X number of last transaction entries
  entry:rev     Reverse a transaction entry
  lpo:add       Add a number of units of a categorized item to a local...
  lpo:pay       Make payment for purchase order
  order:filter  Filter ordered items either by trx_no (transaction number)...
  order:last    View X number of last order items
  order:rev     Revert order only by schedule
  period:last   Last period should be the active period otherwise someone...
  sale:add      Add to sales order.
  sale:disc     Apply sales discount
  sale:rec      Receive payment for sales order
  sale:ret      Sales return units per order
  sch:last      View X number of last schedules
  sch:new       Create new schedule
  sch:push      Push schedule into transaction
  stock:filter  Filter stock items
  stock:last    View X number of stock items
  trx:id        Find transaction by ID or TRXNO.
  trx:last      View X number of last transactions
```

## Contribution

This project purposely leaves out the implementation of the accounting formula 
**Asset = Liabilities + Capital** and **Income = Revenue - Expenses** because it is mainly a proof of concept, it builds up and leaves off just exactly below that threshold. 
This area is where you generate financial statements and summaries. Please feel free to fork 
and implement this tiny remaining area.

### LICENSE

MIT