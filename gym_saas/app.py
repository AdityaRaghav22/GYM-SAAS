from gym_saas.app import create_app

app = create_app()

print(app.url_map)
print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
