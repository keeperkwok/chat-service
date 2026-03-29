module.exports = {
  apps: [
    {
      name: "chat_service",
      script: ".venv/bin/uvicorn",
      args: `app.main:app --host 0.0.0.0 --port ${process.env.PORT || 8003} --workers 2`,
      interpreter: "none",
      autorestart: true,
      watch: false,
      env: {
        APP_ENV: "production",
      },
    },
  ],
};
