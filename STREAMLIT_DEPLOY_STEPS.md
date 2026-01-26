# Streamlit Deploy Steps (Private)

## 1) Push repo to GitHub
- Create a new GitHub repo (if you haven't already).
- Push this project to the repo.

## 2) Create the Streamlit app
- Go to Streamlit Community Cloud.
- Click “New app”.
- Choose your repo + branch.
- Main file path: `app/ui/App.py`.

## 3) Set secrets / env vars
- In Streamlit Cloud app settings, add:
  - `OPENAI_API_KEY` (required)
  - `APP_IMPL=langchain|openai|both` (optional)
  - `ALLOW_IMPL_SWITCH=1` (optional toggle)

## 4) Deploy
- Click “Deploy”.
- Wait for build to finish.

## 5) Verify
- Open the app URL.
- Try both chat + questions pages.
- If you enabled the switch, confirm it appears in the sidebar.

## Notes
- `.env` is local-only; Streamlit Cloud does not read it.
- Dependencies are from `requirements.txt`.
