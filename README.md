# Skimbot

Skimbot is a discord bot that allows users to perform data analysis on their message history.

## Installation

- [Set up a discord bot client](https://discord.com/developers/home).
  - Make sure to enable the message_content intent in the bot section.
- Clone from source, and create a python3 environment in the project root.
  - Create a .env file in the root of the environment and insert the line "token=", then your bot's token.
  - Use pip to install all required dependencies.
- Create a logs and data directory in the project root, because I'm too lazy to do that for you.
  - Create a blank data.db file in the data directory. This is where message data collected by your client will go.

Execute from the project root,
```bash
python3 core.py
```
...or use the script files provided.
```bash
./bin/skimbot.sh
````

## Dependencies

Depends on [py-cord](https://github.com/pycord-development/pycord), [wordfreq](https://github.com/rspeer/wordfreq), [aiosqlite](https://github.com/omnilib/aiosqlite), and [dotenv](https://github.com/theskumar/python-dotenv).

## Contributing

Pull requests are welcome. For major changes, open an issue first. 

## License

[MIT](https://choosealicense.com/licenses/mit/)
