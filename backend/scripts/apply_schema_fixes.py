import pymysql
import sys
import configparser
import os


def read_db_config(filename='config.ini', section='Database'):
    config = configparser.ConfigParser()
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, filename)
    config.read(path)
    return {
        'host': config.get(section, 'host'),
        'port': config.get(section, 'port'),
        'user': config.get(section, 'user'),
        'password': config.get(section, 'password'),
        'database': config.get(section, 'database')
    }


def main():
    cfg = read_db_config()
    db = cfg['database']
    conn = None
    try:
        conn = pymysql.connect(host=cfg['host'], port=int(cfg['port']), user=cfg['user'], password=cfg['password'], database=cfg['database'], autocommit=True)
        cur = conn.cursor()

        # Check and add start_at column
        cur.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='event' AND COLUMN_NAME='start_at'", (db,))
        has_col = cur.fetchone()[0]
        if has_col:
            print('Column `start_at` already exists in `event`.')
        else:
            print('Adding `start_at` column to `event`...')
            cur.execute("ALTER TABLE `event` ADD COLUMN `start_at` DATETIME NULL")
            print('Added `start_at`.')

        # Check and add price column
        cur.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='event' AND COLUMN_NAME='price'", (db,))
        has_price = cur.fetchone()[0]
        if has_price:
            print('Column `price` already exists in `event`.')
        else:
            print('Adding `price` column to `event`...')
            cur.execute("ALTER TABLE `event` ADD COLUMN `price` DECIMAL(10,2) NULL")
            print('Added `price`.')

        # Check and create event_time table
        cur.execute("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME='event_time'", (db,))
        has_tbl = cur.fetchone()[0]
        if has_tbl:
            print('Table `event_time` already exists.')
        else:
            print('Creating `event_time` table...')
            create_sql = '''
            CREATE TABLE `event_time` (
              `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
              `event_id` INT NOT NULL,
              `year` INT NOT NULL,
              `month` INT NOT NULL,
              `day` INT NOT NULL,
              `hour` INT NOT NULL,
              `minute` INT NOT NULL,
              `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
              CONSTRAINT `fk_event_time_event` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            '''
            cur.execute(create_sql)
            print('Created `event_time`.')

        cur.close()
    except Exception as e:
        print('ERROR:', e)
        sys.exit(2)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
