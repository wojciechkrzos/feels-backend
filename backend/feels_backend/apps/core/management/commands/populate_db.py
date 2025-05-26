from django.core.management.base import BaseCommand
from apps.core.models import Account, Feeling, FeelingType, Post, Comment, Chat, Message
from datetime import datetime
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for the social media app'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate database...')
        
        # Create feeling types
        feeling_types_data = [
            {'name': 'high_energy_pleasant', 'description': 'High energy, pleasant emotions'},
            {'name': 'low_energy_pleasant', 'description': 'Low energy, pleasant emotions'},
            {'name': 'high_energy_unpleasant', 'description': 'High energy, unpleasant emotions'},
            {'name': 'low_energy_unpleasant', 'description': 'Low energy, unpleasant emotions'},
        ]
        
        feeling_types = {}
        for ft_data in feeling_types_data:
            feeling_type = FeelingType(
                name=ft_data['name'],
                description=ft_data['description']
            ).save()
            feeling_types[ft_data['name']] = feeling_type
            self.stdout.write(f'Created feeling type: {ft_data["name"]}')
        
        # Create feelings
        feelings_data = [
            # High energy pleasant
            {'name': 'Excited', 'color': '#FF6B35', 'type': 'high_energy_pleasant'},
            {'name': 'Joyful', 'color': '#FFD23F', 'type': 'high_energy_pleasant'},
            {'name': 'Energetic', 'color': '#EE964B', 'type': 'high_energy_pleasant'},
            {'name': 'Enthusiastic', 'color': '#F95738', 'type': 'high_energy_pleasant'},
            
            # Low energy pleasant
            {'name': 'Content', 'color': '#4ECDC4', 'type': 'low_energy_pleasant'},
            {'name': 'Peaceful', 'color': '#45B7D1', 'type': 'low_energy_pleasant'},
            {'name': 'Grateful', 'color': '#96CEB4', 'type': 'low_energy_pleasant'},
            {'name': 'Relaxed', 'color': '#FECA57', 'type': 'low_energy_pleasant'},
            
            # High energy unpleasant
            {'name': 'Anxious', 'color': '#FF6B6B', 'type': 'high_energy_unpleasant'},
            {'name': 'Frustrated', 'color': '#EE5A24', 'type': 'high_energy_unpleasant'},
            {'name': 'Angry', 'color': '#C44569', 'type': 'high_energy_unpleasant'},
            {'name': 'Stressed', 'color': '#F8B500', 'type': 'high_energy_unpleasant'},
            
            # Low energy unpleasant
            {'name': 'Sad', 'color': '#778CA3', 'type': 'low_energy_unpleasant'},
            {'name': 'Lonely', 'color': '#A55EEA', 'type': 'low_energy_unpleasant'},
            {'name': 'Tired', 'color': '#95A5A6', 'type': 'low_energy_unpleasant'},
            {'name': 'Disappointed', 'color': '#74B9FF', 'type': 'low_energy_unpleasant'},
        ]
        
        feelings = {}
        for feeling_data in feelings_data:
            feeling = Feeling(
                name=feeling_data['name'],
                color=feeling_data['color'],
                description=f"A feeling of being {feeling_data['name'].lower()}"
            ).save()
            
            # Connect to feeling type
            feeling_type = feeling_types[feeling_data['type']]
            feeling.feeling_type.connect(feeling_type)
            
            feelings[feeling_data['name']] = feeling
            self.stdout.write(f'Created feeling: {feeling_data["name"]} ({feeling_data["color"]})')
        
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
            account = Account(
                username=acc_data['username'],
                email=acc_data['email'],
                display_name=acc_data['display_name'],
                bio=f"Sharing my emotional journey as {acc_data['display_name']}"
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
                is_public=True,
                likes_count=random.randint(0, 15),
                comments_count=random.randint(0, 5)
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
        
        # Create some comments
        all_posts = Post.nodes.all()
        comment_texts = [
            "I can really relate to this feeling!",
            "Thanks for sharing, this made my day better",
            "Sending you positive vibes! 💙",
            "I felt the same way yesterday",
            "This is so beautifully expressed",
            "Hope you feel better soon! 🌟",
            "Love your perspective on this",
            "Such an honest and heartfelt post"
        ]
        
        account_list = list(accounts.values())
        feeling_list = list(feelings.values())
        
        for post in all_posts[:5]:  # Add comments to first 5 posts
            num_comments = random.randint(1, 3)
            for _ in range(num_comments):
                comment = Comment(
                    text=random.choice(comment_texts),
                    likes_count=random.randint(0, 8)
                ).save()
                
                # Connect to random author (but not the post author)
                possible_authors = [acc for acc in account_list if acc != post.author.single()]
                comment_author = random.choice(possible_authors)
                comment.author.connect(comment_author)
                
                # Connect to post
                comment.post.connect(post)
                
                # Randomly connect to a feeling
                if random.choice([True, False]):
                    comment_feeling = random.choice(feeling_list)
                    comment.feeling.connect(comment_feeling)
        
        self.stdout.write('Created sample comments')
        
        # Create a sample chat
        chat = Chat(
            name="Feeling Support Group",
            is_group_chat=True
        ).save()
        
        # Add participants
        for account in [alice, bob, charlie]:
            chat.participants.connect(account)
        
        # Create sample messages
        messages_data = [
            {'sender': alice, 'text': 'Hey everyone! How are you all feeling today?'},
            {'sender': bob, 'text': 'Pretty good! Just got back from a run.', 'feeling': 'Energetic'},
            {'sender': charlie, 'text': 'Been better, but this group always helps me feel less alone.'},
            {'sender': alice, 'text': 'We are here for you, Charlie! 💙'},
        ]
        
        for msg_data in messages_data:
            message = Message(
                text=msg_data['text'],
                message_type='feeling' if 'feeling' in msg_data else 'text'
            ).save()
            
            message.sender.connect(msg_data['sender'])
            message.chat.connect(chat)
            
            if 'feeling' in msg_data:
                feeling = feelings[msg_data['feeling']]
                message.feeling.connect(feeling)
        
        self.stdout.write('Created sample chat and messages')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated database with:\n'
                f'- {len(feeling_types)} feeling types\n'
                f'- {len(feelings)} feelings\n'
                f'- {len(accounts)} accounts\n'
                f'- {len(posts_data)} posts\n'
                f'- Sample comments and chat messages\n'
                f'- Friend connections'
            )
        )
