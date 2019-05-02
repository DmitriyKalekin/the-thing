class Config:
    MYSQL = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123123",
        "db": "space-wars",
        "autocommit": True
    }

    JOBS = {
        "sleep": 1
    }


CFG = Config