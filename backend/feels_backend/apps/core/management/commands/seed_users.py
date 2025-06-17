from django.core.management.base import BaseCommand
from apps.core.models import Account, Feeling, Post, Chat, Message
import hashlib


class Command(BaseCommand):
    help = 'Populate the database with sample users, posts, and interactions'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate users and content...')
        
        # Get existing feelings
        feelings = {feeling.name: feeling for feeling in Feeling.nodes.all()}
        if not feelings:
            self.stdout.write(
                self.style.ERROR(
                    'No feelings found in database. Please run "python manage.py seed_feelings" first.'
                )
            )
            return
        
        # Create sample accounts
        accounts_data = [
            {'username': 'alice_feels', 'email': 'alice@example.com', 'display_name': 'Alice Johnson'},
            {'username': 'bob_emotions', 'email': 'bob@example.com', 'display_name': 'Bob Smith'},
            {'username': 'charlie_mood', 'email': 'charlie@example.com', 'display_name': 'Charlie Brown'},
            {'username': 'diana_vibes', 'email': 'diana@example.com', 'display_name': 'Diana Prince'},
            {'username': 'eve_heart', 'email': 'eve@example.com', 'display_name': 'Eve Adams'},
        ]
        
        accounts = {}
        for acc_data in accounts_data:
            # Create a simple password hash for demo accounts
            password_hash = hashlib.sha256(f"password123_{acc_data['username']}".encode()).hexdigest()
            
            account = Account(
                username=acc_data['username'],
                email=acc_data['email'],
                display_name=acc_data['display_name'],
                bio=f"Sharing my emotional journey as {acc_data['display_name']}",
                password_hash=password_hash
            ).save()
            accounts[acc_data['username']] = account
            self.stdout.write(f'Created account: {acc_data["username"]}')
        
        # Create friendships
        alice = accounts['alice_feels']
        bob = accounts['bob_emotions']
        charlie = accounts['charlie_mood']
        diana = accounts['diana_vibes']
        eve = accounts['eve_heart']
        
        # Connect some friends
        alice.friends.connect(bob)
        bob.friends.connect(alice)
        alice.friends.connect(charlie)
        charlie.friends.connect(alice)
        bob.friends.connect(diana)
        diana.friends.connect(bob)
        charlie.friends.connect(eve)
        eve.friends.connect(charlie)
        
        self.stdout.write('Created friendship connections')
        
        # Create sample posts
        posts_data = [
            {'author': 'alice_feels', 'body': 'What a beautiful morning! The sun is shining and I feel so grateful for this moment.', 'feeling': 'Grateful'},
            {'author': 'bob_emotions', 'body': 'Just finished my workout and I am pumped! Ready to tackle the day ahead.', 'feeling': 'Energetic'},
            {'author': 'charlie_mood', 'body': 'Feeling a bit overwhelmed with all the work lately. Taking some deep breaths.', 'feeling': 'Stressed'},
            {'author': 'diana_vibes', 'body': 'Spent the evening reading by the fireplace. Such a peaceful way to end the day.', 'feeling': 'Peaceful'},
            {'author': 'eve_heart', 'body': 'Got some disappointing news today, but trying to stay positive and move forward.', 'feeling': 'Disappointed'},
            {'author': 'alice_feels', 'body': 'Dancing to my favorite music! Life is so wonderful when you let yourself feel the joy.', 'feeling': 'Joyful'},
            {'author': 'bob_emotions', 'body': 'Traffic was terrible and now I am running late for everything. Why does this always happen?', 'feeling': 'Frustrated'},
            {'author': 'charlie_mood', 'body': 'Meditation session was exactly what I needed. Feeling so much more centered now.', 'feeling': 'Content'},
        ]
        
        for post_data in posts_data:
            post = Post(
                body=post_data['body'],
            ).save()
            
            # Connect to author
            author = accounts[post_data['author']]
            post.author.connect(author)
            
            # Connect to feeling
            feeling = feelings[post_data['feeling']]
            post.feeling.connect(feeling)
            
            # Update author's feelings shared count
            author.feelings_shared_count += 1
            author.save()
            
            self.stdout.write(f'Created post by {post_data["author"]}: "{post_data["body"][:50]}..."')
        
        # Create a sample chat
        chat1 = Chat(
            name="Alice and bob",
            is_group_chat=False
        ).save()
        
        # Add participants
        for account in [alice, bob]:
            chat1.participants.connect(account)
        
        # Create sample messages
        messages1_data = [
            {'sender': alice, 'text': 'Hey! How are you feeling today?'},
            {'sender': bob, 'text': 'Pretty good! Just got back from a run.', 'feeling': 'Energetic'},
            {'sender': alice, 'text': 'That\'s nice! 💙'},
            {'sender': alice, 'text': 'Have a nice day!', 'feeling': 'Peaceful'}
        ]

        last_msg = None
        
        for msg_data in messages1_data:
            message = Message(
                text=msg_data['text'],
                message_type='feeling' if 'feeling' in msg_data else 'text'
            ).save()
            
            message.sender.connect(msg_data['sender'])
            message.chat.connect(chat1)
            
            if 'feeling' in msg_data:
                feeling = feelings[msg_data['feeling']]
                message.feeling.connect(feeling)

            last_msg = message

        chat1.last_message.connect(last_msg)
        
        self.stdout.write('Created sample chat and messages')

        chat2 = Chat(
            name="Alice and charlie",
            is_group_chat=False
        ).save()

        chat2.participants.connect(alice)
        chat2.participants.connect(charlie)

        message2 = Message(
            text = "Hey! Did you get home safe last night?",
            message_type = 'feeling'
        ).save()

        message2.sender.connect(charlie)
        message2.chat.connect(chat2)
        message2.feeling.connect(feelings["Anxious"])
        chat2.last_message.connect(message2)
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated database with:\n'
                f'- {len(accounts)} accounts\n'
                f'- {len(posts_data)} posts\n'
                f'- Sample comments and chat messages\n'
                f'- Friend connections'
            )
        )
