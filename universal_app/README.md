# Universal Testing App

This application provides a simple webhook based API to create tests and collect responses.

## Features
* Import questions from a GIFT formatted text file
* Supports `// QuestionNumber:` tag for grouping questions into random pools
* Question types supported: single choice, multiple choice, text answer and matching
* Assign random questions to each user from every available pool
* Submit answers and get correctness feedback

## API Endpoints
* `/webhook/import` – POST JSON `{ "file": "path/to/file.gift" }`
* `/webhook/create_user` – POST JSON `{ "username": "user1" }`
* `/webhook/assign` – POST JSON `{ "user_id": 1, "count": 5 }`
* `/webhook/submit` – POST JSON `{ "user_id": 1, "answers": {assignment_id: answer} }`

Database connection parameters are taken from environment variables similar to other lessons.
