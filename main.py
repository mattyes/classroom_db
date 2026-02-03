# Uses a SQLite db to store each classes open windows during each bloc.
# Blocs: 
# - 1: 8:00 - 8:50
# - 2: 8:55 - 9:45
# - 3: 9:50 - 10:40
# - 4: 10:45 - 11:35
# - 5: 11:40 - 12:30
# - 6: 12:35 - 1:25
# - 7: 1:30 - 2:20
# - 8: 2:25 - 3:15
# - 9: 3:20 - 4:10
# - 10: 4:15 - 5:05
# - 11: 5:10 - 6:00

# One table per day of the week (mon-fri)

# Room number is the primary key and linked to each day of the week (So table)

# Each class room has a 3 digit room numbeer
# Each period for each room is open or busy.

# Automatically chose the period & day based on current time & day of week.

import sqlite3
from datetime import datetime
import pandas as pd
import os

current_day = None
current_bloc = None



DB_PATH = os.path.join(os.path.dirname(__file__), "classrooms.db")

def initialize_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect (will create the DB if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Days of the week
    days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']
    
    # Create tables for each day
    for day in days:
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS classrooms_{day} (
                room_number TEXT PRIMARY KEY,
                bloc_1 TEXT,
                bloc_2 TEXT,
                bloc_3 TEXT,
                bloc_4 TEXT,
                bloc_5 TEXT,
                bloc_6 TEXT,
                bloc_7 TEXT,
                bloc_8 TEXT,
                bloc_9 TEXT,
                bloc_10 TEXT,
                bloc_11 TEXT
            )
        ''')
    
    # Info table
    c.execute('''
        CREATE TABLE IF NOT EXISTS classrooms_info (
            room_number TEXT PRIMARY KEY,
            has_printer TEXT,
            has_computer TEXT)''')
    
    conn.commit()
    conn.close()


def add_classroom(room_number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Insert a new classroom with all blocs set to 'close' for ALL days of the week
    days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']
    for day in days:
        c.execute(f'''INSERT OR IGNORE INTO classrooms_{day} (room_number, bloc_1, bloc_2, bloc_3, bloc_4, bloc_5, 
                     bloc_6, bloc_7, bloc_8, bloc_9, bloc_10, bloc_11)
                     VALUES (?, 'fermée', 'fermée', 'fermée', 'fermée', 'fermée', 
                     'fermée', 'fermée', 'fermée', 'fermée', 'fermée', 'fermée')''', (room_number,))
    c.execute('''INSERT OR IGNORE INTO classrooms_info (room_number, has_printer, has_computer)
                 VALUES (?, 'inconnu', 'inconnu')''', (room_number,))
    
    conn.commit()
    conn.close()

def update_bloc_status(room_number, day, bloc_number, status, has_printer, has_computer):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    day = day.lower()

    add_classroom(room_number)  # Ensure the classroom exists

    # Update the status of the specified bloc for the given classroom on a specific day
    c.execute(f'''UPDATE classrooms_{day} 
                  SET bloc_{bloc_number} = ? 
                  WHERE room_number = ?''', (status, room_number))
    
    if has_printer:
        c.execute('''UPDATE classrooms_info 
                     SET has_printer = ? 
                     WHERE room_number = ?''', (has_printer, room_number))
    if has_computer:
        c.execute('''UPDATE classrooms_info 
                     SET has_computer = ? 
                     WHERE room_number = ?''', (has_computer, room_number))

    conn.commit()
    conn.close()

    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()

    # Retrieve the status of all classrooms for the given bloc on a specific day
    c.execute(f'''SELECT room_number, bloc_{bloc_number} FROM classrooms_{day}''')
    rooms = c.fetchall()
    conn.close()

    rooms_open = [room for room, status in rooms if status == 'open']  
    rooms_closed = [room for room, status in rooms if status == 'close']

    return rooms_open, rooms_closed  

def get_current_day_and_bloc() -> tuple:
    # Get current day of the week in french
    current_day = datetime.now().strftime('%A').lower()
    if current_day == 'monday':
        current_day = 'lundi'
    elif current_day == 'tuesday':
        current_day = 'mardi'
    elif current_day == 'wednesday':
        current_day = 'mercredi'
    elif current_day == 'thursday':
        current_day = 'jeudi'
    elif current_day == 'friday':
        current_day = 'vendredi'
    
    # Define bloc time ranges
    bloc_times = [
        (8, 0, 8, 50),
        (8, 51, 9, 45),
        (9, 56, 10, 40),
        (10, 41, 11, 35),
        (11, 36, 12, 30),
        (12, 31, 13, 25),
        (13, 26, 14, 20),
        (14, 21, 15, 15),
        (15, 16, 16, 10),
        (16, 11, 17, 5),
        (17, 6, 18, 0)
    ]
    
    now = datetime.now()
    current_bloc = None
    
    for i, (start_hour, start_minute, end_hour, end_minute) in enumerate(bloc_times):
        start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        if start_time <= now <= end_time:
            current_bloc = i + 1
            break

    return current_day, current_bloc

def update_room_info(room_number, has_printer, has_computer):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if has_printer is not None:
        c.execute('''UPDATE classrooms_info 
                     SET has_printer = ? 
                     WHERE room_number = ?''', (has_printer, room_number))
    if has_computer is not None:
        c.execute('''UPDATE classrooms_info 
                     SET has_computer = ? 
                     WHERE room_number = ?''', (has_computer, room_number))

    conn.commit()
    conn.close()

def get_room_info(room_number) -> str: 
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT has_printer, has_computer 
                 FROM classrooms_info 
                 WHERE room_number = ?''', (room_number,))
    info = c.fetchone()
    
    conn.close()
    return info

def get_open_rooms(day, bloc_number):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    day = day.lower()

    c.execute(f'''SELECT room_number 
                  FROM classrooms_{day} 
                  WHERE bloc_{bloc_number} = 'ouverte' ''')
    rooms = c.fetchall()
    conn.close()
    open_rooms = {}
    
    for i in range(len(rooms)):
        get_room_info(rooms[i][0])
        open_rooms[rooms[i][0]] = get_room_info(rooms[i][0])
    return open_rooms

def get_open_rooms_table(day, bloc_number):
    conn = sqlite3.connect(DB_PATH)

    query = f"""
        SELECT 
            c.room_number AS Room,
            c.bloc_{bloc_number} AS Status,
            i.has_printer AS Printer,
            i.has_computer AS Computer
        FROM classrooms_{day} c
        JOIN classrooms_info i
            ON c.room_number = i.room_number
        WHERE c.bloc_{bloc_number} = 'ouverte'
        ORDER BY c.room_number
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Main function
if __name__ == "__main__":
    initialize_db()
    
    current_day, current_bloc = get_current_day_and_bloc()
    print(f"Current day: {current_day}, Current bloc: {current_bloc}")

    # Example usage
    try:
        add_classroom('102')
        update_bloc_status('102', current_day, current_bloc, 'open', '', '')
        open_rooms = get_open_rooms(current_day, current_bloc)
        print("Open rooms:", open_rooms)
    except Exception as e:
        print(f"Error: {e}")