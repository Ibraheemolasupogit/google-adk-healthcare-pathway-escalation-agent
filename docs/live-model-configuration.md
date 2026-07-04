# Live Model Configuration

Milestone 3 supports a live Gemini configuration path through environment variables only:

- `GOOGLE_API_KEY`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_GENAI_USE_VERTEXAI`
- `GOOGLE_GENAI_MODEL`

The default configured model name is `gemini-2.5-flash`. Users may override it with `GOOGLE_GENAI_MODEL`.

Live mode must fail safely when credentials are missing. Tests and CI use mock mode and do not require Google credentials. Do not commit `.env` files or print secret values.

This milestone does not claim that live Gemini execution has succeeded unless run in an appropriately configured environment.
