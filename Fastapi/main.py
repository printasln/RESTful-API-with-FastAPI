from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Define the Pydantic model for an Observation
class Observation(BaseModel):
    id : int
    radius: int
    rssivalue: float
    lqivalue: float
    throughput: float

# Setup function to create the database and the observations table
def setup_database():
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,      
                radius INTEGER,
                rssivalue REAL,
                lqivalue REAL,
                throughput REAL
            )
        ''')
        
        # Check if there are any rows in the table
        cursor.execute("SELECT COUNT(*) FROM observations")
        row_count = cursor.fetchone()[0]
        
        # If table is empty, insert initial data
        if row_count == 0:
            data = [
                (0, -89.819, 100.722, 19922.9),
                (15, -91.5, 96.9965, 18479),
                (30, -93.1461, 91.743, 15394.9),
                (45, -93.5081, 89.2994, 14295.9),
                (60, -94.6927, 80.0528, 6612.38),
                (75, -94.9086, 79.1629, 6570.35),
                (240, -95.2276, 75.4519, 6810.52),
                (255, -93.691, 84.8017, 12266.3),
                (270, -91.7551, 95.2111, 16964.6),
                (285, -89.7337, 100.748, 20048.8),
                (300, -88.3193, 102.913, 20707.7),
                (315, -87.1499, 103.951, 20898.9),
                (330, -87.9427, 103.427, 20708.6),
                (345, -87.9416, 103.49, 20408.7)
            ]
            cursor.executemany("INSERT INTO observations (radius, rssivalue, lqivalue, throughput) VALUES (?, ?, ?, ?)", data)
            conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


# Initialize the database and table
setup_database()

# GET: Retrieve all observations
@app.get("/observations/")
async def read_observations():
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM observations")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to fetch observations")

# POST: Add a new observation
@app.post("/observations/")
async def create_observation(observation: Observation):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO observations (radius, rssivalue, lqivalue, throughput) VALUES (?, ?, ?, ?)",
                       (observation.radius,observation.rssivalue, observation.lqivalue, observation.throughput))
        conn.commit()
        conn.close()
        return {"message": "Observation added successfully"}
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to create observation")

# PUT: Update an existing observation by ID
@app.put("/observations/{observation_id}")
async def update_observation(observation_id: int, observation: Observation):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE observations SET radius = ?,rssivalue = ?, lqivalue = ?, throughput = ? WHERE id = ?",
                       (observation.radius, observation.rssivalue, observation.lqivalue, observation.throughput, observation_id))
        conn.commit()
        conn.close()
        return {"id": observation_id, **observation.dict()}
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to update observation")

# DELETE: Remove an observation by ID
@app.delete("/observations/{observation_id}")
async def delete_observation(observation_id: int):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM observations WHERE id = ?", (observation_id,))
        conn.commit()
        conn.close()
        return {"message": "Observation deleted"}
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to delete observation")
