import random
import benguin

benguin.benguin()

running = True
messages = 3
print('Hi! I\'m Benguin the Penguin, tell me something about your day!')
user_input = input('You: ')
while running:
    x = random.randint(1, 100)
    if x <= 10:
        print('Benguin: Please explain further.')
    elif x <= 20:
        print(f'Benguin: Why do you say "{user_input}"?')
    elif x <= 30:
        print('Benguin: That\'s interesting. Tell me more.')
    elif x <= 50:
        print(f'Benguin: I\'m not sure I understand what you mean by "{user_input}".')
    elif x <= 70:
        print('Benguin: Can you provide more context?')
    else:
        print('Benguin: What else can you share?')

    messages += 2
    user_input = input('You: ')
    if 'goodbye' in user_input.lower():
        print('Benguin: Goodbye, I enjoyed our conversation.')
        running = False
        print(f'\n\033[32mThis conversation was {messages} messages long.\033[0m')