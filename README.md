# DRF Game Review API

This project is a Django-based REST API for game reviews, containerized with Docker and using PostgreSQL as the database backend.

## Requirements
- Docker

## Getting Started

1. Clone the repository
2. Rename `.env.example` file in the project root to `.env` and replace the values
3. Build and run the Docker containers:
```shell
docker-compose up --build
```
4. The API should now be available at `http://localhost:8000/`

## Features

- User management: Users can create accounts, update their profiles, and obtain access tokens.
- Game management: Administrators can create, read, update, and delete games.
- Game requests: Users can request new games to be added.
- Reviews: Users can create, read, update, and delete reviews for existing games.

## Available Endpoints

### Users

- `POST /api/user/create/`: Create a new user
- `GET /api/user/me/`: Retrieve the current user's profile
- `PUT /api/user/me/`: Update the current user's profile
- `PATCH /api/user/me/`: Partially update the current user's profile
- `POST /api/user/token/`: Obtain an access token

### Game Requests

- `GET /api/game/game-requests/`: List all game requests
- `POST /api/game/game-requests/`: Create a new game request
- `GET /api/game/game-requests/{id}/`: Retrieve a specific game request
- `PUT /api/game/game-requests/{id}/`: Update a game request
- `PATCH /api/game/game-requests/{id}/`: Partially update a game request
- `DELETE /api/game/game-requests/{id}/`: Delete a game request
- `POST /api/game/game-requests/{id}/approve/`: Approve a game request
- `POST /api/game/game-requests/{id}/reject/`: Reject a game request

### Games

- `GET /api/game/games/`: List all games
- `POST /api/game/games/`: Create a new game
- `GET /api/game/games/{id}/`: Retrieve a specific game
- `PUT /api/game/games/{id}/`: Update a game
- `PATCH /api/game/games/{id}/`: Partially update a game
- `DELETE /api/game/games/{id}/`: Delete a game

### Reviews

- `GET /api/review/reviews/`: List all reviews.
- `POST /api/review/reviews/`: Create a new review.
- `GET /api/review/reviews/{id}/`: Retrieve a specific review.
- `PUT /api/review/reviews/{id}/`: Update a review.
- `PATCH /api/review/reviews/{id}/`: Partially update a review.
- `DELETE /api/review/reviews/{id}/`: Delete a review.

## Documentation

The API documentation is available at the `/api/docs/` endpoint, which provides a Swagger UI for testing the API.

## License Information

This project uses the following 3rd party libraries:
- [Django REST Framework (BSD 3-Clause)](https://opensource.org/licenses/BSD-3-Clause)
- [Psycopg2 (GNU LGPL 3.0)](https://www.gnu.org/licenses/lgpl-3.0.html)
- [DRF Spectacular (BSD 3-Clause)](https://opensource.org/licenses/BSD-3-Clause)
- [Flake8 (MIT)](https://opensource.org/licenses/MIT)
