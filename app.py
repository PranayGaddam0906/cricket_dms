import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect('cricket.db')
    c = conn.cursor()
    
    # Players table
    c.execute('''CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    role TEXT,
                    team TEXT,
                    runs INTEGER DEFAULT 0,
                    wickets INTEGER DEFAULT 0,
                    matches INTEGER DEFAULT 0
                )''')
    
    # Matches table
    c.execute('''CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team1 TEXT,
                    team2 TEXT,
                    winner TEXT,
                    venue TEXT,
                    date TEXT
                )''')
    
    conn.commit()
    conn.close()

# ---------------- PLAYER FUNCTIONS ----------------
def add_player(name, role, team):
    conn = sqlite3.connect('cricket.db')
    c = conn.cursor()
    c.execute("INSERT INTO players (name, role, team) VALUES (?,?,?)", (name, role, team))
    conn.commit()
    conn.close()

def update_player_stats(player_id, runs, wickets):
    conn = sqlite3.connect('cricket.db')
    c = conn.cursor()
    c.execute("UPDATE players SET runs = runs + ?, wickets = wickets + ?, matches = matches + 1 WHERE id = ?", 
              (runs, wickets, player_id))
    conn.commit()
    conn.close()

def view_players(team=None):
    conn = sqlite3.connect('cricket.db')
    if team:
        df = pd.read_sql_query("SELECT * FROM players WHERE team=?", conn, params=(team,))
    else:
        df = pd.read_sql_query("SELECT * FROM players", conn)
    conn.close()
    return df

# ---------------- MATCH FUNCTIONS ----------------
def add_match(team1, team2, winner, venue, date):
    conn = sqlite3.connect('cricket.db')
    c = conn.cursor()
    c.execute("INSERT INTO matches (team1, team2, winner, venue, date) VALUES (?,?,?,?,?)", 
              (team1, team2, winner, venue, date))
    conn.commit()
    conn.close()

def view_matches():
    conn = sqlite3.connect('cricket.db')
    df = pd.read_sql_query("SELECT * FROM matches", conn)
    conn.close()
    return df

# ---------------- LEADERBOARDS ----------------
def top_scorers():
    conn = sqlite3.connect('cricket.db')
    df = pd.read_sql_query("SELECT name, team, runs FROM players ORDER BY runs DESC LIMIT 5", conn)
    conn.close()
    return df

def top_wicket_takers():
    conn = sqlite3.connect('cricket.db')
    df = pd.read_sql_query("SELECT name, team, wickets FROM players ORDER BY wickets DESC LIMIT 5", conn)
    conn.close()
    return df

# ================= STREAMLIT APP =================
st.title("🏏 Cricket Database Management System")

menu = ["Add Player", "View Players", "Add Match", "View Matches", "Leaderboards", "Team Stats"]
choice = st.sidebar.selectbox("Menu", menu)

init_db()

# ---------------- ADD PLAYER ----------------
if choice == "Add Player":
    st.subheader("➕ Add New Player")
    name = st.text_input("Player Name")
    role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
    team = st.text_input("Team Name")
    if st.button("Add Player"):
        if name and team:
            add_player(name, role, team)
            st.success(f"✅ Player {name} added successfully!")
        else:
            st.warning("⚠️ Please enter both name and team.")

# ---------------- VIEW PLAYERS ----------------
elif choice == "View Players":
    st.subheader("📋 All Players")
    team_filter = st.text_input("Filter by Team (optional)")
    df = view_players(team_filter if team_filter else None)
    st.dataframe(df)

# ---------------- ADD MATCH ----------------
elif choice == "Add Match":
    st.subheader("🏆 Add Match Result")
    team1 = st.text_input("Team 1")
    team2 = st.text_input("Team 2")
    winner = st.text_input("Winner")
    venue = st.text_input("Venue")
    date = st.date_input("Match Date", datetime.today())
    
    if st.button("Add Match"):
        if team1 and team2 and winner:
            add_match(team1, team2, winner, venue, str(date))
            st.success("✅ Match added successfully!")
        else:
            st.warning("⚠️ Please fill all required fields.")

# ---------------- VIEW MATCHES ----------------
elif choice == "View Matches":
    st.subheader("📅 Match History")
    df = view_matches()
    st.dataframe(df)

# ---------------- LEADERBOARDS ----------------
elif choice == "Leaderboards":
    st.subheader("🏅 Top Performers")
    st.write("### 🔝 Top 5 Run Scorers")
    st.table(top_scorers())
    
    st.write("### 🎯 Top 5 Wicket Takers")
    st.table(top_wicket_takers())

# ---------------- TEAM STATS ----------------
elif choice == "Team Stats":
    st.subheader("📊 Team Performance")
    team = st.text_input("Enter Team Name")
    if st.button("Show Stats") and team:
        df = view_players(team)
        if not df.empty:
            st.write(f"### Players of {team}")
            st.dataframe(df)
        else:
            st.warning(f"No players found for team {team}.")
