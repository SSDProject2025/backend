# Fiordispino 🌸🎮

Fiordispino is a **RESTful backend API** built with **Django** and **Django Rest Framework**, designed as a **Video Game Tracker & Backlog Manager**.

Its main goal is to allow users to manage their personal video game library, keeping track of:
- games they want to play,
- games they have completed,
- and shared metadata curated at platform level.

In short, Fiordispino aims to be a **“Goodreads for video games”**, with a strong focus on data validation and state consistency.

---

## ✨ Core Features

### 🎮 Central Catalogue (Games & Genres)
A global catalogue curated by administrators, containing:
- Title
- Description
- Genre(s)
- PEGI rating
- Release date
- Box art
- Global rating (derived from user votes)

The catalogue also provides **discovery features**, such as:
- random game extraction (`random-games`)

---

### 🕹️ Backlog Management (“Games to Play”)
Authenticated users can add games to their **Backlog** (games they plan to play).

Data integrity is strictly enforced:
- a game already marked as *completed* cannot be added to the backlog.

---

### 🏆 Played Games Diary (“Games Played”)
Users can register completed games by:
- moving them to the *Played* list,
- assigning a **mandatory personal rating (1–10)**.

This design enables (or anticipates) the calculation of a **global average rating** based on user votes.

---

### 🔄 Gameplay Workflow
The API enforces a clear and transactional game lifecycle:

- **Move to Played**  
  Atomically moves a game from the backlog to the played list, requiring a rating.

- **Move to Backlog**  
  Allows moving a completed game back to the backlog (e.g. for replay).

At no point can a game exist in both states simultaneously.

---

### 👤 Authentication & Social Features
- Full authentication system (Registration / Login via Token).
- Users can inspect other users’ libraries via username-based endpoints  
  (e.g. `owner/{username}`).

This introduces a **social component**, enabling library sharing and discovery.

---

## 🧠 Design Philosophy

Fiordispino focuses on:
- strong validation rules,
- consistent state transitions,
- clear separation between global data (catalogue) and user-specific data.

A game **cannot** be both *“to play”* and *“played”* at the same time.

---

## 🛠️ Tech Stack

- **Python**
- **Django**
- **Django Rest Framework**
- **Token-based Authentication**

---

## 🚀 Use Cases

- Personal video game backlog tracking
- Rating and reviewing completed games
- Discovering new games via a curated catalogue
- Exploring other users’ gaming libraries

---

## 📌 Summary

Fiordispino is a clean, robust REST API for managing video game libraries, combining:
- catalogue discovery,
- personal tracking,
- social inspection,
- and strict workflow consistency.

A solid backend foundation for any modern video game tracking platform.
