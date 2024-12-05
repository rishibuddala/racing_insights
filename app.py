import streamlit as st
import sqlite3  # Replace with your preferred database library

# Database connection setup
def connect_to_db():
    conn = sqlite3.connect('output_database.db')  # Replace with your database connection
    return conn

# SQL Queries
queries = {
    "Average Points by Constructor": """
        SELECT c.name AS constructor_name, 
               AVG(r.points) AS average_points
        FROM results r
        JOIN constructors c ON r.constructorId = c.constructorId
        GROUP BY c.name
        ORDER BY average_points DESC;
    """,
    "Drivers with Above Average Points": """
        SELECT d.forename, d.surname, ds.points
        FROM drivers d
        JOIN driver_standings ds ON d.driverId = ds.driverId
        WHERE ds.points > (
            SELECT AVG(points) 
            FROM driver_standings
        );
    """,
    "Top 5 Race Finishes": """
        SELECT r.name AS race_name, 
       r.date AS race_date, 
       d.forename || ' ' || d.surname AS driver_name, 
       c.name AS constructor_name, 
       rs.position AS finishing_position
FROM results rs
INNER JOIN drivers d ON rs.driverId = d.driverId
INNER JOIN constructors c ON rs.constructorId = c.constructorId
INNER JOIN races r ON rs.raceId = r.raceId  
WHERE CAST(rs.position AS INT) <= 5
ORDER BY r.date, rs.position;
    """,
    "2023 Top Winning Driver": """
        SELECT d.forename || ' ' || d.surname AS driver_name, 
       COUNT(rs.position) AS total_wins
FROM results rs
JOIN drivers d ON rs.driverId = d.driverId
JOIN races r ON rs.raceId = r.raceId
WHERE rs.position = 1 AND r.year = 2023
GROUP BY d.driverId, d.forename, d.surname
ORDER BY total_wins DESC
LIMIT 1;
    """,
    "Average Lap Time for Race 5": """
        SELECT d.forename || ' ' || d.surname AS driver_name, 
       AVG(lt.milliseconds) AS avg_lap_time
FROM lap_times lt
JOIN drivers d ON lt.driverId = d.driverId
JOIN races r ON lt.raceId = r.raceId
WHERE r.raceId = 5
GROUP BY d.driverId, d.forename, d.surname
ORDER BY avg_lap_time ASC;

    """
}

# Streamlit App
st.title("Formula 1 Racing Insights")

# Dropdown for query selection
query_name = st.selectbox("Select a query to execute:", list(queries.keys()))

if st.button("Execute Query"):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        selected_query = queries[query_name]
        cursor.execute(selected_query)
        
        # Fetch results
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        if results:
            # Display results in a table
            st.write(f"Results for: {query_name}")
            st.table([dict(zip(column_names, row)) for row in results])
        else:
            st.success("Query executed successfully, but no results to display.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        conn.close()

