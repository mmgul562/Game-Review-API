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

- `GET /api/review/reviews/`: List all reviews
- `POST /api/review/reviews/`: Create a new review
- `GET /api/review/reviews/{id}/`: Retrieve a specific review
- `PUT /api/review/reviews/{id}/`: Update a review
- `PATCH /api/review/reviews/{id}/`: Partially update a review
- `DELETE /api/review/reviews/{id}/`: Delete a review

## Documentation

The full API documentation is available at the `/api/docs/` endpoint, which provides a Swagger UI for testing the API.

## License & Package Information

This project uses the following 3rd party libraries:
| Package                          | Version          | License                                                                 |
|----------------------------------|------------------|-------------------------------------------------------------------------|
| Django                           | >=4.0.1,<4.1     | [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause)<grok-card data-id="00a6de" data-type="citation_card"></grok-card>    |
| djangorestframework              | >=3.13.1,<3.14   | [BSD License](https://opensource.org/licenses/BSD-3-Clause)<grok-card data-id="b83df4" data-type="citation_card"></grok-card>             |
| psycopg2                         | >=2.9.3,<2.10    | [GNU Lesser General Public License (LGPL) v3 or later (with exceptions)](https://opensource.org/licenses/LGPL-3.0)<grok-card data-id="968ff0" data-type="citation_card"></grok-card> |
| drf-spectacular                  | >=0.22.1,<0.23   | [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause)<grok-card data-id="381d76" data-type="citation_card"></grok-card>    |
| flake8                           | >=4.0.1,<4.1     | [MIT License](https://opensource.org/licenses/MIT)<grok-card data-id="7c1e13" data-type="citation_card"></grok-card>                      |
