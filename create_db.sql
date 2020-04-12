

APP_ENV=Production
DEBUG=False
DB_HOSTNAME=t89yihg12rw77y6f.cbetxkdyhwsb.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USERNAME=t9t0fvdvw74wah2e
DB_PASSWORD=mgbuzfe465n5zf6w
DB_DIALECT=mysql
DB_DRIVER=pymysql
DB_DATABASE=l9m8k1idv0asur92

CREATE TABLE categories (
  new_category varchar(40) DEFAULT NULL,
  subcategory varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1


CREATE TABLE expenses (
  expense_id int(11) NOT NULL AUTO_INCREMENT,
  transaction_date date DEFAULT NULL,
  expense_amt int(11) DEFAULT NULL,
  category varchar(40) DEFAULT NULL,
  sub_category varchar(40) DEFAULT NULL,
  payment_method varchar(40) DEFAULT NULL,
  description varchar(500) DEFAULT NULL,
  PRIMARY KEY (expense_id)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1


CREATE TABLE income (
  income_id int(40) NOT NULL AUTO_INCREMENT,
  income_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  income_amt int(40) DEFAULT NULL,
  PRIMARY KEY (income_id)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
