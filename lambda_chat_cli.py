# lambda_chat_cli.py
import requests
import getpass
import argparse
import os

class LambdaChatClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.login()

    def login(self):
        try:
            response = self.session.post('https://lambda.chat/login/google-password', json={
                'email': self.email,
                'password': self.password,
            })
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Login failed: {e}')
            exit(1)

    def send_message(self, chat_id, message):
        try:
            response = self.session.post(f'https://lambda.chat/chats/{chat_id}/messages', json={
                'message': message,
            })
            response.raise_for_status()
            print('Message sent successfully')
        except requests.exceptions.RequestException as e:
            print(f'Failed to send message: {e}')

    def get_chats(self):
        try:
            response = self.session.get('https://lambda.chat/chats')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to retrieve chats: {e}')
            return []

    def get_messages(self, chat_id):
        try:
            response = self.session.get(f'https://lambda.chat/chats/{chat_id}/messages')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Failed to retrieve messages: {e}')
            return []

    def create_chat(self, name):
        try:
            response = self.session.post('https://lambda.chat/chats', json={
                'name': name,
            })
            response.raise_for_status()
            return response.json()['id']
        except requests.exceptions.RequestException as e:
            print(f'Failed to create chat: {e}')

def main():
    parser = argparse.ArgumentParser(description='''
Lambda Chat CLI Client
------------------------

A command-line interface for interacting with Lambda Chat.

Usage:
    lambda_chat_cli.py [options]

Options:
    --email EMAIL         Email address (or LAMBDA_CHAT_EMAIL environment variable)
    --chat-id CHAT_ID     Chat ID (optional)

If no chat ID is provided, a list of existing chats will be displayed, and you can select one to interact with.

Examples:
    lambda_chat_cli.py --email user@example.com
    lambda_chat_cli.py --chat-id 1234567890

Environment Variables:
    LAMBDA_CHAT_EMAIL     Email address

Interactive Commands:
    /quit                 Quit the interactive chat session
''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--email', help=argparse.SUPPRESS)
    parser.add_argument('--chat-id', help=argparse.SUPPRESS)
    args = parser.parse_args()

    email = args.email or os.environ.get('LAMBDA_CHAT_EMAIL')
    if not email:
        email = input('Enter your email address: ')

    password = getpass.getpass('Enter your Google password: ')

    client = LambdaChatClient(email, password)

    if not args.chat_id:
        chats = client.get_chats()
        print('Select a chat:')
        print('1. Create a new chat')
        for i, chat in enumerate(chats, start=2):
            print(f'{i}. {chat["name"]} ({chat["id"]})')
        while True:
            try:
                choice = int(input('> '))
                if choice == 1:
                    name = input('Enter a name for the new chat: ')
                    chat_id = client.create_chat(name)
                    break
                elif 2 <= choice <= len(chats) + 1:
                    chat_id = chats[choice - 2]['id']
                    break
                else:
                    print('Invalid choice. Please try again.')
            except ValueError:
                print('Invalid input. Please try again.')
    else:
        chat_id = args.chat_id

    print(f'Starting interactive chat session in chat {chat_id}...')
    while True:
        message = input('> ')
        if message.lower() == '/quit':
            break
        client.send_message(chat_id, message)
        messages = client.get_messages(chat_id)
        for msg in messages[-5:]:
            print(f'{msg["from"]}: {msg["message"]}')

if __name__ == '__main__':
    main()
